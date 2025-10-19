"""
Run script for the FastAPI application with hot-reload capability.
"""
import uvicorn
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from utils.config import APP_HOST, APP_PORT

if __name__ == "__main__":
    print("=" * 50)
    print("Starting Project Management API Server")
    print("=" * 50)
    print(f"Host: {APP_HOST}")
    print(f"Port: {APP_PORT}")
    print(f"Hot-reload: Enabled")
    print(f"Docs: http://localhost:{APP_PORT}/docs")
    print("=" * 50)
    
    uvicorn.run(
        "app.main:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=True,  # Enable hot-reload for development
        log_level="info"
    )

