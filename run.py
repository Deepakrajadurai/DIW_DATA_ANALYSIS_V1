#!/usr/bin/env python3
"""
Simple script to run the German Economic Insights Dashboard.
This script handles initial setup and launches the FastAPI server.
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path
from config import settings

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required.")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        import google.generativeai
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e.name}")
        print("   Please run: pip install -r requirements.txt")
        return False

def check_api_key():
    """Check if Gemini API key is configured."""
    if not settings.GEMINI_API_KEY:
        print("❌ Gemini API key not found!")
        print("   Please set GEMINI_API_KEY in your .env file")
        print("   Get your API key from: https://makersuite.google.com/app/apikey")
        return False
    print("✅ Gemini API key configured")
    return True

def create_directories():
    """Create necessary directories."""
    directories = ["uploads", "static", "templates", "services", "data"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Directories created")

def check_env_file():
    """Check if .env file exists and create example if not."""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        
        # Create example .env file
        example_env = """# German Economic Dashboard Environment Variables
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///./dashboard.db
DEBUG=True
HOST=0.0.0.0
PORT=8000
"""
        with open(".env.example", "w") as f:
            f.write(example_env)
        
        print("   Created .env.example file for you")
        print("   Please copy it to .env and add your Gemini API key")
        print("   cp .env.example .env")
        return False
    
    print("✅ .env file found")
    return True

def start_server():
    """Start the FastAPI server."""
    print(f"\n🚀 Starting server on http://{settings.HOST}:{settings.PORT}")
    print("   Press Ctrl+C to stop the server")
    
    try:
        # Open browser after a short delay
        if not settings.DEBUG:
            import threading
            def open_browser():
                import time
                time.sleep(2)
                webbrowser.open(f"http://localhost:{settings.PORT}")
            
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
        
        # Start the server
        import uvicorn
        uvicorn.run(
            "main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level="info" if settings.DEBUG else "warning"
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

def main():
    """Main entry point."""
    print("🏛️  German Economic Insights Dashboard")
    print("=" * 50)
    
    # Run all checks
    check_python_version()
    
    if not check_env_file():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    if not check_api_key():
        print("\n💡 You can still run the dashboard without an API key,")
        print("   but AI features will be disabled.")
        response = input("   Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    create_directories()
    
    print("\n✅ All checks passed!")
    print(f"   Database: {settings.DATABASE_PATH}")
    print(f"   Debug mode: {settings.DEBUG}")
    
    # Start the server
    start_server()

if __name__ == "__main__":
    main()