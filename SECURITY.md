# Security Policy

## 🔐 Security Best Practices for BeeHive

This document outlines security best practices and guidelines for deploying and maintaining BeeHive - Website Manager.

---

## ⚠️ Critical Security Requirements

### 1. JWT Secret Token

**Your JWT secret is the master key to your BeeHive installation.**

#### Generating a Secure JWT Token

**NEVER use the default JWT secret in production!**

Generate a cryptographically secure random token using one of these methods:

```bash
# Method 1: OpenSSL (Recommended - Most Secure)
openssl rand -base64 32

# Method 2: Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Method 3: Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"

# Method 4: /dev/urandom (Linux/Unix)
head -c 32 /dev/urandom | base64
```

#### 🚨 JWT TOKEN SECURITY WARNING 🚨

**DO NOT SHARE YOUR JWT TOKEN WITH ANYONE. PERIOD.**

If your JWT token is exposed, an attacker can:
- ✗ Forge authentication tokens for any user
- ✗ Gain complete administrative access
- ✗ Access all monitoring data
- ✗ Create, modify, or delete user accounts
- ✗ Control all monitored websites
- ✗ Bypass all authentication mechanisms

#### JWT Token Security Checklist

Before deploying to production, ensure:

- [ ] Generated a cryptographically secure random token (minimum 32 bytes)
- [ ] Updated `JWT_SECRET` in `/app/backend/.env`
- [ ] **NEVER** committed JWT secret to Git/version control
- [ ] **NEVER** shared in screenshots, documentation, or logs
- [ ] **NEVER** posted in Discord, forums, or support tickets
- [ ] Stored securely (password manager, HashiCorp Vault, AWS Secrets Manager)
- [ ] Documented who has access to the secret
- [ ] Have a rotation plan in place

#### If Your JWT Token is Compromised

If you suspect your JWT token has been exposed:

1. **Immediately generate a new JWT token**
   ```bash
   openssl rand -base64 32
   ```

2. **Update your `.env` file** with the new token

3. **Restart all services**
   ```bash
   docker-compose restart backend
   ```

4. **Force all users to re-login** (existing tokens will be invalidated)

5. **Review access logs** for suspicious activity
   ```bash
   docker-compose logs backend | grep "POST /api/auth/login"
   ```

6. **Change all user passwords** as a precaution

7. **Monitor for unauthorized access** for the next 24-48 hours

---

## 🛡️ Security Best Practices

### Authentication Security

#### 1. Enable Two-Factor Authentication (2FA)

- **Required for admin accounts** in production
- Recommended for all sub-admin accounts
- Uses TOTP (Time-based One-Time Password) standard
- Compatible with Google Authenticator, Authy, Microsoft Authenticator

#### 2. Password Requirements

Enforce strong password policies:
- Minimum 12 characters (8 is system minimum, 12+ recommended)
- Mix of uppercase, lowercase, numbers, and symbols
- No common passwords or dictionary words
- Never reuse passwords from other services
- Use a password manager (1Password, Bitwarden, LastPass)

#### 3. Account Management

- Regularly audit user accounts
- Remove inactive sub-admin accounts
- Review permission levels quarterly
- Use principle of least privilege
- Log all authentication attempts

### Network Security

#### 1. HTTPS/SSL Certificate

**Never run BeeHive without HTTPS in production!**

Use Let's Encrypt for free SSL certificates:

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot --nginx -d yourdomain.com
```

#### 2. Firewall Configuration

Restrict access to BeeHive services:

```bash
# Allow only necessary ports
sudo ufw allow 80/tcp    # HTTP (redirects to HTTPS)
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Block direct access to backend and MongoDB
sudo ufw deny 8001/tcp
sudo ufw deny 27017/tcp
```

Use a reverse proxy (Nginx) to expose only necessary services.

#### 3. CORS Configuration

Update `CORS_ORIGINS` in backend `.env`:

```env
# Development
CORS_ORIGINS=*

# Production - Restrict to your domain only
CORS_ORIGINS=https://yourdomain.com
```

### Database Security

#### 1. MongoDB Authentication

Enable authentication in production:

```yaml
# docker-compose.yml
mongodb:
  environment:
    - MONGO_INITDB_ROOT_USERNAME=admin
    - MONGO_INITDB_ROOT_PASSWORD=<secure-password>
```

Update `MONGO_URL` in backend:
```env
MONGO_URL=mongodb://admin:password@mongodb:27017
```

#### 2. Database Backups

Schedule regular automated backups:

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker exec beehive-mongo mongodump \
  --db beehive_db \
  --out /tmp/backup_$DATE

docker cp beehive-mongo:/tmp/backup_$DATE ./backups/
```

Run daily via cron:
```bash
0 2 * * * /path/to/backup-script.sh
```

#### 3. Data Encryption

Consider encrypting sensitive data:
- MongoDB encryption at rest
- Encrypted Docker volumes
- Application-level encryption for sensitive fields

### Docker Security

#### 1. Image Security

- Use official base images only
- Scan images for vulnerabilities
- Keep images updated
- Use specific version tags (not `latest`)

```bash
# Scan for vulnerabilities
docker scan beehive-backend
docker scan beehive-frontend
```

#### 2. Container Isolation

- Run containers with limited privileges
- Use Docker secrets for sensitive data
- Implement resource limits
- Separate networks for different services

#### 3. Regular Updates

Keep all components updated:

```bash
# Update base images
docker-compose pull

# Rebuild with latest code
git pull origin main
docker-compose up -d --build

# Update system packages
sudo apt update && sudo apt upgrade
```

### Application Security

#### 1. Environment Variables

Never hardcode credentials:

```python
# ✓ Correct
JWT_SECRET = os.environ['JWT_SECRET']

# ✗ Wrong
JWT_SECRET = "my-secret-key-123"
```

#### 2. Input Validation

All user input is validated:
- URL validation for website monitoring
- Email format validation
- Username/password requirements
- SQL injection prevention (using MongoDB parameterized queries)
- XSS protection (React auto-escapes)

#### 3. Rate Limiting

Implement rate limiting for API endpoints:

```python
# Future enhancement - not yet implemented
# Limit login attempts to prevent brute force
# Limit API calls to prevent abuse
```

### Monitoring and Logging

#### 1. Access Logs

Monitor authentication logs:

```bash
# View login attempts
docker-compose logs backend | grep "POST /api/auth/login"

# Failed login attempts
docker-compose logs backend | grep "401 Unauthorized"

# 2FA events
docker-compose logs backend | grep "2fa"
```

#### 2. Alert on Suspicious Activity

Watch for:
- Multiple failed login attempts
- Login attempts from unusual IP addresses
- Unexpected admin account creation
- Mass data exports
- Unusual API usage patterns

#### 3. Security Audit Trail

Log important security events:
- User login/logout
- Password changes
- 2FA enable/disable
- User account creation/deletion
- Permission changes

---

## 🔍 Security Checklist

Before deploying to production:

### Critical (Must Do)

- [ ] Generated secure JWT secret token (32+ bytes)
- [ ] Replaced default JWT_SECRET in `.env`
- [ ] Enabled HTTPS with valid SSL certificate
- [ ] Restricted CORS to your domain only
- [ ] Enabled 2FA for admin account
- [ ] Changed all default passwords
- [ ] Configured firewall rules
- [ ] Enabled MongoDB authentication
- [ ] Set up automated backups

### Important (Highly Recommended)

- [ ] Implemented reverse proxy (Nginx)
- [ ] Configured log monitoring
- [ ] Set up security alerts
- [ ] Documented security procedures
- [ ] Trained team on security practices
- [ ] Reviewed all user permissions
- [ ] Tested backup restoration
- [ ] Configured rate limiting

### Optional (Enhanced Security)

- [ ] Implemented IP whitelisting
- [ ] Configured intrusion detection
- [ ] Set up VPN access
- [ ] Enabled database encryption at rest
- [ ] Implemented audit logging
- [ ] Set up security scanning (Dependabot)
- [ ] Configured Docker secrets
- [ ] Implemented network segmentation

---

## 🚨 Reporting Security Vulnerabilities

If you discover a security vulnerability in BeeHive:

### DO NOT

- ✗ Open a public GitHub issue
- ✗ Post in Discord public channels
- ✗ Share details publicly before fix is available

### DO

1. **Join our Discord** server
2. **Open a private ticket** in the #forms channel
3. **Mark it as "Security Vulnerability"**
4. **Provide details**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will:
- Acknowledge receipt within 48 hours
- Investigate and validate the report
- Develop and test a fix
- Release a security patch
- Credit you (if desired) in the changelog

### Responsible Disclosure

We follow a 90-day disclosure timeline:
1. **Day 0**: Vulnerability reported
2. **Day 1-7**: Initial investigation and validation
3. **Day 7-30**: Develop and test fix
4. **Day 30-45**: Deploy patch and notify users
5. **Day 90**: Public disclosure (if not already patched)

---

## 📚 Additional Resources

### Security Tools

- **Let's Encrypt**: Free SSL certificates - https://letsencrypt.org
- **Certbot**: Automated certificate management - https://certbot.eff.org
- **Docker Bench**: Security audit for Docker - https://github.com/docker/docker-bench-security
- **OWASP**: Web application security best practices - https://owasp.org

### Security Standards

- **NIST Cybersecurity Framework**: https://www.nist.gov/cyberframework
- **CIS Benchmarks**: https://www.cisecurity.org/cis-benchmarks
- **OWASP Top 10**: https://owasp.org/www-project-top-ten

### Learning Resources

- **Security Training**: https://www.cybrary.it
- **Docker Security**: https://docs.docker.com/engine/security
- **MongoDB Security**: https://docs.mongodb.com/manual/security

---

## 📞 Security Support

For security-related questions:

**Discord**: https://discord.gg/ykkkjwDnAD (Private ticket in #forms)

**Response Time**: Within 48 hours for security issues

---

<div align="center">
  <p><strong>Security is everyone's responsibility</strong></p>
  <p>🔐 Keep BeeHive Secure 🔐</p>
</div>
