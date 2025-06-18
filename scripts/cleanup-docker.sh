#!/bin/bash
# Docker Cleanup Script for Crowd Due Dill Production Server
# Removes unused Docker images, build cache, and containers to free disk space
# Run this monthly or when disk usage gets high

set -e

echo "🧹 Starting Docker cleanup..."

echo "📊 Current disk usage:"
df -h / | grep -v "Filesystem"

echo "📊 Current Docker usage:"
docker system df

echo ""
echo "🗑️  Cleaning up..."

# Remove dangling images (untagged)
echo "Removing dangling images..."
docker image prune -f

# Remove unused images (not referenced by any container)
echo "Removing unused images..."
docker image prune -a -f

# Remove build cache
echo "Removing build cache..."
docker builder prune -a -f

# Remove stopped containers (if any)
echo "Removing stopped containers..."
docker container prune -f

# Remove unused networks
echo "Removing unused networks..."
docker network prune -f

# Remove unused volumes (BE CAREFUL - this could remove data!)
echo "⚠️  Checking for unused volumes..."
UNUSED_VOLUMES=$(docker volume ls -qf dangling=true)
if [ -n "$UNUSED_VOLUMES" ]; then
    echo "Found unused volumes: $UNUSED_VOLUMES"
    echo "⚠️  NOT removing volumes automatically (could contain data)"
    echo "Run 'docker volume prune -f' manually if you're sure they're safe to remove"
else
    echo "✅ No unused volumes found"
fi

echo ""
echo "✅ Cleanup complete!"

echo "📊 Final disk usage:"
df -h / | grep -v "Filesystem"

echo "📊 Final Docker usage:"
docker system df

echo ""
echo "🎉 Docker cleanup finished successfully!" 