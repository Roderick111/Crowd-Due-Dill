#!/bin/bash

echo "🔧 SSH Key Format Fixer for GitHub Actions"
echo "=========================================="
echo ""
echo "This script helps format your SSH private key correctly for GitHub secrets."
echo ""

# Get the SSH key from the server with proper formatting
echo "📡 Retrieving properly formatted SSH key from server..."
echo ""

if ssh root@188.34.196.228 "cat /root/.ssh/id_ed25519" > /tmp/github_ssh_key 2>/dev/null; then
    echo "✅ SSH key retrieved successfully"
    echo ""
    
    # Remove any potential carriage returns and ensure proper Unix line endings
    tr -d '\r' < /tmp/github_ssh_key > /tmp/github_ssh_key_clean
    
    echo "🔑 CORRECTED SSH_KEY Secret Value:"
    echo "=================================="
    cat /tmp/github_ssh_key_clean
    echo ""
    echo "=================================="
    echo ""
    echo "📋 Instructions:"
    echo "1. Copy the ENTIRE content above (from -----BEGIN to -----END)"
    echo "2. Go to: https://github.com/Roderick111/Crowd-Due-Dill/settings/secrets/actions"
    echo "3. Update the SSH_KEY secret with this corrected content"
    echo "4. Make sure to preserve all line breaks exactly as shown"
    echo ""
    echo "🚨 IMPORTANT: Do NOT copy extra spaces or characters before/after the key"
    
    # Clean up
    rm -f /tmp/github_ssh_key /tmp/github_ssh_key_clean
    
else
    echo "❌ Failed to retrieve SSH key from server"
    echo "Please ensure you can SSH to root@188.34.196.228"
fi

echo ""
echo "🔍 Alternative Method:"
echo "If the automatic retrieval fails, manually run on the server:"
echo "  ssh root@188.34.196.228"
echo "  cat /root/.ssh/id_ed25519 | tr -d '\\r'"
echo "Then copy the output to GitHub secrets." 