#!/bin/bash

# Docker Installation Script for Ubuntu
# Based on official Docker documentation
# https://docs.docker.com/engine/install/ubuntu/

set -e  # Exit on any error

echo "🐳 Installing Docker for Crowd Due Dill Production"
echo "================================================="

# Step 1: Remove old Docker packages
echo "📦 Removing old Docker packages..."
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do 
    sudo apt-get remove $pkg 2>/dev/null || true
done

# Step 2: Update package index
echo "🔄 Updating package index..."
sudo apt-get update

# Step 3: Install prerequisites
echo "📋 Installing prerequisites..."
sudo apt-get install -y ca-certificates curl

# Step 4: Add Docker's official GPG key
echo "🔑 Adding Docker's official GPG key..."
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Step 5: Add Docker repository
echo "📦 Adding Docker repository..."
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$UBUNTU_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Step 6: Update package index with Docker packages
echo "🔄 Updating package index with Docker packages..."
sudo apt-get update

# Step 7: Install Docker
echo "🐳 Installing Docker..."
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Step 8: Enable and start Docker
echo "🚀 Enabling and starting Docker service..."
sudo systemctl enable docker
sudo systemctl start docker

# Step 9: Add current user to docker group
echo "👤 Adding current user to docker group..."
sudo usermod -aG docker $USER

# Step 10: Create proxy network for nginx-proxy
echo "🌐 Creating proxy network..."
sudo docker network create proxy 2>/dev/null || echo "Proxy network already exists"

# Step 11: Test Docker installation
echo "🧪 Testing Docker installation..."
sudo docker run hello-world

# Step 12: Security setup (basic firewall)
echo "🔒 Setting up basic firewall rules..."
sudo ufw --force reset
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'
sudo ufw --force enable

# Step 13: Install additional utilities
echo "🛠️ Installing additional utilities..."
sudo apt-get install -y git htop curl wget

echo ""
echo "✅ Docker installation completed successfully!"
echo "🔄 Please log out and log back in for docker group changes to take effect"
echo "🌐 Proxy network created for nginx-proxy"
echo "🔒 Basic firewall configured (SSH, HTTP, HTTPS only)"
echo ""
echo "Next steps:"
echo "1. Clone your repository: git clone https://github.com/Roderick111/Crowd-Due-Dill.git"
echo "2. Configure your .env file with production values"
echo "3. Run: docker compose -f docker-compose.production.yml up -d"
echo ""
echo "Security notes:"
echo "- Never commit .env files to git"
echo "- Set proper file permissions: chmod 600 .env"
echo "- Regularly update system: sudo apt update && sudo apt upgrade"
echo "- Monitor logs: docker compose logs -f" 