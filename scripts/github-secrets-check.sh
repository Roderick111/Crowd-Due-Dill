#!/bin/bash

echo "🔑 GitHub Secrets Configuration Guide"
echo "======================================"
echo ""
echo "Your GitHub Actions deployment needs these 3 secrets configured:"
echo ""
echo "1. Go to: https://github.com/Roderick111/Crowd-Due-Dill/settings/secrets/actions"
echo "2. Click 'New repository secret' for each of these:"
echo ""

echo "📍 SECRET 1: HOST"
echo "   Name: HOST"
echo "   Value: 188.34.196.228"
echo ""

echo "👤 SECRET 2: USERNAME"  
echo "   Name: USERNAME"
echo "   Value: root"
echo ""

echo "🔐 SECRET 3: SSH_KEY"
echo "   Name: SSH_KEY"
echo "   Value: (Your PRIVATE key content - see below)"
echo ""

echo "🚨 CRITICAL: SSH_KEY must contain your PRIVATE key, not public key!"
echo ""
echo "To get your private key content:"
echo "   cat ~/.ssh/id_ed25519"
echo ""
echo "It should start with: -----BEGIN OPENSSH PRIVATE KEY-----"
echo "And end with: -----END OPENSSH PRIVATE KEY-----"
echo ""

echo "🧪 Testing if your local SSH key works..."
if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@188.34.196.228 "echo 'SSH test successful'" 2>/dev/null; then
    echo "✅ Your local SSH key works with the server"
    echo ""
    echo "📋 Next steps:"
    echo "1. Copy your private key: cat ~/.ssh/id_ed25519"
    echo "2. Add it as SSH_KEY secret in GitHub"
    echo "3. Trigger a new deployment"
else
    echo "❌ SSH connection failed - check your SSH key setup first"
fi

echo ""
echo "🔧 Alternative debugging:"
echo "1. Run the debug workflow manually: .github/workflows/debug-deployment.yml"
echo "2. Check GitHub Actions logs for specific error messages"
echo "3. Verify all 3 secrets are configured in GitHub repository settings" 