#!/bin/bash

# Vector Database Backup Script
# Creates timestamped backup of the local vector database

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🗄️  Vector Database Backup Script${NC}"
echo "=================================="

# Check if data directory exists
if [ ! -d "data" ]; then
    echo -e "${YELLOW}⚠️  Warning: data/ directory not found${NC}"
    exit 1
fi

# Create backup directory if it doesn't exist
mkdir -p backups/database

# Generate timestamp
timestamp=$(date +"%Y%m%d_%H%M%S")
backup_file="vector_db_backup_${timestamp}.tar.gz"

echo -e "${BLUE}📦 Creating backup: ${backup_file}${NC}"

# Create backup
tar -czf "${backup_file}" -C data/ .

# Move to backup directory
mv "${backup_file}" backups/database/

# Get file size
backup_size=$(ls -lh "backups/database/${backup_file}" | awk '{print $5}')

echo -e "${GREEN}✅ Backup created successfully!${NC}"
echo -e "${GREEN}📁 Location: backups/database/${backup_file}${NC}"
echo -e "${GREEN}📊 Size: ${backup_size}${NC}"

# Verify backup contents
echo -e "${BLUE}🔍 Verifying backup contents...${NC}"
echo "First 10 files in backup:"
tar -tzf "backups/database/${backup_file}" | head -10

# List all backups
echo -e "${BLUE}📋 All database backups:${NC}"
ls -lh backups/database/vector_db_backup_*.tar.gz 2>/dev/null || echo "No previous backups found"

echo -e "${GREEN}🎉 Backup process completed!${NC}" 