#!/usr/bin/env python3
"""
Auto-start script that finds an available port and launches the dashboard.
"""

import socket
import os
import webbrowser
import time
import threading
from config import settings

def find_free_port(start_port=8000, max_port=8100):
    """Find a free port starting from start_port."""
    for port in range(start_port, max_port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"No free port found between {start_port} and {max_port}")

def open_browser_delayed(url, delay=3):
    """Open browser after a delay."""
    time.sleep(delay)
    print(f"\n🌐 Opening browser: {url}")
    webbrowser.open(url)

def main():
    """Main entry point."""
    print("🏛️  German Economic Insights Dashboard")
    print("=" * 50)
    
    # Find available port
    try:
        port = find_free_port(settings.PORT)
        print(f"🔍 Found available port: {port}")
        
        if port != settings.PORT:
            print(f"⚠️  Note: Using port {port} instead of {settings.PORT}")
    except RuntimeError as e:
        print(f"❌ {e}")
        return
    
    # Start browser opener thread
    url = f"http://localhost:{port}"
    browser_thread = threading.Thread(target=open_browser_delayed, args=(url,))
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start the server
    print(f"🚀 Starting server on http://localhost:{port}")
    print("   Press Ctrl+C to stop")
    
    try:
        import uvicorn
        from main import app
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            reload=settings.DEBUG,
            log_level="info" if settings.DEBUG else "warning"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()