# 🌾 AgriVerse - Complete Farmer Advisory AI/ML System

A comprehensive AI-powered agricultural advisory system that provides crop disease detection, farming guidance, market intelligence, and voice-enabled multilingual support for farmers.

![AgriVerse Banner](https://img.shields.io/badge/AgriVerse-AI%20Farmer%20Advisory-green?style=for-the-badge&logo=leaf)

## ✨ Features

### 🔬 **Disease Detection**
- Upload crop/leaf images for AI-powered disease identification
- CNN-based machine learning model with confidence scoring
- Detailed treatment recommendations and preventive measures
- Support for major crops (Tomato, Potato, Corn, Apple, Grape)

### 🌾 **Comprehensive Advisory System**
- Crop-specific guidance based on location and soil type
- Weather-based farming recommendations
- Market price intelligence and selling strategies
- Government schemes and subsidies information
- Pest management and nutrition advice

### 🎤 **Voice Input/Output**
- Speech-to-text for voice queries
- Text-to-speech for audio responses
- Works in multiple languages (English, Hindi, Telugu, Tamil, Kannada)
- Browser-based speech recognition

### 🌍 **Multilingual Support**
- Full UI translation in 5 languages
- Voice input/output in regional languages
- Culturally appropriate farming advice
- Language-specific government scheme information

### 📱 **Modern UI/UX**
- Responsive design for mobile and desktop
- Beautiful animations with Framer Motion
- Intuitive navigation with tab-based interface
- Real-time feedback and loading states
- Query history tracking

### 🔄 **Feedback System**
- User feedback collection (thumbs up/down)
- Continuous improvement of AI recommendations
- Query history and analytics

## 🏗️ Architecture

```
AgriVerse/
├── backend/                 # FastAPI Python Backend
│   ├── app/
│   │   ├── main.py         # FastAPI application
│   │   ├── models/         # ML models and data
│   │   └── services/       # Business logic services
│   ├── requirements.txt    # Python dependencies
│   └── .env.example       # Environment configuration
├── frontend/               # React + Tailwind Frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── contexts/       # Language and state management
│   │   └── App.jsx        # Main application
│   └── package.json       # Node.js dependencies
├── datasets/              # Training data and samples
└── start_agriverse.py    # Automated startup script
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Gemini API Key** (Google AI)

### 1️⃣ One-Click Setup

```bash
# Clone or download the project
cd AgriVerse

# Run automated setup
python start_agriverse.py setup
```

### 2️⃣ Configure Environment

Edit `backend/.env` file:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-pro
```

### 3️⃣ Start the System

```bash
python start_agriverse.py
```

The system will automatically:
- Start the backend API server (Port 8000)
- Start the frontend development server (Port 5173)
- Open your browser to the application

## 🔧 Manual Setup (Advanced Users)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create sample ML model
python app/create_sample_model.py

# Configure environment
cp .env.example .env
# Edit .env and add your Gemini API key

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 📡 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/detect-disease/` | POST | Upload image for disease detection |
| `/advisory/` | POST | Get comprehensive farming advice |
| `/speech-to-text/` | POST | Convert voice to text |
| `/text-to-speech/` | POST | Convert text to speech |
| `/feedback/` | POST | Submit user feedback |
| `/history` | GET | Retrieve query history |
| `/languages` | GET | Get supported languages |

### API Documentation

Visit `http://127.0.0.1:8000/docs` for interactive API documentation.

## 🎯 Usage Guide

### Disease Detection
1. Navigate to the **Disease Detection** tab
2. Upload a crop/leaf image or use voice to describe the problem
3. Select your preferred language
4. Click **Analyze** to get AI-powered diagnosis
5. Review the disease prediction, confidence score, and treatment advice
6. Listen to the audio response if needed

### Crop Advisory
1. Go to the **Crop Advisory** tab
2. Fill in crop name, location, and soil type
3. Ask your farming question (text or voice)
4. Get comprehensive advice including:
   - Specific solutions to your problem
   - Crop management recommendations
   - Weather considerations
   - Market intelligence
   - Government schemes

### Voice Features
1. Visit the **Voice Settings** tab to test capabilities
2. Use the 🎤 buttons throughout the app for voice input
3. Click 🔊 to hear responses in your language

## 🌍 Supported Languages

- **English** - Full support
- **हिंदी (Hindi)** - Full support  
- **తెలుగు (Telugu)** - Full support
- **தமிழ் (Tamil)** - Voice and basic UI
- **ಕನ್ನಡ (Kannada)** - Voice and basic UI

## 📊 Technical Stack

### Backend
- **FastAPI** - Modern Python web framework
- **TensorFlow** - Machine learning models
- **Google Gemini AI** - Large language model
- **Google TTS/STT** - Voice processing
- **Pillow** - Image processing
- **Uvicorn** - ASGI server

### Frontend
- **React 19** - User interface framework
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Animations
- **React Hot Toast** - Notifications
- **Vite** - Build tool and development server

### ML/AI Components
- **CNN Model** - Crop disease classification
- **Gemini Pro** - Natural language processing
- **Speech Recognition API** - Voice input
- **Google TTS** - Voice output

## 📱 Mobile Support

The application is fully responsive and works on:
- **Mobile browsers** (Chrome, Safari, Firefox)
- **Tablets** (iPad, Android tablets)
- **Desktop** (All major browsers)

Voice features work best on:
- Chrome (Android/Desktop)
- Safari (iOS/macOS)
- Edge (Windows/Android)

## 🔒 Privacy & Security

- **No data storage** - Queries are processed in real-time
- **Local processing** - Images processed server-side, not stored
- **API keys** - Securely managed through environment variables
- **HTTPS ready** - Production deployment supports SSL
- **CORS configured** - Secure cross-origin requests

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google AI** - Gemini language model
- **PlantVillage Dataset** - Disease detection training data
- **React Team** - Frontend framework
- **FastAPI** - Backend framework
- **Tailwind CSS** - Styling framework

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
- Check Python version (3.8+ required)
- Ensure all dependencies are installed
- Verify Gemini API key is set in .env

**Frontend won't start:**
- Check Node.js version (16+ required)
- Run `npm install` in frontend directory
- Clear npm cache: `npm cache clean --force`

**Voice features not working:**
- Use Chrome, Safari, or Edge browser
- Allow microphone permissions
- Check internet connection for TTS

**Model predictions are poor:**
- The sample model is for demonstration
- Train with real crop disease data for production
- Ensure uploaded images are clear and well-lit

### Getting Help

- **Issues**: Open an issue on GitHub
- **Discussions**: Join our community discussions
- **Email**: Contact the development team

## 🔮 Future Enhancements

- [ ] Real-time weather integration
- [ ] Satellite imagery analysis
- [ ] IoT sensor data integration
- [ ] Offline mobile app (React Native/Flutter)
- [ ] Blockchain-based crop certification
- [ ] Advanced market prediction models
- [ ] Community features for farmers
- [ ] Integration with agricultural databases

---

**Built with ❤️ for farmers worldwide** 🌾

[![GitHub stars](https://img.shields.io/github/stars/yourusername/agriverse?style=social)](https://github.com/yourusername/agriverse)
[![GitHub forks](https://img.shields.io/github/forks/yourusername/agriverse?style=social)](https://github.com/yourusername/agriverse)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)