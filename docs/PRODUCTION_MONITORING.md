# Production Monitoring for Crowd Due Dill

This document describes the production monitoring setup for the Crowd Due Dill AI chatbot application.

## Overview

The monitoring stack provides comprehensive observability for the production environment, including:

- **Grafana**: Beautiful dashboards and email alerting
- **Prometheus**: Metrics collection and storage
- **Node Exporter**: System metrics (CPU, memory, disk)
- **cAdvisor**: Container metrics
- **Email Alerts**: Direct from Grafana (no Alertmanager needed)

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Your AI App   │───▶│   Prometheus    │───▶│     Grafana     │
│ (crowd-due-dill)│    │  (Metrics DB)   │    │ (Dashboards)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │  Node Exporter  │              │
         │              │ (System Metrics)│              │
         │              └─────────────────┘              │
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │     cAdvisor    │              │
         │              │(Container Stats)│              │
         │              └─────────────────┘              │
         │                                               │
         └───────────────────────────────────────────────┘
                          Email Alerts
```

## Components

### 1. **Grafana** (Main Dashboard & Alerting)
- **Purpose**: Beautiful dashboards and email alerting
- **URL**: https://monitoring.crowd-reg.beautiful-apps.com
- **Port**: 3000 (internal)
- **Features**:
  - Pre-configured dashboards
  - Email alerts for critical issues
  - User management
  - SSL via nginx-proxy

### 2. **Prometheus** (Metrics Collection)
- **Purpose**: Collects and stores metrics from all sources
- **URL**: https://monitoring.crowd-reg.beautiful-apps.com/prometheus
- **Port**: 9090 (internal)
- **Retention**: 30 days, 10GB max
- **Scrapes**:
  - Main app metrics (`/metrics`)
  - Health checks (`/health`)
  - System metrics (Node Exporter)
  - Container metrics (cAdvisor)

### 3. **Node Exporter** (System Metrics)
- **Purpose**: Exports server hardware and OS metrics
- **Port**: 9100
- **Metrics**: CPU, memory, disk, network

### 4. **cAdvisor** (Container Metrics)
- **Purpose**: Container resource usage and performance
- **Port**: 8080
- **Metrics**: Container CPU, memory, network, disk I/O

## Deployment

### Prerequisites

1. **Domain Setup**: Configure DNS for your monitoring subdomain
   ```bash
   monitoring.crowd-reg.beautiful-apps.com → 188.34.196.228
   ```

2. **Environment Configuration**: Copy and configure environment file
   ```bash
   cp config/monitoring.env.example .env.monitoring
   # Edit .env.monitoring with your settings
   ```

3. **SMTP Configuration**: Set up email credentials for alerts
   - Gmail: Use App Passwords
   - Other providers: Use your SMTP settings

### Deploy to Production

```bash
# Deploy monitoring stack
./scripts/deploy-monitoring.sh
```

The script will:
1. Copy all configuration files to production
2. Deploy the monitoring stack with SSL
3. Verify deployment
4. Show access URLs

## Configuration

### Environment Variables (.env.monitoring)

```bash
# Domain and SSL
MONITORING_DOMAIN=monitoring.crowd-reg.beautiful-apps.com
SSL_EMAIL=admin@crowd-reg.beautiful-apps.com

# Grafana Admin
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=your-secure-password

# Email Alerts
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
SMTP_FROM_ADDRESS=monitoring@crowd-reg.beautiful-apps.com

# Alert Recipients
CRITICAL_ALERT_EMAILS=admin@crowd-reg.beautiful-apps.com,team@crowd-reg.beautiful-apps.com
WARNING_ALERT_EMAILS=team@crowd-reg.beautiful-apps.com
```

## Alerts

### Critical Alerts (Sent to admin + team)
- **Application Down**: App unreachable for > 1 minute
- **High Error Rate**: > 10% error rate for > 2 minutes
- **High Memory Usage**: > 90% memory for > 5 minutes

### Warning Alerts (Sent to team)
- **Slow Response Times**: 95th percentile > 5 seconds for > 3 minutes
- **High CPU Usage**: > 80% CPU for > 5 minutes
- **Low Disk Space**: > 85% disk usage for > 5 minutes

### Alert Configuration
- **Grouping**: Alerts grouped by service and severity
- **Timing**:
  - Critical: Check every 1m, repeat every 5m
  - Warning: Check every 2m, repeat every 30m
- **Email Format**: Rich HTML emails with links to dashboards

## Dashboards

### Main Dashboard: "Crowd Due Dill - Application Overview"
- **Application Status**: Uptime, response times, error rates
- **System Resources**: CPU, memory, disk usage
- **Container Metrics**: Docker container performance
- **API Performance**: Request rates, latency percentiles
- **Custom Metrics**: Chat processing times, vector search performance

## Maintenance

### Log Management
```bash
# View monitoring logs
ssh root@188.34.196.228
cd /root/Crowd-Due-Dill
docker compose -f docker-compose.monitoring.yml logs -f

# View specific service logs
docker compose -f docker-compose.monitoring.yml logs grafana
docker compose -f docker-compose.monitoring.yml logs prometheus
```

### Data Retention
- **Prometheus**: 30 days retention, 10GB max size
- **Grafana**: SQLite database, persistent via Docker volumes

### Backup Considerations
- **Grafana Database**: Stored in Docker volume `crowd_due_dill_grafana_data`
- **Prometheus Data**: Stored in Docker volume `crowd_due_dill_prometheus_data`
- **Configuration**: All config files are in Git

### Updates
```bash
# Update monitoring stack
./scripts/deploy-monitoring.sh
```

## Troubleshooting

### Common Issues

1. **Grafana not accessible**
   - Check domain DNS configuration
   - Verify nginx-proxy is running
   - Check SSL certificate generation

2. **No metrics in Grafana**
   - Verify Prometheus is scraping targets
   - Check main app `/metrics` endpoint
   - Verify network connectivity between containers

3. **Email alerts not working**
   - Test SMTP settings in Grafana
   - Check spam folder
   - Verify email credentials

4. **High resource usage**
   - Adjust Prometheus retention settings
   - Optimize scrape intervals
   - Check dashboard query efficiency

### Health Checks

```bash
# Quick health check
curl -f https://monitoring.crowd-reg.beautiful-apps.com/api/health
curl -f https://monitoring.crowd-reg.beautiful-apps.com/prometheus/-/healthy

# Detailed service status
ssh root@188.34.196.228
cd /root/Crowd-Due-Dill
docker compose -f docker-compose.monitoring.yml ps
```

## Security

### Access Control
- **Grafana**: Admin user + secure password
- **SSL**: Automatic certificates via Let's Encrypt
- **Network**: Internal Docker networks for service communication
- **Firewall**: Only HTTPS (443) and SSH (22) exposed

### Best Practices
1. Use strong passwords for Grafana admin
2. Regularly update Docker images
3. Monitor email alert volume
4. Review dashboard access patterns
5. Keep environment files secure (.env.monitoring)

## Performance Impact

### Resource Usage
- **Prometheus**: ~200MB RAM, ~1GB disk per week
- **Grafana**: ~100MB RAM, minimal disk
- **Node Exporter**: ~10MB RAM, minimal CPU
- **cAdvisor**: ~50MB RAM, low CPU

### Network Impact
- **Scraping**: 15s intervals, minimal bandwidth
- **Alerting**: Only when conditions met
- **Dashboard Access**: Only when viewing

## Integration with Main App

The monitoring stack integrates with your main application through:

1. **Metrics Endpoint**: `https://crowd-reg.beautiful-apps.com/metrics`
2. **Health Endpoint**: `https://crowd-reg.beautiful-apps.com/health`
3. **Custom Metrics**: Application-specific metrics from FastAPI
4. **Network**: Shared Docker networks for internal communication

## Next Steps

1. **Custom Dashboards**: Create specific dashboards for your use cases
2. **Additional Metrics**: Add business metrics (user registrations, chat volumes)
3. **Log Aggregation**: Consider adding ELK stack for log analysis
4. **APM**: Add application performance monitoring if needed
5. **Capacity Planning**: Monitor trends for scaling decisions 