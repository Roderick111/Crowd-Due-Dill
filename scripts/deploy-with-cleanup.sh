#!/bin/bash
# Smart Deployment Script with Automatic Cleanup
# Prevents disk space accumulation during deployments

set -e

echo "🚀 Starting deployment with cleanup..."

# Check disk space before deployment
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
echo "📊 Current disk usage: ${DISK_USAGE}%"

if [ "$DISK_USAGE" -gt 80 ]; then
    echo "⚠️  High disk usage detected (${DISK_USAGE}%), running cleanup first..."
    ./scripts/cleanup-docker.sh
fi

echo "🔄 Pulling latest code..."
git pull

echo "🏗️  Building new images..."
docker compose -f docker-compose.production.yml build --no-cache

echo "🚀 Deploying containers..."
docker compose -f docker-compose.production.yml up -d

echo "🧹 Cleaning up old images and build cache..."
docker image prune -f
docker builder prune -f

echo "📊 Final disk usage:"
df -h / | grep -v "Filesystem"

echo "✅ Deployment with cleanup completed successfully!" 