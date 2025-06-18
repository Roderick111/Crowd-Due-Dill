#!/bin/bash

# Production Monitoring Deployment Script for Crowd Due Dill
# Deploys Grafana + Prometheus to production server with SSL

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PRODUCTION_SERVER="root@188.34.196.228"
PRODUCTION_PATH="/root/Crowd-Due-Dill"
COMPOSE_FILE="docker-compose.monitoring.yml"

echo -e "${BLUE}🎯 Deploying Crowd Due Dill Monitoring Stack${NC}"
echo "================================================="

# Check if we have the environment file
if [[ ! -f ".env.monitoring" ]]; then
    echo -e "${RED}❌ Error: .env.monitoring file not found!${NC}"
    echo -e "${YELLOW}💡 Please copy config/monitoring.env.example to .env.monitoring and configure it${NC}"
    exit 1
fi

echo -e "${BLUE}📋 Pre-deployment checks...${NC}"

# Check if monitoring compose file exists
if [[ ! -f "$COMPOSE_FILE" ]]; then
    echo -e "${RED}❌ Error: $COMPOSE_FILE not found!${NC}"
    exit 1
fi

# Check if SSH key exists
if [[ ! -f ~/.ssh/id_ed25519 ]]; then
    echo -e "${RED}❌ Error: SSH key not found at ~/.ssh/id_ed25519${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Pre-deployment checks passed${NC}"

# Function to run commands on production server
run_remote() {
    ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$PRODUCTION_SERVER" "$1"
}

# Function to copy files to production server
copy_to_production() {
    scp -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$1" "$PRODUCTION_SERVER:$PRODUCTION_PATH/$2"
}

echo -e "${BLUE}🔄 Syncing monitoring configuration...${NC}"

# Ensure monitoring directory exists on production
run_remote "mkdir -p $PRODUCTION_PATH/monitoring/grafana/provisioning/{datasources,alerting,dashboards}"
run_remote "mkdir -p $PRODUCTION_PATH/monitoring/prometheus"

# Copy monitoring files
echo -e "${YELLOW}📁 Copying Docker Compose file...${NC}"
copy_to_production "$COMPOSE_FILE" "."

echo -e "${YELLOW}📁 Copying Prometheus configuration...${NC}"
copy_to_production "monitoring/prometheus/prometheus.yml" "monitoring/prometheus/prometheus.yml"

echo -e "${YELLOW}📁 Copying Grafana configuration...${NC}"
copy_to_production "monitoring/grafana/provisioning/datasources/prometheus.yml" "monitoring/grafana/provisioning/datasources/prometheus.yml"
copy_to_production "monitoring/grafana/provisioning/alerting/notification-channels.yml" "monitoring/grafana/provisioning/alerting/"
copy_to_production "monitoring/grafana/provisioning/alerting/alert-rules.yml" "monitoring/grafana/provisioning/alerting/"
copy_to_production "monitoring/grafana/dashboards/crowd-due-dill-overview.json" "monitoring/grafana/dashboards/"

echo -e "${YELLOW}📁 Copying environment file...${NC}"
copy_to_production ".env.monitoring" "."

echo -e "${BLUE}🚀 Starting monitoring deployment...${NC}"

# Deploy monitoring stack
run_remote "cd $PRODUCTION_PATH && docker compose -f $COMPOSE_FILE --env-file .env.monitoring down || true"
run_remote "cd $PRODUCTION_PATH && docker compose -f $COMPOSE_FILE --env-file .env.monitoring pull"
run_remote "cd $PRODUCTION_PATH && docker compose -f $COMPOSE_FILE --env-file .env.monitoring up -d"

echo -e "${BLUE}⏳ Waiting for services to start...${NC}"
sleep 30

# Health checks
echo -e "${BLUE}🏥 Running health checks...${NC}"

MONITORING_DOMAIN=$(grep MONITORING_DOMAIN .env.monitoring | cut -d'=' -f2)

echo -e "${YELLOW}Checking Prometheus...${NC}"
if run_remote "cd $PRODUCTION_PATH && docker compose -f $COMPOSE_FILE logs prometheus | tail -5"; then
    echo -e "${GREEN}✅ Prometheus deployed${NC}"
else
    echo -e "${RED}❌ Prometheus deployment failed${NC}"
fi

echo -e "${YELLOW}Checking Grafana...${NC}"
if run_remote "cd $PRODUCTION_PATH && docker compose -f $COMPOSE_FILE logs grafana | tail -5"; then
    echo -e "${GREEN}✅ Grafana deployed${NC}"
else
    echo -e "${RED}❌ Grafana deployment failed${NC}"
fi

# Show service status
echo -e "${BLUE}📊 Service Status:${NC}"
run_remote "cd $PRODUCTION_PATH && docker compose -f $COMPOSE_FILE ps"

echo -e "${GREEN}🎉 Monitoring deployment complete!${NC}"
echo ""
echo -e "${BLUE}📱 Access your monitoring:${NC}"
echo -e "🌐 Grafana: https://$MONITORING_DOMAIN"
echo -e "📊 Prometheus: https://$MONITORING_DOMAIN/prometheus"
echo ""
echo -e "${YELLOW}📧 Email alerts are configured and will be sent to:${NC}"
grep "_ALERT_EMAILS" .env.monitoring | sed 's/^/   /'
echo ""
echo -e "${BLUE}🔧 Next steps:${NC}"
echo -e "1. Visit https://$MONITORING_DOMAIN and login with your Grafana credentials"
echo -e "2. Verify dashboards are loading correctly"
echo -e "3. Test email alerts by triggering a test alert"
echo -e "4. Configure additional notification channels if needed" 