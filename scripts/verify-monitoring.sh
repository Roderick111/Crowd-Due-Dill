#!/bin/bash

# Monitoring Verification Script for Crowd Due Dill
# Verifies that all monitoring components are working correctly

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "SUCCESS")
            echo -e "${GREEN}✅ ${message}${NC}"
            ;;
        "ERROR")
            echo -e "${RED}❌ ${message}${NC}"
            ;;
        "WARNING")
            echo -e "${YELLOW}⚠️  ${message}${NC}"
            ;;
        "INFO")
            echo -e "${BLUE}ℹ️  ${message}${NC}"
            ;;
    esac
}

# Test function with timeout
test_endpoint() {
    local url=$1
    local description=$2
    local expected_content=$3
    local timeout=${4:-10}
    
    print_status "INFO" "Testing $description..."
    
    if timeout $timeout curl -sf "$url" | grep -q "$expected_content"; then
        print_status "SUCCESS" "$description is working"
        return 0
    else
        print_status "ERROR" "$description failed"
        return 1
    fi
}

# Check if containers are running
check_containers() {
    print_status "INFO" "Checking container status..."
    
    local containers=(
        "crowd-due-dill-backend"
        "crowd-due-dill-prometheus"
        "crowd-due-dill-grafana"
        "crowd-due-dill-node-exporter"
        "crowd-due-dill-cadvisor"
    )
    
    local all_running=true
    
    for container in "${containers[@]}"; do
        if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
            print_status "SUCCESS" "$container is running"
        else
            print_status "ERROR" "$container is not running"
            all_running=false
        fi
    done
    
    return $all_running
}

# Check application health
check_application() {
    print_status "INFO" "Checking application health..."
    
    # Test health endpoint
    if test_endpoint "http://localhost:8001/health" "Application health check" "healthy"; then
        health_status="healthy"
    else
        health_status="unhealthy"
        return 1
    fi
    
    # Test metrics endpoint
    if test_endpoint "http://localhost:8001/metrics" "Application metrics" "component_health_status"; then
        print_status "SUCCESS" "Metrics endpoint contains component health metrics"
    else
        print_status "ERROR" "Metrics endpoint missing expected metrics"
        return 1
    fi
    
    # Test business metrics
    if curl -sf "http://localhost:8001/metrics" | grep -q "chat_messages_total"; then
        print_status "SUCCESS" "Business metrics are available"
    else
        print_status "WARNING" "Business metrics not found (this is OK if no activity yet)"
    fi
    
    # Test error metrics
    if curl -sf "http://localhost:8001/metrics" | grep -q "application_errors_total"; then
        print_status "SUCCESS" "Error tracking metrics are available"
    else
        print_status "ERROR" "Error tracking metrics not found"
        return 1
    fi
    
    return 0
}

# Check Prometheus
check_prometheus() {
    print_status "INFO" "Checking Prometheus..."
    
    # Test Prometheus health
    if test_endpoint "http://localhost:9090/prometheus/-/healthy" "Prometheus health" "Prometheus Server is Healthy"; then
        prometheus_healthy=true
    else
        prometheus_healthy=false
        return 1
    fi
    
    # Test if Prometheus can scrape our application
    print_status "INFO" "Checking if Prometheus is scraping application..."
    
    local query_url="http://localhost:9090/prometheus/api/v1/query?query=up{job=\"crowd-due-dill-api\"}"
    if curl -sf "$query_url" | grep -q '"value":\["[0-9.]*","1"\]'; then
        print_status "SUCCESS" "Prometheus is successfully scraping application"
    else
        print_status "ERROR" "Prometheus is not scraping application successfully"
        return 1
    fi
    
    # Check for component health metrics
    local component_query="http://localhost:9090/prometheus/api/v1/query?query=component_health_status"
    if curl -sf "$component_query" | grep -q "component_health_status"; then
        print_status "SUCCESS" "Component health metrics are in Prometheus"
    else
        print_status "WARNING" "Component health metrics not yet in Prometheus (may take a few minutes)"
    fi
    
    return 0
}

# Check Grafana
check_grafana() {
    print_status "INFO" "Checking Grafana..."
    
    # Test Grafana health
    if test_endpoint "http://localhost:3000/api/health" "Grafana health" "ok"; then
        grafana_healthy=true
    else
        grafana_healthy=false
        return 1
    fi
    
    # Test Grafana datasource
    print_status "INFO" "Checking Grafana datasource..."
    
    # This would require authentication, so we'll just check if the API responds
    if curl -sf "http://localhost:3000/api/datasources" &>/dev/null; then
        print_status "SUCCESS" "Grafana API is responding"
    else
        print_status "WARNING" "Grafana API not responding (may require authentication)"
    fi
    
    return 0
}

# Check system monitoring
check_system_monitoring() {
    print_status "INFO" "Checking system monitoring..."
    
    # Test Node Exporter
    if test_endpoint "http://localhost:9100/metrics" "Node Exporter" "node_cpu_seconds_total"; then
        print_status "SUCCESS" "Node Exporter is working"
    else
        print_status "ERROR" "Node Exporter is not working"
        return 1
    fi
    
    # Test cAdvisor
    if test_endpoint "http://localhost:8080/metrics" "cAdvisor" "container_cpu_usage_seconds_total"; then
        print_status "SUCCESS" "cAdvisor is working"
    else
        print_status "ERROR" "cAdvisor is not working"
        return 1
    fi
    
    return 0
}

# Generate test traffic to verify metrics collection
generate_test_traffic() {
    print_status "INFO" "Generating test traffic to verify metrics collection..."
    
    # Make a few requests to the application
    for i in {1..5}; do
        curl -sf "http://localhost:8001/health" >/dev/null || true
        curl -sf "http://localhost:8001/api" >/dev/null || true
        sleep 1
    done
    
    print_status "SUCCESS" "Test traffic generated"
    
    # Wait a moment for metrics to be updated
    sleep 5
    
    # Check if metrics reflect the activity
    if curl -sf "http://localhost:8001/metrics" | grep -q "crowdfunding_api_requests_total"; then
        print_status "SUCCESS" "HTTP request metrics are being collected"
    else
        print_status "WARNING" "HTTP request metrics not found"
    fi
}

# Main verification function
main() {
    echo "========================================"
    echo "Crowd Due Dill Monitoring Verification"
    echo "========================================"
    echo
    
    local exit_code=0
    
    # Run all checks
    check_containers || exit_code=1
    echo
    
    check_application || exit_code=1
    echo
    
    check_prometheus || exit_code=1
    echo
    
    check_grafana || exit_code=1
    echo
    
    check_system_monitoring || exit_code=1
    echo
    
    generate_test_traffic
    echo
    
    # Summary
    echo "========================================"
    echo "Verification Summary"
    echo "========================================"
    
    if [ $exit_code -eq 0 ]; then
        print_status "SUCCESS" "All monitoring components are working correctly!"
        echo
        print_status "INFO" "Next steps:"
        echo "  1. Access Grafana dashboards at your monitoring domain"
        echo "  2. Set up alert notification channels"
        echo "  3. Configure alert rules for your environment"
        echo "  4. Monitor application metrics at /metrics endpoint"
    else
        print_status "ERROR" "Some monitoring components have issues"
        echo
        print_status "INFO" "Troubleshooting:"
        echo "  1. Check container logs: docker compose logs [service-name]"
        echo "  2. Verify environment configuration"
        echo "  3. Check network connectivity between containers"
        echo "  4. Ensure all required ports are accessible"
    fi
    
    exit $exit_code
}

# Run verification if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 