"""
BeeHive Monitoring Scheduler
Handles automated website monitoring and notifications
"""
import asyncio
import ssl
import socket
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
import httpx
import time
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

# Initialize MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'beehive_db')]


async def check_ssl_certificate(url: str) -> Dict[str, Any]:
    """Check SSL certificate expiration"""
    try:
        # Extract hostname from URL
        if url.startswith('https://'):
            hostname = url.replace('https://', '').split('/')[0].split(':')[0]
        else:
            return {"has_ssl": False, "days_until_expiry": None, "error": "Not an HTTPS URL"}
        
        # Connect and get certificate
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
                # Parse expiration date
                not_after = cert['notAfter']
                expiry_date = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                expiry_date = expiry_date.replace(tzinfo=timezone.utc)
                
                # Calculate days until expiry
                now = datetime.now(timezone.utc)
                days_until_expiry = (expiry_date - now).days
                
                return {
                    "has_ssl": True,
                    "expiry_date": expiry_date.isoformat(),
                    "days_until_expiry": days_until_expiry,
                    "issuer": cert.get('issuer'),
                    "subject": cert.get('subject'),
                    "is_expired": days_until_expiry < 0,
                    "expires_soon": days_until_expiry < 30
                }
    except Exception as e:
        logger.error(f"SSL check failed for {url}: {str(e)}")
        return {
            "has_ssl": False,
            "error": str(e),
            "days_until_expiry": None
        }


async def check_website_from_location(url: str, location: str = "primary") -> Dict[str, Any]:
    """
    Check website from a specific location
    In a production environment, this could use different proxy servers or VPN endpoints
    """
    start_time = time.time()
    monitoring_data = {
        "location": location,
        "is_online": False,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url)
            latency = (time.time() - start_time) * 1000  # Convert to ms
            
            monitoring_data.update({
                "latency": round(latency, 2),
                "page_load_time": round(latency, 2),
                "status_code": response.status_code,
                "is_online": 200 <= response.status_code < 400,
                "response_size": len(response.content)
            })
    except Exception as e:
        monitoring_data["error_message"] = str(e)
        logger.error(f"Website check failed for {url} from {location}: {str(e)}")
    
    return monitoring_data


async def monitor_website_complete(website_id: str, url: str, check_ssl: bool = True, 
                                   multi_location: bool = False) -> Dict[str, Any]:
    """
    Complete website monitoring with SSL and optional multi-location checks
    """
    import uuid
    
    # Primary location check
    primary_data = await check_website_from_location(url, "primary")
    
    # SSL Certificate check
    ssl_data = {}
    if check_ssl and url.startswith('https://'):
        ssl_data = await check_ssl_certificate(url)
    
    # Multi-location checks (if enabled)
    location_checks = [primary_data]
    if multi_location:
        # In production, these would use different geographic locations/proxies
        # For now, we'll simulate with additional checks
        locations = ["us-west", "eu-central"]
        for location in locations:
            location_data = await check_website_from_location(url, location)
            location_checks.append(location_data)
    
    # Calculate average metrics across locations
    online_count = sum(1 for check in location_checks if check.get("is_online", False))
    avg_latency = sum(check.get("latency", 0) for check in location_checks) / len(location_checks) if location_checks else 0
    
    # Create monitoring record
    monitoring_record = {
        "id": str(uuid.uuid4()),
        "website_id": website_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "latency": round(avg_latency, 2),
        "page_load_time": round(avg_latency, 2),
        "status_code": primary_data.get("status_code"),
        "is_online": online_count > 0,
        "error_message": primary_data.get("error_message"),
        "ssl_info": ssl_data if ssl_data else None,
        "location_checks": location_checks if multi_location else None
    }
    
    # Store in database
    await db.monitoring_data.insert_one(monitoring_record)
    
    # Update website status
    website_status = "online" if monitoring_record["is_online"] else "offline"
    await db.websites.update_one(
        {"id": website_id},
        {"$set": {
            "status": website_status,
            "last_checked": monitoring_record["timestamp"],
            "ssl_info": ssl_data if ssl_data else None
        }}
    )
    
    return monitoring_record


async def send_email_notification(to_email: str, subject: str, body: str):
    """Send email notification"""
    smtp_host = os.environ.get('SMTP_HOST')
    smtp_port = int(os.environ.get('SMTP_PORT', '587'))
    smtp_user = os.environ.get('SMTP_USER')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    from_email = os.environ.get('SMTP_FROM_EMAIL', smtp_user)
    
    if not all([smtp_host, smtp_user, smtp_password]):
        logger.warning("SMTP settings not configured, skipping email notification")
        return
    
    try:
        message = MIMEMultipart()
        message['From'] = from_email
        message['To'] = to_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'html'))
        
        await aiosmtplib.send(
            message,
            hostname=smtp_host,
            port=smtp_port,
            username=smtp_user,
            password=smtp_password,
            start_tls=True
        )
        logger.info(f"Email notification sent to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email notification: {str(e)}")


async def send_slack_notification(webhook_url: str, message: str):
    """Send Slack notification"""
    try:
        async with httpx.AsyncClient() as client:
            await client.post(webhook_url, json={"text": message})
        logger.info("Slack notification sent")
    except Exception as e:
        logger.error(f"Failed to send Slack notification: {str(e)}")


async def check_and_notify(website: Dict[str, Any], monitoring_data: Dict[str, Any]):
    """Check monitoring data and send notifications if needed"""
    website_id = website["id"]
    website_name = website["name"]
    website_url = website["url"]
    
    # Check for downtime
    if not monitoring_data["is_online"]:
        # Get owner information
        owner = await db.users.find_one({"id": website["owner_id"]}, {"_id": 0})
        if owner and owner.get("email"):
            subject = f"🚨 BeeHive Alert: {website_name} is DOWN"
            body = f"""
            <html>
            <body>
                <h2>Website Down Alert</h2>
                <p>Your website <strong>{website_name}</strong> is currently unreachable.</p>
                <p><strong>URL:</strong> {website_url}</p>
                <p><strong>Time:</strong> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                <p><strong>Error:</strong> {monitoring_data.get('error_message', 'Unknown error')}</p>
                <p>Please check your website as soon as possible.</p>
                <hr>
                <p><em>BeeHive - Website Manager</em></p>
            </body>
            </html>
            """
            await send_email_notification(owner["email"], subject, body)
    
    # Check for SSL expiration
    ssl_info = monitoring_data.get("ssl_info")
    if ssl_info and ssl_info.get("expires_soon"):
        days_left = ssl_info.get("days_until_expiry", 0)
        owner = await db.users.find_one({"id": website["owner_id"]}, {"_id": 0})
        if owner and owner.get("email"):
            subject = f"⚠️ BeeHive Alert: SSL Certificate Expiring Soon for {website_name}"
            body = f"""
            <html>
            <body>
                <h2>SSL Certificate Expiration Warning</h2>
                <p>The SSL certificate for <strong>{website_name}</strong> is expiring soon.</p>
                <p><strong>URL:</strong> {website_url}</p>
                <p><strong>Days Until Expiry:</strong> {days_left} days</p>
                <p><strong>Expiry Date:</strong> {ssl_info.get('expiry_date')}</p>
                <p>Please renew your SSL certificate to avoid service disruption.</p>
                <hr>
                <p><em>BeeHive - Website Manager</em></p>
            </body>
            </html>
            """
            await send_email_notification(owner["email"], subject, body)
    
    # Send Slack notification if webhook is configured
    slack_webhook = os.environ.get('SLACK_WEBHOOK_URL')
    if slack_webhook and not monitoring_data["is_online"]:
        message = f"🚨 *{website_name}* is DOWN\nURL: {website_url}\nTime: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"
        await send_slack_notification(slack_webhook, message)


async def scheduled_monitoring_task():
    """Main scheduled monitoring task that checks all websites"""
    logger.info("Starting scheduled monitoring task...")
    
    try:
        # Get all websites from database
        websites = await db.websites.find({}).to_list(None)
        logger.info(f"Found {len(websites)} websites to monitor")
        
        # Get monitoring settings
        settings = await db.settings.find_one({"key": "monitoring"}) or {}
        check_ssl = settings.get("check_ssl", True)
        multi_location = settings.get("multi_location", False)
        notifications_enabled = settings.get("notifications_enabled", True)
        
        # Monitor each website
        for website in websites:
            try:
                monitoring_data = await monitor_website_complete(
                    website["id"], 
                    website["url"],
                    check_ssl=check_ssl,
                    multi_location=multi_location
                )
                
                # Send notifications if enabled
                if notifications_enabled:
                    await check_and_notify(website, monitoring_data)
                    
            except Exception as e:
                logger.error(f"Error monitoring website {website.get('name', 'unknown')}: {str(e)}")
        
        logger.info("Scheduled monitoring task completed")
    except Exception as e:
        logger.error(f"Error in scheduled monitoring task: {str(e)}")


def start_scheduler():
    """Start the APScheduler for automated monitoring"""
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    
    scheduler = AsyncIOScheduler()
    
    # Get monitoring interval from environment (default: 5 minutes)
    interval_minutes = int(os.environ.get('MONITORING_INTERVAL_MINUTES', '5'))
    
    # Schedule the monitoring task
    scheduler.add_job(
        scheduled_monitoring_task,
        trigger=IntervalTrigger(minutes=interval_minutes),
        id='website_monitoring',
        name='Automated Website Monitoring',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info(f"Scheduler started - monitoring every {interval_minutes} minutes")
    return scheduler
