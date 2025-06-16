#!/bin/bash

# SSL Certificate Setup Script for crowd-reg.beautiful-apps.com
# Run this script on your VPS server as root

set -e  # Exit on any error

DOMAIN="crowd-reg.beautiful-apps.com"
EMAIL="your-email@example.com"  # Replace with your actual email
PROJECT_DIR="/opt/esoteric-vectors"

echo "🔐 Setting up SSL certificate for $DOMAIN"
echo "========================================"

# Step 1: Install Certbot (if not already installed)
echo "📦 Installing Certbot..."
if ! command -v certbot &> /dev/null; then
    apt update
    apt install -y certbot python3-certbot-nginx
    echo "✅ Certbot installed successfully"
else
    echo "✅ Certbot already installed"
fi

# Step 2: Stop nginx temporarily for standalone verification
echo "🛑 Stopping nginx temporarily..."
cd $PROJECT_DIR
docker-compose stop nginx || echo "Nginx not running or not found"

# Step 3: Get SSL certificate using standalone mode
echo "🔒 Obtaining SSL certificate for $DOMAIN..."
certbot certonly \
    --standalone \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    --domains $DOMAIN \
    --domains www.$DOMAIN

# Step 4: Verify certificate was created
echo "🔍 Verifying certificate files..."
if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ] && [ -f "/etc/letsencrypt/live/$DOMAIN/privkey.pem" ]; then
    echo "✅ SSL certificate successfully created!"
    echo "Certificate location: /etc/letsencrypt/live/$DOMAIN/"
    
    # Show certificate info
    echo "📋 Certificate information:"
    openssl x509 -in "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" -text -noout | grep -E "(Subject:|Issuer:|Not Before|Not After)"
else
    echo "❌ Certificate files not found!"
    exit 1
fi

# Step 5: Set up automatic renewal
echo "🔄 Setting up automatic renewal..."
if ! crontab -l | grep -q "certbot renew"; then
    (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet --deploy-hook 'cd $PROJECT_DIR && docker-compose restart nginx'") | crontab -
    echo "✅ Automatic renewal configured (daily at 12:00)"
else
    echo "✅ Automatic renewal already configured"
fi

# Step 6: Restart the application with SSL
echo "🚀 Starting application with SSL..."
cd $PROJECT_DIR
docker-compose up -d

# Step 7: Test SSL certificate
echo "🧪 Testing SSL certificate..."
sleep 10  # Wait for nginx to start
if curl -s "https://$DOMAIN/health" > /dev/null; then
    echo "✅ SSL certificate working correctly!"
    echo "🌐 Your site is now available at: https://$DOMAIN"
else
    echo "⚠️  SSL test failed. Check nginx logs:"
    echo "docker-compose logs nginx"
fi

echo ""
echo "🎉 SSL setup complete!"
echo "Certificate expires: $(openssl x509 -in "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" -noout -enddate | cut -d= -f2)"
echo "Renewal will happen automatically via cron job" 