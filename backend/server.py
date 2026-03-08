from fastapi import FastAPI, APIRouter, HTTPException, Depends, BackgroundTasks, Header, Request
from fastapi.responses import StreamingResponse, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
import pyotp
import qrcode
import io
import httpx
import asyncio
import time
from monitoring_scheduler import start_scheduler, monitor_website_complete
from reports_export import generate_monitoring_report
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Settings
SECRET_KEY = os.environ.get('JWT_SECRET', 'beehive-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)

# Create the main app without a prefix
app = FastAPI(title="BeeHive - Website Manager")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Convert validation errors to user-friendly messages"""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")
    
    return JSONResponse(
        status_code=422,
        content={"detail": " | ".join(errors)}
    )

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "admin"  # admin or subadmin

class UserLogin(BaseModel):
    username: str
    password: str
    totp_code: Optional[str] = None
    remember_me: bool = False

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    role: str
    twofa_enabled: bool = False
    twofa_secret: Optional[str] = None
    permissions: Optional[Dict[str, bool]] = None
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    must_change_password: bool = False

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]
    requires_2fa: bool = False
    requires_password_change: bool = False

class WebsiteCreate(BaseModel):
    name: str
    url: str

class Website(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    url: str
    owner_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_checked: Optional[datetime] = None
    status: str = "unknown"  # online, offline, unknown

class MonitoringData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    website_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    latency: Optional[float] = None  # in milliseconds
    page_load_time: Optional[float] = None  # in milliseconds
    status_code: Optional[int] = None
    is_online: bool = False
    error_message: Optional[str] = None

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

class Enable2FA(BaseModel):
    totp_code: str

class MonitoringSettings(BaseModel):
    check_ssl: bool = True
    multi_location: bool = False
    notifications_enabled: bool = True
    monitoring_interval_minutes: int = 5
    email_notifications: bool = True
    slack_notifications: bool = False

class WeeklyStats(BaseModel):
    message: str
    total_checks: int
    avg_latency: float
    uptime_percentage: float
    improvement: str

class MonitoringSettings(BaseModel):
    check_ssl: bool = True
    multi_location: bool = False
    notifications_enabled: bool = True
    monitoring_interval_minutes: int = 5
    discord_notifications: bool = True

class NotificationSettings(BaseModel):
    discord_webhook: Optional[str] = None

class AlertThreshold(BaseModel):
    website_id: str
    max_latency: Optional[int] = None  # milliseconds
    min_uptime: Optional[float] = None  # percentage
    ssl_days_warning: int = 30  # days before expiry to alert
    enabled: bool = True

class ExportRequest(BaseModel):
    days: int = 30
    format: str = "both"  # pdf, csv, or both

# Helper Functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace('Bearer ', '')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Background monitoring task
async def monitor_website(website_id: str, url: str):
    start_time = time.time()
    monitoring_data = {
        "id": str(uuid.uuid4()),
        "website_id": website_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "is_online": False
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            latency = (time.time() - start_time) * 1000  # Convert to ms
            
            monitoring_data.update({
                "latency": round(latency, 2),
                "page_load_time": round(latency, 2),
                "status_code": response.status_code,
                "is_online": 200 <= response.status_code < 400
            })
            
            # Update website status
            await db.websites.update_one(
                {"id": website_id},
                {"$set": {
                    "status": "online" if monitoring_data["is_online"] else "offline",
                    "last_checked": monitoring_data["timestamp"]
                }}
            )
    except Exception as e:
        monitoring_data["error_message"] = str(e)
        await db.websites.update_one(
            {"id": website_id},
            {"$set": {"status": "offline", "last_checked": monitoring_data["timestamp"]}}
        )
    
    await db.monitoring_data.insert_one(monitoring_data)

# Auth Routes
@api_router.post("/auth/register", response_model=User)
@limiter.limit("10/hour")
async def register(request: Request, user_data: UserCreate, current_user: dict = Depends(get_current_user)):
    # Only admins can create new users
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create users")
    
    # Check if username exists
    existing = await db.users.find_one({"username": user_data.username}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create user
    user = User(
        username=user_data.username,
        email=user_data.email,
        role=user_data.role,
        created_by=current_user["id"]
    )
    
    user_dict = user.model_dump()
    user_dict["password_hash"] = hash_password(user_data.password)
    user_dict["created_at"] = user_dict["created_at"].isoformat()
    
    await db.users.insert_one(user_dict)
    return user

@api_router.post("/auth/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(request: Request, user_data: UserLogin):
    user = await db.users.find_one({"username": user_data.username}, {"_id": 0})
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check if 2FA is enabled
    if user.get("twofa_enabled"):
        if not user_data.totp_code:
            return TokenResponse(
                access_token="",
                user={"id": user["id"], "username": user["username"]},
                requires_2fa=True
            )
        
        # Verify TOTP code
        totp = pyotp.TOTP(user["twofa_secret"])
        if not totp.verify(user_data.totp_code):
            raise HTTPException(status_code=401, detail="Invalid 2FA code")
    
    # Set token expiration based on remember_me
    if user_data.remember_me:
        token_expiry = timedelta(days=60)
    else:
        token_expiry = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Create token
    access_token = create_access_token(
        data={"sub": user["id"]},
        expires_delta=token_expiry
    )
    
    user_response = {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "twofa_enabled": user.get("twofa_enabled", False)
    }
    
    return TokenResponse(
        access_token=access_token,
        user=user_response,
        requires_password_change=user.get("must_change_password", False)
    )

@api_router.post("/auth/change-password")
async def change_password(password_data: PasswordChange, current_user: dict = Depends(get_current_user)):
    if not verify_password(password_data.old_password, current_user["password_hash"]):
        raise HTTPException(status_code=400, detail="Invalid old password")
    
    new_hash = hash_password(password_data.new_password)
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {"password_hash": new_hash, "must_change_password": False}}
    )
    
    return {"message": "Password changed successfully"}

@api_router.post("/auth/2fa/setup")
async def setup_2fa(current_user: dict = Depends(get_current_user)):
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=current_user["username"], issuer_name="BeeHive Manager")
    
    # Store temporary secret
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {"twofa_secret_temp": secret}}
    )
    
    return {"secret": secret, "uri": uri}

@api_router.get("/auth/2fa/qrcode")
async def get_2fa_qrcode(current_user: dict = Depends(get_current_user)):
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    secret = user.get("twofa_secret_temp") or user.get("twofa_secret")
    
    if not secret:
        raise HTTPException(status_code=400, detail="2FA not set up")
    
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=current_user["username"], issuer_name="BeeHive Manager")
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    
    return StreamingResponse(buf, media_type="image/png")

@api_router.post("/auth/2fa/enable")
async def enable_2fa(data: Enable2FA, current_user: dict = Depends(get_current_user)):
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    secret = user.get("twofa_secret_temp")
    
    if not secret:
        raise HTTPException(status_code=400, detail="2FA setup not initiated")
    
    totp = pyotp.TOTP(secret)
    if not totp.verify(data.totp_code):
        raise HTTPException(status_code=400, detail="Invalid TOTP code")
    
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {"twofa_enabled": True, "twofa_secret": secret}, "$unset": {"twofa_secret_temp": ""}}
    )
    
    return {"message": "2FA enabled successfully"}

@api_router.post("/auth/2fa/disable")
async def disable_2fa(current_user: dict = Depends(get_current_user)):
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {"twofa_enabled": False}, "$unset": {"twofa_secret": ""}}
    )
    return {"message": "2FA disabled successfully"}

# User Management
@api_router.get("/users", response_model=List[Dict])
async def get_users(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view users")
    
    users = await db.users.find({}, {"_id": 0, "password_hash": 0}).to_list(100)
    return users

@api_router.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete users")
    
    if user_id == current_user["id"]:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"}

# Website Management
@api_router.post("/websites", response_model=Website)
async def create_website(website_data: WebsiteCreate, current_user: dict = Depends(get_current_user)):
    # Check website limit
    count = await db.websites.count_documents({"owner_id": current_user["id"]})
    if count >= 10:
        raise HTTPException(status_code=400, detail="Maximum 10 websites allowed")
    
    website = Website(
        name=website_data.name,
        url=website_data.url,
        owner_id=current_user["id"]
    )
    
    website_dict = website.model_dump()
    website_dict["created_at"] = website_dict["created_at"].isoformat()
    
    await db.websites.insert_one(website_dict)
    return website

@api_router.get("/websites", response_model=List[Dict])
async def get_websites(current_user: dict = Depends(get_current_user)):
    if current_user["role"] == "admin":
        websites = await db.websites.find({}, {"_id": 0}).to_list(100)
    else:
        websites = await db.websites.find({"owner_id": current_user["id"]}, {"_id": 0}).to_list(100)
    return websites

@api_router.delete("/websites/{website_id}")
async def delete_website(website_id: str, current_user: dict = Depends(get_current_user)):
    website = await db.websites.find_one({"id": website_id}, {"_id": 0})
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    
    if website["owner_id"] != current_user["id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await db.websites.delete_one({"id": website_id})
    await db.monitoring_data.delete_many({"website_id": website_id})
    
    return {"message": "Website deleted successfully"}

@api_router.post("/websites/{website_id}/check")
async def check_website(website_id: str, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    website = await db.websites.find_one({"id": website_id}, {"_id": 0})
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    
    # Get monitoring settings
    settings = await db.settings.find_one({"key": "monitoring"}) or {}
    check_ssl = settings.get("check_ssl", True)
    multi_location = settings.get("multi_location", False)
    
    # Use advanced monitoring
    background_tasks.add_task(monitor_website_complete, website_id, website["url"], check_ssl, multi_location)
    return {"message": "Website check initiated with advanced monitoring"}

# Monitoring Data
@api_router.get("/monitoring/{website_id}")
async def get_monitoring_data(website_id: str, limit: int = 50, current_user: dict = Depends(get_current_user)):
    data = await db.monitoring_data.find(
        {"website_id": website_id},
        {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    return data

@api_router.get("/stats/weekly")
async def get_weekly_stats(current_user: dict = Depends(get_current_user)):
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    
    # Get all monitoring data from the last week
    pipeline = [
        {"$match": {"timestamp": {"$gte": week_ago.isoformat()}}},
        {"$group": {
            "_id": None,
            "total_checks": {"$sum": 1},
            "avg_latency": {"$avg": "$latency"},
            "online_count": {"$sum": {"$cond": ["$is_online", 1, 0]}}
        }}
    ]
    
    result = await db.monitoring_data.aggregate(pipeline).to_list(1)
    
    if not result:
        return {
            "message": "Welcome back! Start monitoring your websites to see insights.",
            "total_checks": 0,
            "avg_latency": 0,
            "uptime_percentage": 0,
            "improvement": "Add websites to begin tracking performance."
        }
    
    stats = result[0]
    uptime = (stats["online_count"] / stats["total_checks"] * 100) if stats["total_checks"] > 0 else 0
    
    improvements = [
        "Consider enabling CDN for faster global access.",
        "Optimize images to reduce page load time.",
        "Enable browser caching for better performance.",
        "Minimize JavaScript and CSS files.",
        "Use lazy loading for below-the-fold content."
    ]
    
    import random
    improvement = random.choice(improvements)
    
    message = "Welcome back! "
    if uptime > 99:
        message += "Excellent uptime this week! Your sites are performing great."
    elif uptime > 95:
        message += "Good uptime this week. Keep up the monitoring."
    else:
        message += "Your sites had some downtime this week. Check the logs for details."
    
    return {
        "message": message,
        "total_checks": stats["total_checks"],
        "avg_latency": round(stats.get("avg_latency", 0), 2),
        "uptime_percentage": round(uptime, 2),
        "improvement": improvement
    }

# Setup Check
@api_router.get("/setup/status")
async def check_setup():
    admin_count = await db.users.count_documents({"role": "admin"})
    return {"setup_complete": admin_count > 0}

@api_router.post("/setup/initialize")
async def initialize_setup(user_data: UserCreate):
    admin_count = await db.users.count_documents({"role": "admin"})
    if admin_count > 0:
        raise HTTPException(status_code=400, detail="Setup already completed")
    
    user = User(
        username=user_data.username,
        email=user_data.email,
        role="admin",
        must_change_password=False
    )
    
    user_dict = user.model_dump()
    user_dict["password_hash"] = hash_password(user_data.password)
    user_dict["created_at"] = user_dict["created_at"].isoformat()
    
    await db.users.insert_one(user_dict)
    return {"message": "Setup completed successfully", "user": user}

@api_router.get("/")
async def root():
    return {"message": "BeeHive - Website Manager API"}

# Alert Thresholds Endpoints
@api_router.get("/thresholds")
async def get_alert_thresholds(current_user: dict = Depends(get_current_user)):
    thresholds = await db.alert_thresholds.find({"user_id": current_user["id"]}, {"_id": 0}).to_list(None)
    return thresholds

@api_router.post("/thresholds")
async def create_alert_threshold(threshold: AlertThreshold, current_user: dict = Depends(get_current_user)):
    # Check if website belongs to user
    website = await db.websites.find_one({"id": threshold.website_id}, {"_id": 0})
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    
    if website["owner_id"] != current_user["id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    threshold_dict = threshold.model_dump()
    threshold_dict["id"] = str(uuid.uuid4())
    threshold_dict["user_id"] = current_user["id"]
    threshold_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.alert_thresholds.insert_one(threshold_dict)
    return {"message": "Alert threshold created successfully", "threshold": threshold_dict}

@api_router.put("/thresholds/{threshold_id}")
async def update_alert_threshold(threshold_id: str, threshold: AlertThreshold, current_user: dict = Depends(get_current_user)):
    existing = await db.alert_thresholds.find_one({"id": threshold_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Threshold not found")
    
    if existing["user_id"] != current_user["id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    threshold_dict = threshold.model_dump()
    await db.alert_thresholds.update_one({"id": threshold_id}, {"$set": threshold_dict})
    
    return {"message": "Alert threshold updated successfully"}

@api_router.delete("/thresholds/{threshold_id}")
async def delete_alert_threshold(threshold_id: str, current_user: dict = Depends(get_current_user)):
    existing = await db.alert_thresholds.find_one({"id": threshold_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Threshold not found")
    
    if existing["user_id"] != current_user["id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await db.alert_thresholds.delete_one({"id": threshold_id})
    return {"message": "Alert threshold deleted successfully"}

# Export Reports Endpoint
@api_router.post("/export/report")
@limiter.limit("5/minute")
async def export_report(request: Request, export_req: ExportRequest, current_user: dict = Depends(get_current_user)):
    """Export monitoring report as ZIP file"""
    try:
        zip_content = await generate_monitoring_report(db, current_user["id"], export_req.days, export_req.format)
        
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        filename = f"beehive_report_{timestamp}.zip"
        
        return Response(
            content=zip_content,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate report")

# Monitoring Settings Endpoints
@api_router.get("/settings/monitoring")
async def get_monitoring_settings(current_user: dict = Depends(get_current_user)):
    settings = await db.settings.find_one({"key": "monitoring"}, {"_id": 0})
    if not settings:
        # Return defaults
        return {
            "key": "monitoring",
            "check_ssl": True,
            "multi_location": False,
            "notifications_enabled": True,
            "monitoring_interval_minutes": 5,
            "discord_notifications": True
        }
    return settings

@api_router.post("/settings/monitoring")
async def update_monitoring_settings(settings: MonitoringSettings, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update settings")
    
    settings_dict = settings.model_dump()
    settings_dict["key"] = "monitoring"
    
    await db.settings.update_one(
        {"key": "monitoring"},
        {"$set": settings_dict},
        upsert=True
    )
    
    # Update environment variable for monitoring interval
    os.environ['MONITORING_INTERVAL_MINUTES'] = str(settings.monitoring_interval_minutes)
    
    return {"message": "Monitoring settings updated successfully", "settings": settings_dict}

@api_router.get("/settings/notifications")
async def get_notification_settings(current_user: dict = Depends(get_current_user)):
    user_settings = await db.user_settings.find_one({"user_id": current_user["id"]}, {"_id": 0})
    if not user_settings:
        return {"user_id": current_user["id"], "discord_webhook": None}
    return user_settings

@api_router.post("/settings/notifications")
async def update_notification_settings(settings: NotificationSettings, current_user: dict = Depends(get_current_user)):
    settings_dict = settings.model_dump()
    settings_dict["user_id"] = current_user["id"]
    
    await db.user_settings.update_one(
        {"user_id": current_user["id"]},
        {"$set": settings_dict},
        upsert=True
    )
    
    # Update Discord webhook environment variable if provided
    if settings.discord_webhook:
        os.environ['DISCORD_WEBHOOK_URL'] = settings.discord_webhook
    
    return {"message": "Notification settings updated successfully"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("BeeHive - Website Manager starting up...")
    # Start the monitoring scheduler
    try:
        scheduler = start_scheduler()
        app.state.scheduler = scheduler
        logger.info("Monitoring scheduler started successfully")
    except Exception as e:
        logger.error(f"Failed to start monitoring scheduler: {str(e)}")

@app.on_event("shutdown")
async def shutdown_db_client():
    # Shutdown scheduler
    if hasattr(app.state, 'scheduler'):
        app.state.scheduler.shutdown()
        logger.info("Monitoring scheduler shut down")
    client.close()
