# Production Deployment Checklist

## Pre-Deployment Requirements

### ✅ Server Setup
- [ ] Production server accessible via SSH [[memory:6529604374433690318]]
- [ ] Docker installed and configured [[memory:2985192409657752994]]
- [ ] Domain DNS configured
- [ ] Firewall configured (ports 22, 80, 443)
- [ ] SSL email configured for Let's Encrypt

### ✅ Environment Configuration
- [ ] `.env` file configured with production values
- [ ] `.env.monitoring` file configured for monitoring stack
- [ ] Auth0 credentials verified [[memory:7948408943203327332]]
- [ ] Stripe keys configured
- [ ] OpenAI/Google API keys set
- [ ] SMTP settings for Grafana alerts configured

### ✅ Repository
- [ ] Latest code pushed to main branch ✅
- [ ] All monitoring integration committed ✅
- [ ] Deployment scripts are executable ✅

## Deployment Steps

### 1. Connect to Production Server
```bash
ssh root@188.34.196.228
```

### 2. Update Repository
```bash
cd /root/Crowd-Due-Dill/
git pull origin main
```

### 3. Configure Environment Files
```bash
# Check if .env exists and has correct values
cat .env | head -5

# Create monitoring environment if not exists
cp config/monitoring.env.example .env.monitoring
nano .env.monitoring  # Configure with your values
```

### 4. Run Deployment
```bash
# Option A: Automated deployment (recommended)
./scripts/deploy-production-with-monitoring.sh

# Option B: Manual deployment
docker compose -f docker-compose.production.yml build --no-cache
docker compose -f docker-compose.production.yml up -d
docker compose -f docker-compose.monitoring.yml --env-file .env.monitoring up -d
```

### 5. Verify Deployment
```bash
./scripts/verify-monitoring.sh
```

## Post-Deployment Verification

### ✅ Main Application
- [ ] Health check: `curl http://localhost:8001/health`
- [ ] Metrics endpoint: `curl http://localhost:8001/metrics | head -20`
- [ ] Web interface accessible at domain
- [ ] SSL certificate working
- [ ] Auth0 authentication working

### ✅ Monitoring Stack
- [ ] Prometheus accessible: `curl http://localhost:9090/prometheus/-/healthy`
- [ ] Grafana accessible: `curl http://localhost:3000/api/health`
- [ ] Application metrics in Prometheus
- [ ] Component health metrics working
- [ ] System metrics (Node Exporter) working
- [ ] Container metrics (cAdvisor) working

### ✅ External Access
- [ ] Main application: `https://your-domain.com`
- [ ] Monitoring dashboard: `https://monitoring.your-domain.com`
- [ ] SSL certificates auto-renewing
- [ ] All services behind nginx-proxy

## Configuration Checklist

### Environment Variables to Verify
```bash
# Main application
DOMAIN_NAME=your-domain.com
ENABLE_METRICS=true
AUTH0_CLIENT_ID=v2QYBQK2VnpV51BG46l1SW3dYYhiNs86  # Note: correct ID

# Monitoring
MONITORING_DOMAIN=monitoring.your-domain.com
GRAFANA_ADMIN_PASSWORD=<secure-password>
SMTP_HOST=smtp.gmail.com
```

### Docker Networks
```bash
# Verify networks exist
docker network ls | grep -E "(proxy|monitoring)"

# Should show:
# proxy
# crowd_due_dill_monitoring
```

### Container Status
```bash
# All containers should be running
docker ps --format "table {{.Names}}\t{{.Status}}"

# Expected containers:
# crowd-due-dill-backend
# crowd-due-dill-proxy
# crowd-due-dill-ssl
# crowd-due-dill-prometheus
# crowd-due-dill-grafana
# crowd-due-dill-node-exporter
# crowd-due-dill-cadvisor
```

## Troubleshooting Commands

### Application Issues
```bash
# Check application logs
docker compose logs crowd-due-dill-backend

# Check database permissions [[memory:9098391257454260529]]
docker exec crowd-due-dill-backend ls -la /app/data/
docker exec -u root crowd-due-dill-backend chown -R appuser:appuser /app/data/

# Test metrics manually
docker exec crowd-due-dill-backend curl http://localhost:8001/metrics
```

### Monitoring Issues
```bash
# Check monitoring services
docker compose -f docker-compose.monitoring.yml logs

# Check Prometheus targets
curl http://localhost:9090/prometheus/api/v1/targets

# Reset Grafana password
docker exec -it crowd-due-dill-grafana grafana-cli admin reset-admin-password newpassword
```

### SSL/Proxy Issues
```bash
# Check acme-companion logs
docker logs crowd-due-dill-ssl

# Check nginx-proxy logs
docker logs crowd-due-dill-proxy

# Force certificate renewal
docker exec crowd-due-dill-ssl /app/force_renew
```

## Security Checklist

### ✅ Server Security
- [ ] SSH key authentication only
- [ ] Firewall configured (ufw)
- [ ] Regular security updates
- [ ] Non-root user for applications

### ✅ Application Security
- [ ] Environment files not in git
- [ ] Strong passwords for Grafana
- [ ] SSL certificates working
- [ ] CORS properly configured
- [ ] API rate limiting enabled

### ✅ Monitoring Security
- [ ] Grafana admin password changed
- [ ] Internal networks for service communication
- [ ] No sensitive data in metrics
- [ ] Log rotation configured

## Maintenance Tasks

### Daily
- [ ] Check application health
- [ ] Monitor disk usage
- [ ] Review error metrics

### Weekly
- [ ] Update system packages
- [ ] Check certificate expiry
- [ ] Review performance metrics
- [ ] Backup application data

### Monthly
- [ ] Update Docker images
- [ ] Clean old Docker images/volumes
- [ ] Review security logs
- [ ] Update documentation

## Rollback Plan

If deployment fails:

1. **Stop new services**:
   ```bash
   docker compose -f docker-compose.production.yml down
   docker compose -f docker-compose.monitoring.yml down
   ```

2. **Restore from backup** (if needed):
   ```bash
   # Restore data from backup
   docker run --rm -v crowd_due_dill_data:/data -v /root/backups/latest:/backup alpine tar xzf /backup/app_data.tar.gz -C /data
   ```

3. **Deploy previous version**:
   ```bash
   git checkout <previous-commit>
   # Deploy previous working version
   ```

4. **Verify rollback**:
   ```bash
   curl http://localhost:8001/health
   ```

## Success Criteria

Deployment is successful when:
- ✅ All containers are running and healthy
- ✅ Main application responds at domain
- ✅ Monitoring dashboards accessible
- ✅ SSL certificates working
- ✅ Metrics being collected correctly
- ✅ Component health monitoring working
- ✅ No critical errors in logs
- ✅ Database permissions correct [[memory:4455220904368756323]]

## Contact Information

- **Production Server**: 188.34.196.228 [[memory:6529604374433690318]]
- **Repository**: https://github.com/Roderick111/Crowd-Due-Dill
- **Monitoring**: Based on previous successful setup [[memory:2434024368312314981]]

---

**Note**: This deployment integrates the new clean monitoring architecture while maintaining compatibility with existing production setup. All monitoring components run in separate containers as planned. 