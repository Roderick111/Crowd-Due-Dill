#!/bin/bash

# Production Server Deployment Diagnostics
# This script helps investigate deployment issues

set -e

SERVER="188.34.196.228"
USER="root"
REPO_PATH="/root/Crowd-Due-Dill"

echo "🔍 Crowd Due Dill Production Deployment Diagnostics"
echo "=================================================="
echo ""

# Function to run commands on server
run_on_server() {
    ssh "${USER}@${SERVER}" "$1"
}

echo "📡 1. Testing SSH Connection..."
if run_on_server "echo 'SSH connection successful'"; then
    echo "✅ SSH connection working"
else
    echo "❌ SSH connection failed"
    exit 1
fi
echo ""

echo "🖥️  2. Server Environment Check..."
run_on_server "
    echo 'Server: $(hostname)'
    echo 'OS: $(uname -a)'
    echo 'Docker: $(docker --version)'
    echo 'Git: $(git --version)'
    echo 'Date: $(date)'
    echo 'Uptime: $(uptime)'
    echo 'Disk usage:'
    df -h | head -5
    echo ''
"

echo "📁 3. Repository Status Check..."
run_on_server "
    if [ -d '${REPO_PATH}' ]; then
        cd ${REPO_PATH}
        echo 'Repository exists at ${REPO_PATH}'
        echo 'Git status:'
        git status
        echo ''
        echo 'Recent commits:'
        git log --oneline -5
        echo ''
        echo 'Git remotes:'
        git remote -v
        echo ''
        echo 'Git config:'
        git config --list | grep -E '(user|url|remote)'
        echo ''
        echo 'Directory permissions:'
        ls -la
    else
        echo 'Repository does NOT exist at ${REPO_PATH}'
        echo 'Contents of /root/:'
        ls -la /root/
    fi
"

echo "🐳 4. Docker Environment Check..."
run_on_server "
    echo 'Docker containers:'
    docker ps -a
    echo ''
    echo 'Docker images:'
    docker images | head -10
    echo ''
    echo 'Docker networks:'
    docker network ls
    echo ''
    echo 'Docker volumes:'
    docker volume ls
    echo ''
    echo 'Docker system info:'
    docker system df
"

echo "⚙️  5. Production Files Check..."
run_on_server "
    cd ${REPO_PATH}
    echo 'Production docker-compose file:'
    if [ -f 'docker-compose.production.yml' ]; then
        echo '✅ docker-compose.production.yml exists'
        ls -la docker-compose.production.yml
    else
        echo '❌ docker-compose.production.yml NOT found'
    fi
    echo ''
    echo 'Environment files:'
    ls -la .env* || echo 'No .env files found'
    echo ''
    echo 'SSL certificates:'
    ls -la ssl/ || echo 'No ssl/ directory found'
    echo ''
    echo 'Nginx config:'
    ls -la nginx/ || echo 'No nginx/ directory found'
"

echo "🏥 6. Service Health Check..."
echo "Testing application health endpoint..."
if curl -f -s https://crowd-reg.beautiful-apps.com/health > /dev/null; then
    echo "✅ Health endpoint is responding"
    echo "Response:"
    curl -s https://crowd-reg.beautiful-apps.com/health | head -5
else
    echo "❌ Health endpoint is not responding"
    echo "Checking server logs..."
    run_on_server "
        cd ${REPO_PATH}
        echo 'Container logs (last 20 lines):'
        docker compose -f docker-compose.production.yml logs --tail=20
    "
fi

echo ""
echo "📊 7. GitHub Actions Simulation..."
echo "Simulating the deployment steps that GitHub Actions would run..."

run_on_server "
    cd ${REPO_PATH}
    echo 'Step 1: Git pull simulation'
    git fetch origin main
    echo 'Local commit: $(git rev-parse HEAD)'
    echo 'Remote commit: $(git rev-parse origin/main)'
    
    if [ \$(git rev-parse HEAD) != \$(git rev-parse origin/main) ]; then
        echo '⚠️  Local repository is behind remote'
        echo 'Attempting git pull...'
        git pull origin main
    else
        echo '✅ Repository is up to date'
    fi
    
    echo ''
    echo 'Step 2: Docker build test (dry-run)'
    echo 'This would run: docker compose -f docker-compose.production.yml build --no-cache'
    echo 'Current containers status:'
    docker compose -f docker-compose.production.yml ps
"

echo ""
echo "🔧 8. Potential Issues Analysis..."
echo "Common deployment failure causes:"
echo "- SSH key authentication issues"
echo "- Git repository not up to date"
echo "- Docker build failures"
echo "- Environment variables missing"
echo "- Port conflicts"
echo "- SSL certificate issues"
echo "- Insufficient disk space"

echo ""
echo "📋 9. Recommendations..."
echo "1. Check GitHub repository secrets (HOST, USERNAME, SSH_KEY)"
echo "2. Verify SSH key has correct permissions (private key, not public)"
echo "3. Ensure git remote is set to SSH (not HTTPS)"
echo "4. Check Docker logs for any build errors"
echo "5. Verify all required environment files are present"

echo ""
echo "🎯 Diagnosis Complete!"
echo "==================================================" 