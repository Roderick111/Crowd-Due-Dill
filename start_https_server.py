#!/usr/bin/env python3
"""
Simple HTTPS server for local development
This may help resolve CORS issues by serving over HTTPS instead of HTTP
"""

import http.server
import ssl
import socketserver
import os
from pathlib import Path
import urllib.parse

# Configuration
PORT = 8443
CERT_FILE = "ssl/ssl/localhost.pem"
KEY_FILE = "ssl/ssl/localhost-key.pem"

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to properly serve the web application"""
    
    def do_GET(self):
        # Parse the URL
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Handle root redirect to /web/
        if path == '/':
            self.send_response(302)
            self.send_header('Location', '/web/')
            self.end_headers()
            return
        
        # Handle /web/ paths
        if path.startswith('/web/'):
            # Remove /web prefix and serve from web directory
            web_path = path[5:]  # Remove '/web/'
            if not web_path:
                web_path = 'index.html'
            
            # Construct file path
            file_path = Path('web') / web_path
            
            # Serve the file
            if file_path.exists() and file_path.is_file():
                self.path = str(file_path)
                return super().do_GET()
            elif web_path == '' or web_path == 'index.html':
                # Serve web/index.html for /web/ requests
                self.path = 'web/index.html'
                return super().do_GET()
        
        # For all other paths, serve normally
        return super().do_GET()

def create_self_signed_cert():
    """Create a self-signed certificate for localhost"""
    try:
        import subprocess
        
        # Check if openssl is available
        result = subprocess.run(['which', 'openssl'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ OpenSSL not found. Please install it or use the Chrome CORS disable method.")
            return False
        
        # Create self-signed certificate
        print("🔐 Creating self-signed certificate for localhost...")
        
        # Generate private key
        subprocess.run([
            'openssl', 'genrsa', '-out', KEY_FILE, '2048'
        ], check=True)
        
        # Generate certificate
        subprocess.run([
            'openssl', 'req', '-new', '-x509', '-key', KEY_FILE, '-out', CERT_FILE, '-days', '365',
            '-subj', '/C=US/ST=CA/L=Local/O=Dev/CN=localhost'
        ], check=True)
        
        print("✅ Certificate created successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create certificate: {e}")
        return False
    except ImportError:
        print("❌ subprocess module not available")
        return False

def start_https_server():
    """Start HTTPS server"""
    
    # Stay in root directory to serve both root and web files
    print(f"📁 Serving from: {Path.cwd()}")
    
    # Create certificate if it doesn't exist
    if not (Path(CERT_FILE).exists() and Path(KEY_FILE).exists()):
        if not create_self_signed_cert():
            print("❌ Could not create certificate. Try the Chrome CORS disable method instead.")
            return
    
    # Set up HTTPS server with custom handler
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        # Wrap with SSL
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(CERT_FILE, KEY_FILE)
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        
        print(f"🚀 HTTPS Server starting on port {PORT}")
        print(f"🌐 Open: https://localhost:{PORT}/web/")
        print(f"🔐 Note: You'll need to accept the self-signed certificate warning")
        print(f"⚠️  Make sure Auth0 Dashboard includes: https://localhost:{PORT}/web/")
        print("🛑 Press Ctrl+C to stop")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")

if __name__ == "__main__":
    start_https_server() 