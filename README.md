# 🌾 AgriVerse — Unified Guide

A concise, single-document guide covering architecture, setup flow, and how to run the system.

## 🏗️ Architecture (High Level)
```
AgriVerse/
├── backend/                 # FastAPI (Python)
│   ├── app/
│   │   ├── main.py         # API endpoints
│   │   ├── services/       # Advisory, ML inference, voice, Gemini
│   │   └── models/         # Runtime model files (if present)
│   ├── requirements.txt    # Python dependencies
│   ├── start_dev.py        # Dev helper
│   └── train_model.py      # Training script(s)
└── frontend/               # React + Vite
    ├── src/
    └── package.json
```

## 🚦 Setup Flow (Step-by-step)
1) Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

# env (example; set your Gemini key)
# copy .env.example to .env and edit
# GEMINI_API_KEY=your_key

# run (dev)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
# docs → http://127.0.0.1:8000/docs
```

2) Frontend
```bash
cd frontend
npm install
npm run dev
# opens → http://127.0.0.1:5173
```

## 🔌 Key API Endpoints
- POST `/detect-disease/` — multipart form with `file`, optional `language`, `location`
- POST `/advisory/` — JSON: `crop_name`, `location`, `soil_type`, `query`, `language`
- POST `/ask-gemini/` — JSON: `query`, `language`
- POST `/tts/` — JSON: `text`, `language` → audio/wav
- GET `/languages`, `/health`

## 🧰 Tips
- 422 on `/detect-disease/` means the request isn’t multipart or field isn’t named `file`
- Ensure backend on 8000 and frontend on 5173
- If TensorFlow import errors occur, check Python version and reinstall deps

## ✅ Production Notes
- Provide a valid model in `backend/app/models/` as needed by `disease_detector.py`
- Configure environment via `.env` (Gemini API key, model names)

That’s it—this README is the single source of truth for setup, architecture, and run commands.