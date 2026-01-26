# BeeHive - Website Manager

<div align="center">
  <h3>🐝 Self-Hostable Website Monitoring Tool 🐝</h3>
  <p>Monitor website latency, page speed, and uptime with ease</p>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Join Discord](https://img.shields.io/discord/YOUR_DISCORD_ID?color=7289DA&label=Discord&logo=discord&logoColor=white)](https://discord.gg/ykkkjwDnAD)
  ![Docker](https://img.shields.io/badge/Docker-Ready-blue)
  ![Security](https://img.shields.io/badge/Security-2FA-green)
</div>

---

## 📚 Documentation

- [Quick Start Guide](QUICKSTART.md) - Get running in 5 minutes
- [Installation Guide](INSTALLATION.md) - Detailed setup instructions
- [Security Best Practices](SECURITY.md) - **Read this before deploying to production**
- [Contributing Guide](CONTRIBUTING.md) - How to contribute
- [API Documentation](#api-documentation) - API endpoints reference

---

## 🌟 Features

### Core Features
- **Website Monitoring**: Track latency (ping time) and page load speed for up to 10 websites
- **Automated Monitoring**: Schedule automatic checks at configurable intervals (1-60 minutes)
- **Real-time Checks**: Manual website health checks with instant results
- **Performance Analytics**: View detailed charts and statistics over time
- **Page Speed Testing**: Analyze and improve website loading speeds
- **SSL Certificate Monitoring**: Track SSL certificate expiration dates with alerts
- **Multi-Location Monitoring**: Check websites from multiple geographic locations
- **Email & Slack Notifications**: Receive instant alerts for downtime and SSL expiration

### Security & Authentication
- **Username/Password Authentication**: Secure login system
- **2FA Support**: Time-based One-Time Password (TOTP) authentication
- **Role-Based Access**: Admin and sub-admin accounts with granular permissions
- **Multi-Admin Support**: Create and manage multiple sub-admin accounts

### User Experience
- **Light/Dark Mode**: Seamless theme switching
- **Welcome Popup**: Weekly roundup with performance insights
- **Improvement Suggestions**: AI-driven tips to enhance website performance
- **Beautiful UI**: Modern design with black/yellow/white BeeHive theme

### Technical
- **Self-Hostable**: Full control over your data
- **Docker Ready**: Easy deployment with Docker & Docker Compose
- **RESTful API**: FastAPI backend with async support
- **React Frontend**: Modern, responsive single-page application
- **MongoDB**: Reliable NoSQL database for monitoring data

---

## 📦 Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React 19 with React Router
- **Database**: MongoDB
- **Authentication**: JWT + bcrypt + PyOTP (2FA)
- **Monitoring**: httpx for async HTTP requests
- **Charts**: Recharts for data visualization
- **UI Components**: Shadcn/UI with Tailwind CSS

---

## 🚀 Quick Start

### Prerequisites

- Docker (v24.0.0 or later)
- Docker Compose (v2.20.0 or later)
- Git

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/OfficialMikeJ/beehive-manager.git
cd beehive-manager
```

2. **Generate a Secure JWT Secret**

**⚠️ CRITICAL SECURITY STEP ⚠️**

Before deploying to production, you MUST generate a secure JWT secret token:

```bash
# Generate a secure random JWT secret (Linux/Mac)
openssl rand -base64 32

# Or using Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Or using Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

**🚨 SECURITY WARNING 🚨**

**DO NOT SHARE YOUR JWT TOKEN WITH ANYONE. PERIOD.**

Sharing your JWT secret will:
- Expose your monitoring tool to unauthorized access
- Allow attackers to forge authentication tokens
- Compromise all user accounts
- Grant full access to your monitoring data

Keep this token secure like a password!

3. **Configure environment variables**

The application uses default environment variables that work out of the box. However, for production deployment, you should update the following:

**Backend** (`/app/backend/.env`):
```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="beehive_db"
CORS_ORIGINS="*"
JWT_SECRET="your-super-secure-secret-key-change-this-in-production"
```

**Frontend** (`/app/frontend/.env`):
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

> **Security Note**: Always change the `JWT_SECRET` in production!

3. **Build and run with Docker Compose**

```bash
docker-compose up -d
```

This will start:
- MongoDB on port `27017`
- Backend API on port `8001`
- Frontend on port `3000`

4. **Access the application**

Open your browser and navigate to:
```
http://localhost:3000
```

5. **Initial Setup**

On first launch, you'll be greeted with a setup wizard:

- Create your **admin account**
- Set a strong password (minimum 8 characters)
- Complete the setup

> **Important**: The initial admin credentials you create during setup are the master credentials for your BeeHive instance. Store them securely!

---

## 🛠️ Usage Guide

### First Time Setup

1. **Navigate to the setup page** (automatic on first visit)
2. **Create admin account**:
   - Username: `admin` (or your preferred username)
   - Email: `admin@example.com`
   - Password: Minimum 8 characters
   - Confirm password
3. **Click "Complete Setup"**
4. **Login** with your new credentials

### Dashboard Overview

After logging in, you'll see:

- **Overview Page**: Quick stats on all websites, uptime, and latency
- **Websites Page**: Manage and monitor your websites
- **Users Page** (Admin only): Create sub-admin accounts
- **Settings Page**: Change password, enable 2FA

### Adding Websites

1. Go to **Websites** page
2. Click **"Add Website"**
3. Enter:
   - Website Name: `My Blog`
   - Website URL: `https://myblog.com`
4. Click **"Add Website"**
5. Click **"Check Now"** to run an immediate health check

### Monitoring Data

- **Check Now**: Manual website check
- **View Details**: See latency charts and statistics
- **Delete**: Remove website from monitoring

### Setting Up 2FA

1. Go to **Settings** page
2. Click **"Setup 2FA"**
3. Scan the QR code with an authenticator app (Google Authenticator, Authy, etc.)
4. Enter the 6-digit code to verify
5. Click **"Enable 2FA"**

### Managing Sub-Admins (Admin Only)

1. Go to **Users** page
2. Click **"Add Sub-Admin"**
3. Enter username, email, and password
4. Click **"Create Sub-Admin"**
5. Sub-admins can now login and manage websites

### Configuring Automated Monitoring (Admin Only)

1. Go to **Settings** page → **Monitoring** tab
2. Configure monitoring options:
   - **SSL Certificate Checking**: Monitor SSL expiration (30-day warning)
   - **Multi-Location Monitoring**: Check from multiple locations
   - **Email Notifications**: Receive downtime alerts via email
   - **Slack Notifications**: Get instant Slack alerts
   - **Monitoring Interval**: Set check frequency (1-60 minutes)
3. Click **"Save Monitoring Settings"**

### Setting Up Notifications

1. Go to **Settings** page → **Notifications** tab
2. Enter your **Email Address** for alerts
3. (Optional) Add **Slack Webhook URL** for instant notifications
4. Click **"Save Notification Settings"**

**Email Setup (SMTP)**: Add to backend `.env`:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
```

**Slack Setup**: Create a webhook at https://api.slack.com/messaging/webhooks

---

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

The project includes a production-ready `docker-compose.yml`:

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:7.0
    container_name: beehive-mongo
    restart: always
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      - MONGO_INITDB_DATABASE=beehive_db

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: beehive-backend
    restart: always
    ports:
      - "8001:8001"
    environment:
      - MONGO_URL=mongodb://mongodb:27017
      - DB_NAME=beehive_db
      - JWT_SECRET=your-secure-secret-key
    depends_on:
      - mongodb

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: beehive-frontend
    restart: always
    ports:
      - "3000:80"
    environment:
      - REACT_APP_BACKEND_URL=http://localhost:8001
    depends_on:
      - backend

volumes:
  mongodb_data:
```

### Build from Dockerfile

**Backend Dockerfile** (`/app/backend/Dockerfile`):

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
```

**Frontend Dockerfile** (`/app/frontend/Dockerfile`):

```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

COPY . .
RUN yarn build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Manual Docker Commands

```bash
# Build images
docker build -t beehive-backend ./backend
docker build -t beehive-frontend ./frontend

# Run MongoDB
docker run -d --name beehive-mongo -p 27017:27017 mongo:7.0

# Run Backend
docker run -d --name beehive-backend -p 8001:8001 \
  -e MONGO_URL="mongodb://beehive-mongo:27017" \
  -e DB_NAME="beehive_db" \
  beehive-backend

# Run Frontend
docker run -d --name beehive-frontend -p 3000:80 \
  -e REACT_APP_BACKEND_URL="http://localhost:8001" \
  beehive-frontend
```

---

## 📚 API Documentation

Once the backend is running, access the interactive API docs:

- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`

### Key Endpoints

#### Authentication
- `POST /api/setup/initialize` - Initial setup
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - Create sub-admin (admin only)
- `POST /api/auth/change-password` - Change password
- `POST /api/auth/2fa/setup` - Setup 2FA
- `POST /api/auth/2fa/enable` - Enable 2FA

#### Websites
- `GET /api/websites` - List all websites
- `POST /api/websites` - Add new website
- `DELETE /api/websites/{id}` - Delete website
- `POST /api/websites/{id}/check` - Manual health check

#### Monitoring
- `GET /api/monitoring/{website_id}` - Get monitoring data
- `GET /api/stats/weekly` - Weekly statistics

#### Users
- `GET /api/users` - List users (admin only)
- `DELETE /api/users/{id}` - Delete user (admin only)

---

---

## 🔐 Security Best Practices

### JWT Secret Token

**⚠️ CRITICAL SECURITY REQUIREMENT**

Your JWT secret is the master key to your BeeHive installation. Follow these guidelines:

#### Generate a Secure JWT Token

```bash
# Method 1: OpenSSL (Recommended)
openssl rand -base64 32

# Method 2: Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Method 3: Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

#### 🚨 SECURITY WARNING 🚨

**DO NOT SHARE YOUR JWT TOKEN WITH ANYONE. PERIOD.**

Exposing your JWT token will:
- ❌ Allow unauthorized access to your monitoring system
- ❌ Enable attackers to forge authentication tokens
- ❌ Compromise all user accounts and data
- ❌ Grant complete control over your BeeHive installation

#### JWT Token Security Checklist

- [ ] Generated a cryptographically secure random token
- [ ] Replaced default JWT_SECRET in `.env` file
- [ ] Never committed JWT secret to version control
- [ ] Never shared in screenshots, logs, or documentation
- [ ] Stored securely (password manager, secrets vault)
- [ ] Rotated token if potentially exposed

### Additional Security Measures

1. **Enable 2FA** for all accounts (especially admin)
2. **Use strong passwords** - minimum 12 characters with mixed case, numbers, symbols
3. **Regular updates** - Keep Docker images and dependencies updated
4. **HTTPS/SSL** - Always use encrypted connections in production
5. **Firewall rules** - Restrict access to MongoDB and backend ports
6. **Database authentication** - Enable MongoDB authentication in production
7. **Regular backups** - Schedule automated database backups
8. **Monitor logs** - Watch for suspicious login attempts

---

## 🔒 Security Features

### Password Security
- Bcrypt hashing with salt
- Minimum 8 character requirement
- Enforced password change on first login (if configured)

### Two-Factor Authentication
- TOTP-based 2FA (RFC 6238)
- QR code generation for easy setup
- Compatible with Google Authenticator, Authy, etc.

### JWT Authentication
- Secure token-based authentication
- Configurable token expiration (default: 30 minutes)
- Authorization header validation

### Role-Based Access Control
- Admin: Full access to all features
- Sub-admin: Limited access (configurable)

---

## 🛡️ Production Deployment

### Security Checklist

- [ ] Change `JWT_SECRET` to a strong random value
- [ ] Use HTTPS/SSL certificates (Let's Encrypt recommended)
- [ ] Set `CORS_ORIGINS` to your domain only
- [ ] Enable MongoDB authentication
- [ ] Use Docker secrets for sensitive data
- [ ] Set up firewall rules
- [ ] Regular database backups
- [ ] Monitor logs for suspicious activity

### Environment Variables for Production

```env
# Backend
MONGO_URL=mongodb://username:password@mongodb:27017
DB_NAME=beehive_production
JWT_SECRET=<generate-with-openssl-rand-base64-32>
CORS_ORIGINS=https://yourdomain.com

# Frontend
REACT_APP_BACKEND_URL=https://api.yourdomain.com
```

### Reverse Proxy (Nginx)

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🐛 Troubleshooting

### Common Issues

**1. Cannot connect to MongoDB**
```bash
# Check if MongoDB is running
docker ps | grep mongo

# Check MongoDB logs
docker logs beehive-mongo
```

**2. Backend not starting**
```bash
# Check backend logs
docker logs beehive-backend

# Verify environment variables
docker exec beehive-backend env
```

**3. Frontend shows connection error**
- Verify `REACT_APP_BACKEND_URL` is correct
- Check CORS settings in backend
- Ensure backend is accessible

**4. 2FA not working**
- Ensure device time is synchronized (NTP)
- Try with time-based code from authenticator app
- Regenerate 2FA secret if needed

---

## 📊 Monitoring Data Storage

BeeHive stores monitoring data in MongoDB with the following structure:

- **users**: User accounts and authentication data
- **websites**: Website configuration and status
- **monitoring_data**: Historical monitoring records

Data retention is unlimited by default. To implement retention policies:

```javascript
// MongoDB TTL Index (run in mongo shell)
db.monitoring_data.createIndex(
  { "timestamp": 1 },
  { expireAfterSeconds: 2592000 } // 30 days
)
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn server:app --reload --port 8001

# Frontend
cd frontend
yarn install
yarn start
```

---

## 📝 License

This project is open source and available under the MIT License.

---

## ❓ FAQ

**Q: How many websites can I monitor?**
A: Up to 10 websites per installation. This limit can be modified in the backend code.

**Q: Can I run multiple instances?**
A: Yes, each instance is independent with its own database.

**Q: Is there a mobile app?**
A: The web interface is fully responsive and works on mobile browsers.

**Q: How often are websites checked?**
A: Manual checks only by default. You can implement scheduled checks using cron or similar.

**Q: Can I export monitoring data?**
A: Yes, data is stored in MongoDB and can be exported using mongodump or custom queries.

---

## 📧 Support

For issues, questions, or contributions:

- **Discord Support**: Join our Discord server and open a ticket in the **#forms** channel
  
  [![Join Discord](https://img.shields.io/discord/YOUR_DISCORD_ID?color=7289DA&label=Discord&logo=discord&logoColor=white)](https://discord.gg/ykkkjwDnAD)
  
  Direct Link: https://discord.gg/ykkkjwDnAD

- **GitHub Issues**: Report bugs and feature requests
- **Pull Requests**: Contribute code improvements

---

## 🚀 Roadmap

- ✅ Automated scheduled monitoring
- ✅ Discord Webhooks for notifications
- ✅ SSL certificate expiration tracking
- ✅ Multi-location monitoring
- [ ] Custom alert thresholds
- [ ] Export reports (PDF/CSV)
- [ ] API rate limiting
- [ ] Additional webhook integrations (Slack, Microsoft Teams)

---

<div align="center">
  <p>Built with ♥️ by the BeeHive Team</p>
  <p>🐝 <strong>BeeHive - Website Manager</strong> 🐝</p>
</div>
