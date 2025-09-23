#!/usr/bin/env python3
"""
AgriVerse Farmer Advisory AI/ML System Startup Script
This script helps set up and run the complete AgriVerse system
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def print_banner():
    """Print AgriVerse banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                        🌾 AgriVerse AI 🌾                    ║
║              Complete Farmer Advisory System                 ║
║                                                              ║
║  Features:                                                   ║
║  🔬 AI Disease Detection      📊 Market Intelligence         ║
║  🎤 Voice Input/Output        🌍 Multilingual Support       ║
║  📱 Mobile Ready             🧠 Gemini AI Integration       ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    
    # Check if Node.js is available
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js: {result.stdout.strip()}")
        else:
            print("❌ Node.js not found. Please install Node.js 16+")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found. Please install Node.js 16+")
        return False
    
    print("✅ System requirements check passed!")
    return True

def setup_backend():
    """Set up the backend environment and dependencies"""
    print("\n🔧 Setting up backend...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return False
    
    os.chdir(backend_dir)
    
    # Create virtual environment if it doesn't exist
    venv_path = Path("venv")
    if not venv_path.exists():
        print("Creating Python virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        pip_path = venv_path / "Scripts" / "pip.exe"
        python_path = venv_path / "Scripts" / "python.exe"
    else:  # Unix/Linux/macOS
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    print("Installing Python dependencies...")
    subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
    
    # Create sample model if it doesn't exist
    model_path = Path("app/models/disease_model.h5")
    if not model_path.exists():
        print("Creating sample ML model...")
        subprocess.run([str(python_path), "app/create_sample_model.py"], check=True)
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        print("Creating .env file from template...")
        subprocess.run(["copy" if os.name == 'nt' else "cp", ".env.example", ".env"], shell=True)
        print("⚠️  Please edit .env file and add your Gemini API key!")
    
    os.chdir("..")
    print("✅ Backend setup completed!")
    return True

def setup_frontend():
    """Set up the frontend environment and dependencies"""
    print("\n🎨 Setting up frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        return False
    
    os.chdir(frontend_dir)
    
    # Install npm dependencies
    print("Installing Node.js dependencies...")
    subprocess.run(["npm", "install"], check=True)
    
    os.chdir("..")
    print("✅ Frontend setup completed!")
    return True

def start_backend():
    """Start the FastAPI backend server"""
    print("\n🚀 Starting backend server...")
    
    backend_dir = Path("backend")
    os.chdir(backend_dir)
    
    # Start uvicorn server
    if os.name == 'nt':  # Windows
        python_path = Path("venv/Scripts/python.exe")
    else:  # Unix/Linux/macOS
        python_path = Path("venv/bin/python")
    
    cmd = [str(python_path), "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
    
    try:
        # Start backend in background
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ Backend server started on http://127.0.0.1:8000")
        os.chdir("..")
        return process
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        os.chdir("..")
        return None

def start_frontend():
    """Start the React frontend development server"""
    print("\n🌐 Starting frontend server...")
    
    frontend_dir = Path("frontend")
    os.chdir(frontend_dir)
    
    try:
        # Start frontend in background
        process = subprocess.Popen(["npm", "run", "dev"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ Frontend server starting on http://localhost:5173")
        os.chdir("..")
        return process
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        os.chdir("..")
        return None

def open_browser():
    """Open browser to the application"""
    print("\n🌐 Opening browser...")
    time.sleep(3)  # Wait for servers to start
    try:
        webbrowser.open('http://localhost:5173')
    except Exception as e:
        print(f"Could not open browser automatically: {e}")
        print("Please manually open http://localhost:5173 in your browser")

def main():
    """Main function to orchestrate the startup process"""
    print_banner()
    
    # Check requirements
    if not check_requirements():
        print("❌ Requirements check failed. Please fix the issues and try again.")
        sys.exit(1)
    
    # Setup mode or run mode
    if len(sys.argv) > 1 and sys.argv[1] == 'setup':
        print("\n🔧 Running setup mode...")
        if setup_backend() and setup_frontend():
            print("\n✅ Setup completed successfully!")
            print("\nNext steps:")
            print("1. Edit backend/.env file and add your Gemini API key")
            print("2. Run: python start_agriverse.py")
        else:
            print("❌ Setup failed!")
            sys.exit(1)
        return
    
    # Start servers
    print("\n🚀 Starting AgriVerse system...")
    
    backend_process = start_backend()
    if not backend_process:
        print("❌ Failed to start backend server!")
        sys.exit(1)
    
    time.sleep(2)  # Give backend time to start
    
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ Failed to start frontend server!")
        backend_process.terminate()
        sys.exit(1)
    
    # Open browser
    open_browser()
    
    print(f"""
🎉 AgriVerse system is now running!

📊 Backend API: http://127.0.0.1:8000
🌐 Frontend App: http://localhost:5173
📚 API Docs: http://127.0.0.1:8000/docs

Features Available:
🔬 Disease Detection - Upload crop images for AI analysis
🌾 Crop Advisory - Get comprehensive farming guidance  
🎤 Voice Input/Output - Speak your queries in multiple languages
🌍 Multilingual Support - English, Hindi, Telugu, Tamil, Kannada
📊 Query History - Track your farming consultations
📱 Mobile Ready - Responsive design for all devices

Press Ctrl+C to stop the servers...
    """)
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping AgriVerse system...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ System stopped. Thank you for using AgriVerse!")

if __name__ == "__main__":
    main()