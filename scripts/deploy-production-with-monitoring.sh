#!/bin/bash

# Production Deployment Script for Crowd Due Dill with Monitoring
# Deploys both the main application and monitoring stack
# Designed for production server deployment

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="/tmp/crowd-due-dill-deploy-$(date +%Y%m%d-%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${1}" | tee -a "$LOG_FILE"
}

log_info() {
    log "${BLUE}[INFO]${NC} $1"
}

log_success() {
    log "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    log "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    log "${RED}[ERROR]${NC} $1"
}

# Check if running as root or with sudo
check_permissions() {
    log_info "Checking permissions..."
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root or with sudo"
        exit 1
    fi
    log_success "Running with appropriate permissions"
}

# Check required files
check_requirements() {
    log_info "Checking deployment requirements..."
    
    local required_files=(
        "$PROJECT_DIR/.env"
        "$PROJECT_DIR/docker-compose.production.yml"
        "$PROJECT_DIR/docker-compose.monitoring.yml"
        "$PROJECT_DIR/Dockerfile"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log_error "Required file not found: $file"
            exit 1
        fi
    done
    
    # Check for monitoring configuration
    if [[ ! -f "$PROJECT_DIR/.env.monitoring" ]]; then
        log_warning "Monitoring environment file (.env.monitoring) not found"
        log_warning "Copy config/monitoring.env.example to .env.monitoring and configure it"
        read -p "Continue without monitoring? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
        SKIP_MONITORING=true
    fi
    
    log_success "All required files present"
}

# Backup current deployment
backup_current() {
    log_info "Creating backup of current deployment..."
    
    local backup_dir="/root/backups/crowd-due-dill-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup environment files
    if [[ -f "$PROJECT_DIR/.env" ]]; then
        cp "$PROJECT_DIR/.env" "$backup_dir/"
    fi
    
    if [[ -f "$PROJECT_DIR/.env.monitoring" ]]; then
        cp "$PROJECT_DIR/.env.monitoring" "$backup_dir/"
    fi
    
    # Export current Docker volumes (if they exist)
    if docker volume ls | grep -q "crowd_due_dill_data"; then
        log_info "Backing up application data..."
        docker run --rm -v crowd_due_dill_data:/data -v "$backup_dir":/backup alpine tar czf /backup/app_data.tar.gz -C /data .
    fi
    
    log_success "Backup created in $backup_dir"
}

# Update system and Docker
update_system() {
    log_info "Updating system packages..."
    apt-get update -qq
    apt-get upgrade -y -qq
    
    log_info "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    
    log_success "System and Docker are up to date"
}

# Set up networks
setup_networks() {
    log_info "Setting up Docker networks..."
    
    # Create proxy network if it doesn't exist
    if ! docker network ls | grep -q "proxy"; then
        docker network create proxy
        log_success "Created proxy network"
    else
        log_info "Proxy network already exists"
    fi
    
    # Create monitoring network if it doesn't exist
    if ! docker network ls | grep -q "crowd_due_dill_monitoring"; then
        docker network create crowd_due_dill_monitoring
        log_success "Created monitoring network"
    else
        log_info "Monitoring network already exists"
    fi
}

# Deploy main application
deploy_application() {
    log_info "Deploying main application..."
    
    cd "$PROJECT_DIR"
    
    # Pull latest code (if this is a git deployment)
    if [[ -d ".git" ]]; then
        log_info "Pulling latest code from Git..."
        git pull origin main
    fi
    
    # Build and deploy
    log_info "Building application..."
    docker compose -f docker-compose.production.yml build --no-cache
    
    log_info "Starting application services..."
    docker compose -f docker-compose.production.yml up -d
    
    # Wait for application to be healthy
    log_info "Waiting for application to be healthy..."
    for i in {1..30}; do
        if docker compose -f docker-compose.production.yml ps | grep -q "healthy"; then
            log_success "Application is healthy"
            break
        fi
        if [[ $i -eq 30 ]]; then
            log_error "Application failed to become healthy"
            log_info "Check logs with: docker compose -f docker-compose.production.yml logs"
            exit 1
        fi
        sleep 10
    done
}

# Deploy monitoring stack
deploy_monitoring() {
    if [[ "${SKIP_MONITORING:-false}" == "true" ]]; then
        log_warning "Skipping monitoring deployment"
        return
    fi
    
    log_info "Deploying monitoring stack..."
    
    cd "$PROJECT_DIR"
    
    # Create monitoring directories if they don't exist
    mkdir -p monitoring/prometheus monitoring/grafana/provisioning monitoring/grafana/dashboards
    
    # Deploy monitoring services
    log_info "Starting monitoring services..."
    docker compose -f docker-compose.monitoring.yml --env-file .env.monitoring up -d
    
    # Wait for monitoring services to be healthy
    log_info "Waiting for monitoring services to be healthy..."
    sleep 30
    
    # Check Grafana health
    for i in {1..20}; do
        if curl -f http://localhost:3000/api/health &>/dev/null; then
            log_success "Grafana is healthy"
            break
        fi
        if [[ $i -eq 20 ]]; then
            log_warning "Grafana health check timed out, but continuing..."
            break
        fi
        sleep 10
    done
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check main application
    log_info "Checking main application health..."
    local app_health=$(curl -s http://localhost:8001/health | jq -r '.status' 2>/dev/null || echo "unknown")
    if [[ "$app_health" == "healthy" ]]; then
        log_success "Main application is healthy"
    else
        log_warning "Main application health check failed"
    fi
    
    # Check metrics endpoint
    log_info "Checking metrics endpoint..."
    if curl -s http://localhost:8001/metrics | grep -q "component_health_status"; then
        log_success "Metrics endpoint is working"
    else
        log_warning "Metrics endpoint check failed"
    fi
    
    # Check monitoring (if deployed)
    if [[ "${SKIP_MONITORING:-false}" != "true" ]]; then
        log_info "Checking monitoring stack..."
        
        if curl -s http://localhost:9090/prometheus/api/v1/query?query=up | grep -q "success"; then
            log_success "Prometheus is responding"
        else
            log_warning "Prometheus check failed"
        fi
        
        if curl -s http://localhost:3000/api/health | grep -q "ok"; then
            log_success "Grafana is responding"
        else
            log_warning "Grafana check failed"
        fi
    fi
}

# Show deployment summary
show_summary() {
    log_info "Deployment Summary"
    echo "===================="
    
    # Show running containers
    log_info "Running containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep crowd-due-dill
    
    # Show URLs
    echo
    log_info "Application URLs:"
    if [[ -f "$PROJECT_DIR/.env" ]]; then
        local domain=$(grep "^DOMAIN_NAME=" "$PROJECT_DIR/.env" | cut -d'=' -f2)
        if [[ -n "$domain" ]]; then
            echo "  Main Application: https://$domain"
        fi
    fi
    
    if [[ -f "$PROJECT_DIR/.env.monitoring" ]]; then
        local monitoring_domain=$(grep "^MONITORING_DOMAIN=" "$PROJECT_DIR/.env.monitoring" | cut -d'=' -f2)
        if [[ -n "$monitoring_domain" ]]; then
            echo "  Monitoring (Grafana): https://$monitoring_domain"
        fi
    fi
    
    echo "  Metrics Endpoint: http://localhost:8001/metrics (internal)"
    echo "  Health Check: http://localhost:8001/health (internal)"
    
    echo
    log_success "Deployment completed successfully!"
    log_info "Logs saved to: $LOG_FILE"
}

# Cleanup function
cleanup() {
    if [[ $? -ne 0 ]]; then
        log_error "Deployment failed. Check logs: $LOG_FILE"
        log_info "To rollback, run: docker compose -f docker-compose.production.yml down"
    fi
}

# Main deployment function
main() {
    log_info "Starting Crowd Due Dill production deployment with monitoring"
    log_info "Timestamp: $(date)"
    log_info "Log file: $LOG_FILE"
    
    trap cleanup EXIT
    
    check_permissions
    check_requirements
    backup_current
    update_system
    setup_networks
    deploy_application
    deploy_monitoring
    verify_deployment
    show_summary
}

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 