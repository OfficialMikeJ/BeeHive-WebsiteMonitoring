# BeeHive - Website Manager
## Quick Start Guide (5 Minutes)

Get BeeHive running in just 5 minutes!

---

## 🚀 Quick Deploy

```bash
# 1. Clone repository
git clone https://github.com/OfficialMikeJ/beehive-manager.git
cd beehive-manager

# 2. Start with Docker Compose
docker-compose up -d

# 3. Open in browser
open http://localhost:3000
```

---

## ⚡ First-Time Setup (2 minutes)

### Step 1: Create Admin Account

When you open http://localhost:3000 for the first time:

1. Enter **Username**: `admin`
2. Enter **Email**: `admin@example.com`
3. Enter **Password**: (min 8 characters)
4. Confirm password
5. Click **"Complete Setup"**

### Step 2: Login

1. Username: `admin`
2. Password: (your password)
3. Click **"Sign In"**

### Step 3: Add Your First Website

1. Click **"Websites"** in the sidebar
2. Click **"Add Website"**
3. Name: `My Website`
4. URL: `https://example.com`
5. Click **"Add Website"**
6. Click **"Check Now"** to start monitoring

---

## 🎯 Key Features

✅ Monitor up to 10 websites
✅ Track latency and page speed
✅ 2FA security
✅ Multi-admin support
✅ Light/dark mode
✅ Weekly performance reports
✅ Self-hosted - your data stays with you

---

## 📊 Dashboard Overview

After login, you'll see:

- **Overview**: Quick stats and recent websites
- **Websites**: Manage and monitor websites
- **Users**: Create sub-admin accounts (admin only)
- **Settings**: Change password, enable 2FA

---

## 🔐 Enable 2FA (Recommended)

1. Go to **Settings**
2. Click **"Setup 2FA"**
3. Scan QR code with your authenticator app
4. Enter 6-digit code
5. Click **"Enable 2FA"**

---

## 👥 Add Team Members (Admin Only)

1. Go to **Users**
2. Click **"Add Sub-Admin"**
3. Enter username, email, password
4. Click **"Create Sub-Admin"**

---

## 🛠️ Common Commands

```bash
# Start BeeHive
docker-compose up -d

# Stop BeeHive
docker-compose down

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Update to latest version
git pull && docker-compose up -d --build
```

---

## 🎨 Theme

BeeHive uses a distinctive black/yellow/white theme:
- Click the moon/sun icon to toggle light/dark mode
- Theme preference is saved automatically

---

## 📱 Mobile Access

BeeHive is fully responsive! Access from any device:
- Smartphones
- Tablets
- Desktops

---

## 🆘 Need Help?

- **Discord Support**: Join our Discord server and open a ticket in **#forms** channel
  
  [![Join Discord](https://img.shields.io/discord/YOUR_DISCORD_ID?color=7289DA&label=Discord&logo=discord&logoColor=white)](https://discord.gg/ykkkjwDnAD)

- **Full Documentation**: See [README.md](README.md)
- **Installation Guide**: See [INSTALLATION.md](INSTALLATION.md)
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Issues**: GitHub Issues page

---

## 🔒 Security Tips

1. Change default JWT_SECRET in production
2. Enable 2FA for all accounts
3. Use strong passwords (12+ characters)
4. Keep Docker images updated
5. Enable HTTPS with SSL certificates

---

## 📈 What's Next?

After setup:

1. ✅ Add all your websites (up to 10)
2. ✅ Set up monitoring checks
3. ✅ Enable 2FA for security
4. ✅ Add team members as sub-admins
5. ✅ Review weekly performance reports

---

## 🐝 That's It!

You're now monitoring your websites with BeeHive!

**Pro Tips:**
- Check your websites regularly
- Review the weekly roundup popup
- Follow improvement suggestions
- Keep your data backed up

---

<div align="center">
  <p>🐝 <strong>Welcome to BeeHive!</strong> 🐝</p>
  <p>Happy Monitoring!</p>
</div>
