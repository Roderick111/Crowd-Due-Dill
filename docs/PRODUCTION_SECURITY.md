# Production Security Guide for Crowd Due Dill

## 🔒 Security Considerations for Docker Deployment

### Firewall Configuration

⚠️ **Important**: Docker bypasses UFW/firewalld rules when exposing ports. Our nginx-proxy setup mitigates this by only exposing ports 80/443.

#### Recommended Firewall Rules:
```bash
# Allow SSH (adjust port if needed)
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS only
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw --force enable

# Check status
sudo ufw status
```

#### Docker Network Security:
```bash
# Our setup uses custom networks for isolation
# nginx-proxy network: only web traffic
# Internal network: app-to-app communication only
```

### SSL/TLS Configuration

#### Let's Encrypt Certificates:
- **Automatic renewal** via acme-companion
- **Strong ciphers** configured by nginx-proxy
- **HSTS headers** enabled by default

#### Environment Variables Security:
```bash
# Never commit .env file to git
echo ".env" >> .gitignore

# Set proper file permissions
chmod 600 .env

# Regularly rotate API keys
# - Auth0 secrets
# - Stripe keys  
# - OpenAI API keys
```

### Container Security

#### Resource Limits:
Our docker-compose.production.yml includes:
```yaml
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
```

#### Volume Security:
- **Named volumes** instead of bind mounts
- **Read-only mounts** where possible
- **Data persistence** in `/app/data`

### Monitoring & Logging

#### Log Management:
```bash
# Check container logs
docker compose -f docker-compose.production.yml logs -f

# Log rotation (handled automatically by Docker)
# Logs stored in: /var/lib/docker/containers/
```

#### Health Checks:
All services include health checks for monitoring:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### Regular Maintenance

#### Security Updates:
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker compose -f docker-compose.production.yml pull
docker compose -f docker-compose.production.yml up -d

# Clean up old images
docker image prune -f
```

#### SSL Certificate Monitoring:
```bash
# Check certificate expiry (automatic with acme-companion)
docker compose -f docker-compose.production.yml logs acme-companion

# Manual certificate check
echo | openssl s_client -servername your-domain.com -connect your-domain.com:443 2>/dev/null | openssl x509 -noout -dates
```

### Backup Strategy

#### Critical Data to Backup:
- **Environment variables** (.env file)
- **Application data** (named volumes)
- **SSL certificates** (handled by acme-companion)

#### Backup Commands:
```bash
# Backup application data
docker run --rm -v crowd_due_dill_data:/data -v $(pwd):/backup alpine tar czf /backup/crowd-due-dill-data-$(date +%Y%m%d).tar.gz -C /data .

# Backup SSL certificates
docker run --rm -v crowd_due_dill_ssl_certs:/certs -v $(pwd):/backup alpine tar czf /backup/ssl-certs-$(date +%Y%m%d).tar.gz -C /certs .
```

### Incident Response

#### Emergency Procedures:
```bash
# Stop all services
docker compose -f docker-compose.production.yml down

# Emergency SSL renewal
docker compose -f docker-compose.production.yml restart acme-companion

# Check service status
docker compose -f docker-compose.production.yml ps
```

#### Log Analysis:
```bash
# Application logs
docker compose -f docker-compose.production.yml logs crowd-due-dill-backend

# Nginx proxy logs
docker compose -f docker-compose.production.yml logs nginx-proxy

# SSL logs
docker compose -f docker-compose.production.yml logs acme-companion
``` 