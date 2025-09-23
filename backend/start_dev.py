#!/usr/bin/env python3
"""
AgriVerse Development Backend Startup Script
Quick development server startup with minimal checks
"""

import os
import sys
import subprocess
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_dev_server():
    """Start development server with minimal validation"""
    logger.info("🌾 AgriVerse Development Backend")
    logger.info("=" * 40)
    
    backend_dir = Path(__file__).parent
    app_dir = backend_dir / "app"
    
    # Quick checks
    if not app_dir.exists():
        logger.error("app directory not found")
        return False
    
    # Check if model exists (optional for development)
    model_file = app_dir / "models" / "rice_disease_model.h5"
    if not model_file.exists():
        logger.warning("Model not found - some features may not work")
        logger.info("Train model with: python train_model.py")
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    try:
        logger.info("Starting development server...")
        logger.info("Server: http://127.0.0.1:8000")
        logger.info("API Docs: http://127.0.0.1:8000/docs")
        logger.info("Press Ctrl+C to stop")
        
        # Start uvicorn with reload
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app",
            "--reload",
            "--host", "127.0.0.1",
            "--port", "8000"
        ])
        
    except KeyboardInterrupt:
        logger.info("\n👋 Development server stopped")
    except Exception as e:
        logger.error(f"Server error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = start_dev_server()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n👋 Goodbye!")
        sys.exit(0)
