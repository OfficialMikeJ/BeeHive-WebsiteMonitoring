# BeeHive - Website Manager
## Quick Installation Guide

This guide will help you get BeeHive up and running in minutes using Docker.

---

## Prerequisites

Before you begin, ensure you have:

- **Docker** (v24.0.0 or later) - [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose** (v2.20.0 or later) - Usually bundled with Docker Desktop
- **Git** - For cloning the repository

### Verify Prerequisites

```bash
docker --version
docker-compose --version
git --version
```

---

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/OfficialMikeJ/beehive-manager.git
cd beehive-manager
```

### 2. Configure Environment (Optional)

For a quick start, you can use the default settings. For production, copy and modify the environment file:

```bash
cp .env.example .env
```

Edit `.env` and update:
- `JWT_SECRET` - Change to a random secure string
- `REACT_APP_BACKEND_URL` - Update if deploying to a custom domain

### 3. Start BeeHive with Docker Compose

```bash
docker-compose up -d
```

This command will:
- Pull the MongoDB image
- Build the backend and frontend containers
- Start all services in detached mode

### 4. Verify Services are Running

```bash
docker-compose ps
```

You should see three containers running:
- `beehive-mongo` (MongoDB database)
- `beehive-backend` (FastAPI backend)
- `beehive-frontend` (React frontend)

### 5. Access BeeHive

Open your web browser and navigate to:

```
http://localhost:3000
```

---

## Initial Setup

When you first access BeeHive, you'll be guided through a setup wizard:

### Step 1: Create Admin Account

![Setup Screen](docs/setup-screen.png)

1. **Username**: Choose your admin username (e.g., `admin`)
2. **Email**: Enter your email address
3. **Password**: Create a strong password (minimum 8 characters)
4. **Confirm Password**: Re-enter your password
5. Click **"Complete Setup"**

### Step 2: Login

After setup, you'll be redirected to the login page:

1. Enter your **username** and **password**
2. Click **"Sign In"**

### Step 3: Welcome to BeeHive!

Upon first login, you'll see:
- Welcome popup with weekly roundup
- Dashboard overview with statistics
- Navigation menu on the left

---

## First Steps

### Add Your First Website

1. Click **"Websites"** in the sidebar
2. Click **"Add Website"** button
3. Fill in the details:
   - **Website Name**: `My Blog`
   - **Website URL**: `https://myblog.com`
4. Click **"Add Website"**
5. Click **"Check Now"** to run your first monitoring check

### Enable Two-Factor Authentication (Recommended)

1. Click **"Settings"** in the sidebar
2. In the "Two-Factor Authentication" section, click **"Setup 2FA"**
3. Scan the QR code with your authenticator app:
   - Google Authenticator
   - Authy
   - Microsoft Authenticator
   - Any TOTP-compatible app
4. Enter the 6-digit code from your app
5. Click **"Enable 2FA"**

### Create Sub-Admin Accounts (Admin Only)

1. Click **"Users"** in the sidebar
2. Click **"Add Sub-Admin"**
3. Fill in the details:
   - **Username**: `developer1`
   - **Email**: `dev@example.com`
   - **Password**: Create a strong password
4. Click **"Create Sub-Admin"**

---

## Managing BeeHive

### Start Services

```bash
docker-compose up -d
```

### Stop Services

```bash
docker-compose down
```

### View Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend

# MongoDB only
docker-compose logs -f mongodb
```

### Restart Services

```bash
docker-compose restart
```

### Update BeeHive

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart containers
docker-compose down
docker-compose up -d --build
```

---

## Backup and Restore

### Backup MongoDB Data

```bash
# Create backup directory
mkdir -p backups

# Backup database
docker exec beehive-mongo mongodump \
  --db beehive_db \
  --out /tmp/backup

# Copy backup from container
docker cp beehive-mongo:/tmp/backup ./backups/backup-$(date +%Y%m%d)
```

### Restore MongoDB Data

```bash
# Copy backup to container
docker cp ./backups/backup-20240126 beehive-mongo:/tmp/restore

# Restore database
docker exec beehive-mongo mongorestore \
  --db beehive_db \
  /tmp/restore/beehive_db
```

---

## Troubleshooting

### Port Already in Use

If ports 3000, 8001, or 27017 are already in use:

1. Edit `docker-compose.yml`
2. Change the port mappings:
   ```yaml
   ports:
     - "3001:80"  # Change 3000 to 3001
   ```
3. Restart: `docker-compose up -d`

### Cannot Connect to Backend

1. Check if backend is running: `docker-compose ps`
2. View backend logs: `docker-compose logs backend`
3. Verify environment variables in `.env`
4. Ensure `REACT_APP_BACKEND_URL` matches your backend URL

### MongoDB Connection Failed

1. Check MongoDB logs: `docker-compose logs mongodb`
2. Verify MongoDB is running: `docker-compose ps`
3. Check `MONGO_URL` in backend environment

### Frontend Shows Blank Page

1. Clear browser cache and reload
2. Check frontend logs: `docker-compose logs frontend`
3. Verify frontend build: `docker-compose up --build frontend`

---

## Uninstall

To completely remove BeeHive:

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: This deletes all data!)
docker-compose down -v

# Remove images
docker rmi beehive-backend beehive-frontend
```

---

## Getting Help

- **Documentation**: See [README.md](README.md) for detailed features
- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Join community discussions on GitHub

---

## What's Next?

After installation, explore these features:

1. **Add more websites** - Monitor up to 10 websites
2. **View monitoring data** - Check latency charts and statistics
3. **Enable 2FA** - Add extra security to your account
4. **Create sub-admins** - Share access with your team
5. **Customize settings** - Change password, toggle themes

---

## Production Deployment

For production deployment, see the **Production Deployment** section in [README.md](README.md) for:

- SSL/HTTPS configuration
- Domain setup with Nginx
- Security best practices
- Performance optimization
- Automated backups

---

<div align="center">
  <p>🐝 <strong>Happy Monitoring with BeeHive!</strong> 🐝</p>
</div>
