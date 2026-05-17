#!/usr/bin/env python3
import http.server
import socketserver
import os
from pathlib import Path

PORT = 8000
FRONTEND_DIR = Path(__file__).parent

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)
    
    def end_headers(self):
        # Prevent caching
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        super().end_headers()

if __name__ == "__main__":
    os.chdir(FRONTEND_DIR)
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"✅ Frontend server running at http://localhost:{PORT}")
        print(f"📁 Serving files from: {FRONTEND_DIR}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n❌ Server stopped")
