# Crowd Due Dill - Production Deployment Guide

Complete guide for deploying Crowd Due Dill with integrated monitoring to production.

## Overview

This deployment includes:
- **Main Application**: FastAPI backend with AI chat functionality
- **Monitoring Stack**: Prometheus, Grafana, Node Exporter, cAdvisor
- **SSL/Proxy**: Automatic SSL certificates via nginx-proxy + acme-companion
- **Metrics Integration**: Application metrics exposed to Prometheus

## Prerequisites

### Server Requirements
- Ubuntu 22.04+ or compatible Linux distribution
- Minimum 4GB RAM, 8GB+ recommended
- 20GB+ available disk space
- Docker and Docker Compose installed
- Domain name with DNS pointing to server

### Required Environment Files

1. **Main application environment (`.env`)**:
   ```bash
   cp config/production.env.example .env
   # Edit .env with your values
   ```

2. **Monitoring environment (`.env.monitoring`)**:
   ```bash
   cp config/monitoring.env.example .env.monitoring
   # Edit .env.monitoring with your values
   ```

## Quick Start Deployment

### Option 1: Automated Deployment (Recommended)

```bash
# 1. Copy deployment script to server
scp scripts/deploy-production-with-monitoring.sh root@your-server:/root/

# 2. SSH to server and run deployment
ssh root@your-server
cd /root
chmod +x deploy-production-with-monitoring.sh
./deploy-production-with-monitoring.sh
```

### Option 2: Manual Deployment

1. **Prepare the server**:
   ```bash
   # Update system
   apt update && apt upgrade -y
   
   # Install Docker (if not already installed)
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   
   # Create Docker networks
   docker network create proxy
   docker network create crowd_due_dill_monitoring
   ```

2. **Clone and configure**:
   ```bash
   git clone git@github.com:your-username/Crowd-Due-Dill.git
   cd Crowd-Due-Dill
   
   # Configure environment files
   cp config/production.env.example .env
   cp config/monitoring.env.example .env.monitoring
   # Edit both files with your actual values
   ```

3. **Deploy main application**:
   ```bash
   docker compose -f docker-compose.production.yml build --no-cache
   docker compose -f docker-compose.production.yml up -d
   ```

4. **Deploy monitoring stack**:
   ```bash
   docker compose -f docker-compose.monitoring.yml --env-file .env.monitoring up -d
   ```

5. **Verify deployment**:
   ```bash
   ./scripts/verify-monitoring.sh
   ```

## Configuration Details

### Environment Variables

#### Main Application (`.env`)
```bash
# Domain Configuration
DOMAIN_NAME=your-domain.com
SSL_EMAIL=admin@your-domain.com

# Monitoring Configuration
ENABLE_METRICS=true
METRICS_PORT=8001
MONITORING_DOMAIN=monitoring.your-domain.com

# Auth0 Configuration
AUTH0_DOMAIN=your-auth0-domain.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret
# ... (see production.env.example for all variables)
```

#### Monitoring (`.env.monitoring`)
```bash
# Monitoring Domain
MONITORING_DOMAIN=monitoring.your-domain.com
SSL_EMAIL=admin@your-domain.com

# Grafana Admin
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=your-secure-password

# Email Alerts
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
# ... (see monitoring.env.example for all variables)
```

## Architecture Overview

### Network Architecture
```
Internet
    ↓
nginx-proxy (ports 80, 443)
    ↓
┌─────────────────┬─────────────────┐
│  Main App       │  Monitoring     │
│  Network        │  Network        │
│                 │                 │
│  Backend:8001   │  Grafana:3000   │
│  /metrics       │  Prometheus:9090│
│                 │  Node-exp:9100  │
│                 │  cAdvisor:8080  │
└─────────────────┴─────────────────┘
```

### Monitoring Data Flow
```
Application Metrics (/metrics)
    ↓
Prometheus (scrapes every 15s)
    ↓
Grafana (queries Prometheus)
    ↓
Dashboards & Alerts
```

## Available Metrics

### Application Metrics
- **Component Health**: `component_health_status`
- **Request Metrics**: `crowdfunding_api_requests_total`
- **Chat Messages**: `chat_messages_total`
- **Processing Time**: `chat_processing_time_seconds`
- **Error Tracking**: `application_errors_total`
- **Active Sessions**: `active_sessions_count`

### System Metrics (Node Exporter)
- CPU usage, memory, disk, network
- Process statistics
- File system metrics

### Container Metrics (cAdvisor)
- Container CPU, memory usage
- Container network statistics
- Docker container health

## Access Points

After deployment, you can access:

- **Main Application**: `https://your-domain.com`
- **Grafana**: `https://monitoring.your-domain.com`
- **Prometheus**: `https://monitoring.your-domain.com/prometheus`
- **Metrics Endpoint**: `https://your-domain.com/metrics` (internal)
- **Health Check**: `https://your-domain.com/health`

## Verification and Troubleshooting

### Verification Script
```bash
./scripts/verify-monitoring.sh
```

This script checks:
- Container status
- Application health and metrics
- Prometheus scraping
- Grafana connectivity
- System monitoring components

### Common Issues

#### 1. Containers Not Starting
```bash
# Check logs
docker compose logs crowd-due-dill-backend
docker compose -f docker-compose.monitoring.yml logs grafana

# Check networks
docker network ls | grep crowd
```

#### 2. Metrics Not Appearing
```bash
# Check metrics endpoint
curl http://localhost:8001/metrics | head -20

# Check Prometheus targets
curl http://localhost:9090/prometheus/api/v1/targets
```

#### 3. SSL Certificate Issues
```bash
# Check acme-companion logs
docker logs crowd-due-dill-ssl

# Check nginx-proxy logs
docker logs crowd-due-dill-proxy
```

#### 4. Grafana Access Issues
```bash
# Check Grafana logs
docker logs crowd-due-dill-grafana

# Reset admin password
docker exec -it crowd-due-dill-grafana grafana-cli admin reset-admin-password newpassword
```

### Log Locations
- **Application logs**: Docker container logs
- **Prometheus data**: `/var/lib/docker/volumes/crowd_due_dill_prometheus_data`
- **Grafana data**: `/var/lib/docker/volumes/crowd_due_dill_grafana_data`
- **Application data**: `/var/lib/docker/volumes/crowd_due_dill_data`

## Maintenance

### Updates
```bash
# Update application
git pull origin main
docker compose -f docker-compose.production.yml build --no-cache
docker compose -f docker-compose.production.yml up -d

# Update monitoring
docker compose -f docker-compose.monitoring.yml pull
docker compose -f docker-compose.monitoring.yml up -d
```

### Backups
```bash
# Backup application data
docker run --rm -v crowd_due_dill_data:/data -v $(pwd):/backup alpine tar czf /backup/app_data_$(date +%Y%m%d).tar.gz -C /data .

# Backup monitoring data
docker run --rm -v crowd_due_dill_prometheus_data:/data -v $(pwd):/backup alpine tar czf /backup/prometheus_data_$(date +%Y%m%d).tar.gz -C /data .
docker run --rm -v crowd_due_dill_grafana_data:/data -v $(pwd):/backup alpine tar czf /backup/grafana_data_$(date +%Y%m%d).tar.gz -C /data .
```

### Performance Monitoring
- Monitor disk usage for time-series data
- Set up log rotation for container logs
- Monitor memory usage of monitoring containers
- Set up alerts for critical metrics

## Security Considerations

1. **Firewall Configuration**:
   ```bash
   ufw allow 22    # SSH
   ufw allow 80    # HTTP
   ufw allow 443   # HTTPS
   ufw enable
   ```

2. **Environment Security**:
   - Keep `.env` files secure and not in Git
   - Use strong passwords for Grafana admin
   - Regularly update Docker images
   - Monitor for security alerts

3. **Network Security**:
   - Internal networks for service communication
   - Only expose necessary ports
   - Use SSL for all public endpoints

## Support and Monitoring

### Health Checks
- Application health: `/health` endpoint
- Monitoring health: Built into verification script
- Automated alerts via Grafana (configure email/Slack)

### Key Metrics to Monitor
1. **Application Health**: Component status, error rates
2. **Performance**: Response times, throughput
3. **Resources**: CPU, memory, disk usage
4. **Business**: Chat volume, user activity

### Alert Setup
Configure alerts for:
- High error rates (>5% in 5 minutes)
- High response times (>2s average)
- Component failures
- High resource usage (>80% CPU/memory)
- Disk space warnings (>85% full)

## Next Steps

1. **Dashboard Configuration**: Import/create Grafana dashboards
2. **Alert Rules**: Set up monitoring alerts
3. **Log Aggregation**: Consider ELK stack for centralized logging
4. **Backup Strategy**: Automate regular backups
5. **Documentation**: Document your specific configuration 