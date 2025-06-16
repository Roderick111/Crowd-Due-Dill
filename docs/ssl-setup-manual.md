# Manual SSL Certificate Setup

Manual commands for setting up SSL certificate for `crowd-reg.beautiful-apps.com`.

## Prerequisites
- DNS already pointing to your VPS (31.97.153.220) ✅
- SSH access to server: `ssh root@31.97.153.220`

## Step-by-Step Commands

### 1. Connect to Server
```bash
ssh root@31.97.153.220
```

### 2. Install Certbot (if not installed)
```bash
apt update
apt install -y certbot python3-certbot-nginx
```

### 3. Stop Nginx Temporarily
```bash
cd /opt/esoteric-vectors
docker-compose stop nginx
```

### 4. Get SSL Certificate
```bash
certbot certonly \
    --standalone \
    --email your-email@example.com \
    --agree-tos \
    --no-eff-email \
    --domains crowd-reg.beautiful-apps.com \
    --domains www.crowd-reg.beautiful-apps.com
```

### 5. Verify Certificate
```bash
ls -la /etc/letsencrypt/live/crowd-reg.beautiful-apps.com/
# Should show: fullchain.pem, privkey.pem, etc.
```

### 6. Set up Auto-Renewal
```bash
crontab -e
# Add this line:
# 0 12 * * * /usr/bin/certbot renew --quiet --deploy-hook 'cd /opt/esoteric-vectors && docker-compose restart nginx'
```

### 7. Start Application with SSL
```bash
cd /opt/esoteric-vectors
docker-compose up -d
```

### 8. Test SSL
```bash
curl -I https://crowd-reg.beautiful-apps.com/health
# Should return 200 OK with HTTPS
```

## Troubleshooting

### If Port 80 is Busy
```bash
# Find what's using port 80
netstat -tulpn | grep :80
# Stop the service or use --webroot method instead
```

### If Domain Verification Fails
```bash
# Check DNS propagation
dig crowd-reg.beautiful-apps.com
nslookup crowd-reg.beautiful-apps.com
```

### Check Certificate Status
```bash
certbot certificates
openssl x509 -in /etc/letsencrypt/live/crowd-reg.beautiful-apps.com/fullchain.pem -text -noout
```

## Expected Results

After successful setup:
- ✅ Certificate files in `/etc/letsencrypt/live/crowd-reg.beautiful-apps.com/`
- ✅ Site accessible at `https://crowd-reg.beautiful-apps.com`
- ✅ Automatic renewal configured
- ✅ HTTP redirects to HTTPS 