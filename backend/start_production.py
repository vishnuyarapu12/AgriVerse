#!/usr/bin/env python3
"""
AgriVerse Production Backend Startup Script
Production-ready backend server startup with health checks and validation
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductionBackend:
    def __init__(self):
        self.backend_dir = Path(__file__).parent
        self.app_dir = self.backend_dir / "app"
        self.model_dir = self.app_dir / "models"
        self.env_file = self.backend_dir / ".env"
        
    def check_python_version(self) -> bool:
        """Check if Python version is compatible"""
        if sys.version_info < (3, 8):
            logger.error(f"Python 3.8+ required, found {sys.version}")
            return False
        logger.info(f"Python version: {sys.version.split()[0]}")
        return True
    
    def check_environment(self) -> bool:
        """Check and create environment configuration"""
        if not self.env_file.exists():
            logger.warning("Environment file not found, creating template...")
            with open(self.env_file, "w") as f:
                f.write("GEMINI_API_KEY=your_gemini_api_key_here\n")
                f.write("GEMINI_MODEL=gemini-2.5-pro\n")
            logger.warning("Please edit .env file and add your Gemini API key")
            return False
        
        # Check if API key is configured
        with open(self.env_file, "r") as f:
            content = f.read()
            if "your_gemini_api_key_here" in content:
                logger.warning("Please configure your Gemini API key in .env file")
                return False
        
        logger.info("Environment configuration validated")
        return True
    
    def check_dependencies(self) -> bool:
        """Check if required dependencies are installed"""
        try:
            import fastapi
            import tensorflow
            import google.generativeai
            import uvicorn
            logger.info("All required dependencies are installed")
            return True
        except ImportError as e:
            logger.error(f"Missing dependency: {e}")
            logger.error("Please install requirements: pip install -r requirements.txt")
            return False
    
    def check_model(self) -> bool:
        """Check if model files exist"""
        model_file = self.model_dir / "rice_disease_model.h5"
        label_file = self.model_dir / "label_map.json"
        
        if not self.model_dir.exists():
            logger.error(f"Model directory not found: {self.model_dir}")
            return False
        
        if not model_file.exists():
            logger.error(f"Model file not found: {model_file}")
            logger.error("Please train the model first: python train_model.py")
            return False
        
        if not label_file.exists():
            logger.error(f"Label mapping not found: {label_file}")
            logger.error("Please train the model first: python train_model.py")
            return False
        
        logger.info("Model files validated")
        return True
    
    def test_model_loading(self) -> bool:
        """Test if the model can be loaded successfully"""
        try:
            os.chdir(self.app_dir)
            sys.path.insert(0, str(self.app_dir))
            
            from services.disease_detector import predict
            from PIL import Image
            import io
            
            # Create a test image
            test_img = Image.new('RGB', (224, 224), color='green')
            buf = io.BytesIO()
            test_img.save(buf, format='JPEG')
            buf.seek(0)
            
            # Test prediction
            result = predict(buf)
            logger.info(f"Model test successful: {result['prediction']}")
            return True
            
        except Exception as e:
            logger.error(f"Model loading test failed: {e}")
            return False
        finally:
            os.chdir(self.backend_dir)
    
    def test_gemini_client(self) -> bool:
        """Test Gemini client connectivity"""
        try:
            os.chdir(self.app_dir)
            sys.path.insert(0, str(self.app_dir))
            
            from services.gemini_client import ask_gemini
            
            # Test simple query
            response = ask_gemini("Hello, this is a test", "en")
            if "error" in response.lower():
                logger.error(f"Gemini test failed: {response}")
                return False
            
            logger.info("Gemini client test successful")
            return True
            
        except Exception as e:
            logger.error(f"Gemini client test failed: {e}")
            return False
        finally:
            os.chdir(self.backend_dir)
    
    def start_server(self) -> bool:
        """Start the production server"""
        logger.info("🚀 Starting AgriVerse Production Backend")
        logger.info("=" * 50)
        
        try:
            os.chdir(self.backend_dir)
            
            # Start uvicorn server
            cmd = [
                sys.executable, "-m", "uvicorn", 
                "app.main:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--workers", "4",
                "--access-log",
                "--log-level", "info"
            ]
            
            logger.info(f"Starting server with command: {' '.join(cmd)}")
            subprocess.run(cmd)
            
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server startup failed: {e}")
            return False
        
        return True
    
    def run_health_check(self) -> bool:
        """Run health check after server startup"""
        logger.info("Running health check...")
        
        max_retries = 30
        for i in range(max_retries):
            try:
                response = requests.get("http://127.0.0.1:8000/health", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Health check passed")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(1)
            if i % 5 == 0:
                logger.info(f"Waiting for server... ({i}/{max_retries})")
        
        logger.error("Health check failed - server not responding")
        return False
    
    def run_full_validation(self) -> bool:
        """Run full system validation"""
        logger.info("🔍 Running system validation...")
        
        checks = [
            ("Python Version", self.check_python_version),
            ("Dependencies", self.check_dependencies),
            ("Environment", self.check_environment),
            ("Model Files", self.check_model),
            ("Model Loading", self.test_model_loading),
            ("Gemini Client", self.test_gemini_client)
        ]
        
        for check_name, check_func in checks:
            logger.info(f"Checking {check_name}...")
            if not check_func():
                logger.error(f"❌ {check_name} check failed")
                return False
            logger.info(f"✅ {check_name} check passed")
        
        logger.info("🎉 All validation checks passed")
        return True
    
    def start(self):
        """Main startup function"""
        logger.info("🌾 AgriVerse Production Backend Startup")
        logger.info("=" * 60)
        
        # Run validation
        if not self.run_full_validation():
            logger.error("System validation failed. Cannot start server.")
            logger.error("Please fix the issues above and try again.")
            return False
        
        # Start server
        logger.info("Starting production server...")
        logger.info("Server will be available at: http://127.0.0.1:8000")
        logger.info("API Documentation: http://127.0.0.1:8000/docs")
        logger.info("Press Ctrl+C to stop the server")
        
        return self.start_server()

def main():
    """Main entry point"""
    backend = ProductionBackend()
    
    try:
        success = backend.start()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n👋 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {e}")
        logger.exception("Full error traceback:")
        sys.exit(1)

if __name__ == "__main__":
    main()
