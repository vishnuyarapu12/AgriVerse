# 🔧 Backend Installation Fix

If you're having issues installing backend dependencies, follow these steps:

## Step 1: Create Virtual Environment
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
```

## Step 2: Install Core Dependencies First
```bash
pip install --upgrade pip setuptools wheel
pip install fastapi uvicorn[standard] python-multipart pydantic
```

## Step 3: Install Machine Learning Libraries
```bash
pip install numpy pandas
pip install tensorflow
pip install scikit-learn joblib Pillow
```

## Step 4: Install AI/Language Processing
```bash
pip install google-generativeai python-dotenv requests
```

## Step 5: Install Voice Processing (Optional - Skip if Errors)
```bash
# Try these one by one, skip if any fail
pip install speechrecognition
pip install gtts
pip install pyttsx3

# PyAudio often fails on Windows - skip it for now
# pip install pyaudio
```

## Step 6: Install Utilities
```bash
pip install aiofiles
pip install "python-jose[cryptography]"
pip install "passlib[bcrypt]"
```

## Step 7: Install Testing Tools
```bash
pip install pytest pytest-asyncio httpx
```

## Step 8: Test Installation
```bash
# Test if FastAPI works
python -c "import fastapi; print('FastAPI OK')"

# Test if TensorFlow works
python -c "import tensorflow; print('TensorFlow OK')"

# Test if Gemini client works
python -c "import google.generativeai; print('Gemini OK')"
```

## Step 9: Create Environment File
```bash
copy .env.example .env  # Windows
# Edit .env and add your Gemini API key
```

## Step 10: Create Sample Model
```bash
python app/create_sample_model.py
```

## Step 11: Start Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Common Issues & Solutions

### PyAudio Installation Fails
- **Solution**: Skip it for now. Voice features will still work with Google TTS
- **Alternative**: Download from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

### TensorFlow Installation Fails
- **Solution**: Try: `pip install tensorflow-cpu` instead
- **Alternative**: Use `pip install tensorflow --no-cache-dir`

### Cryptography Issues
- **Solution**: Install Visual Studio Build Tools
- **Alternative**: Use `pip install --only-binary=cryptography python-jose[cryptography]`

### ImportError for Services
- **Solution**: Make sure `__init__.py` files exist in app/ and app/services/
- **Fixed**: I've already created these files

## Test Backend Without Errors
```bash
# Start without voice features
python -c "
from app.main import app
print('Backend imports successful!')
"
```

Your backend should now work! The voice features are optional and the system will work fine without them.