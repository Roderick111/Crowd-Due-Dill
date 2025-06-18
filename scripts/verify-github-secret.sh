#!/bin/bash

echo "🔍 GitHub SSH Secret Verification Tool"
echo "======================================"
echo ""

# Get the server's SSH key fingerprint
echo "📡 Getting server SSH key fingerprint..."
SERVER_FINGERPRINT=$(ssh root@188.34.196.228 "ssh-keygen -lf /root/.ssh/id_ed25519.pub 2>/dev/null | awk '{print \$2}'" 2>/dev/null)

if [ -z "$SERVER_FINGERPRINT" ]; then
    echo "❌ Failed to get server key fingerprint"
    exit 1
fi

echo "✅ Server key fingerprint: $SERVER_FINGERPRINT"
echo ""

# Get the key from GitHub secret format (simulate what GitHub Actions sees)
echo "🔑 Testing GitHub secret format..."
echo ""

# Create a temporary test key from our corrected format
cat > /tmp/test_github_key << 'EOF'
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACAvdb7ZAzvfuyxKlaW/TRc3MwslpCoBP7JfDan6qfoq+wAAAJDpeNR46XjU
eAAAAAtzc2gtZWQyNTUxOQAAACAvdb7ZAzvfuyxKlaW/TRc3MwslpCoBP7JfDan6qfoq+w
AAAEC8llBhS5gEYxX1wQix9OllsUJjJ3sWwLgqysGWDWUwKy91vtkDO9+7LEqVpb9NFzcz
CyWkKgE/sl8Nqfqp+ir7AAAADHJvb3RAc2VydmVyMQE=
-----END OPENSSH PRIVATE KEY-----
EOF

# Test if the key is valid
chmod 600 /tmp/test_github_key
if ssh-keygen -lf /tmp/test_github_key >/dev/null 2>&1; then
    echo "✅ GitHub secret key format is VALID"
    
    # Get the fingerprint of our test key
    TEST_FINGERPRINT=$(ssh-keygen -lf /tmp/test_github_key 2>/dev/null | awk '{print $2}')
    echo "📋 Test key fingerprint: $TEST_FINGERPRINT"
    echo ""
    
    # Compare fingerprints
    if [ "$SERVER_FINGERPRINT" = "$TEST_FINGERPRINT" ]; then
        echo "🎯 ✅ PERFECT MATCH!"
        echo "   The GitHub secret key matches the server key exactly."
        echo "   The SSH authentication should work."
    else
        echo "❌ MISMATCH!"
        echo "   Server: $SERVER_FINGERPRINT"
        echo "   GitHub: $TEST_FINGERPRINT"
        echo "   The keys don't match - this is the problem!"
    fi
else
    echo "❌ GitHub secret key format is INVALID"
    echo "   The key format has issues that prevent SSH from using it."
    
    # Test for common issues
    echo ""
    echo "🔍 Checking for common issues..."
    
    # Check for line ending issues
    if grep -q $'\r' /tmp/test_github_key; then
        echo "   ❌ Found carriage returns (Windows line endings)"
    else
        echo "   ✅ No carriage return issues"
    fi
    
    # Check for header/footer
    if grep -q "BEGIN OPENSSH PRIVATE KEY" /tmp/test_github_key && grep -q "END OPENSSH PRIVATE KEY" /tmp/test_github_key; then
        echo "   ✅ Header and footer present"
    else
        echo "   ❌ Missing header or footer"
    fi
fi

echo ""
echo "🧪 Testing SSH connection simulation..."
# Test if we can connect using the test key
if ssh -i /tmp/test_github_key -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@188.34.196.228 "echo 'Test connection successful'" 2>/dev/null; then
    echo "✅ SSH connection test PASSED"
    echo "   The key works for SSH authentication"
else
    echo "❌ SSH connection test FAILED"
    echo "   The key cannot authenticate to the server"
fi

# Clean up
rm -f /tmp/test_github_key

echo ""
echo "🎯 CONCLUSION:"
echo "=============="
if [ "$SERVER_FINGERPRINT" = "$TEST_FINGERPRINT" ]; then
    echo "✅ Your GitHub secret is correctly formatted and should work."
    echo "   If GitHub Actions still fails, the issue might be:"
    echo "   1. Network connectivity in GitHub Actions environment"
    echo "   2. Server SSH configuration changes"
    echo "   3. GitHub Actions runner environment issues"
else
    echo "❌ Your GitHub secret doesn't match the server key."
    echo "   You need to update the GitHub secret with the correct key."
fi 