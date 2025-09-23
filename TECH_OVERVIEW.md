## AgriVerse — Technical Overview, Workflow, and Runbook

### 1) Tech Stack
- Backend: FastAPI (Python), Uvicorn
- ML: TensorFlow/Keras (MobileNetV2 transfer learning)
- AI Advisory: Google Gemini 2.5 Pro (`google-generativeai`)
- Voice: gTTS (TTS), SpeechRecognition (optional STT)
- Images: Pillow
- Frontend: React + Vite + Tailwind

### 2) Directory Layout (relevant)
```
backend/
  app/
    main.py                  # FastAPI app and endpoints
    services/
      advisory_service.py    # Advisory logic + text cleaning
      disease_detector.py    # CNN inference (rice diseases)
      gemini_client.py       # Gemini ask + translate
      voice_service.py       # TTS/STT
    models/
      rice_disease_model.h5  # Trained model (after training)
      label_map.json         # Class → names (en/hi/ml)
  train_model.py             # Production training script

frontend/                    # React app (language switch + UI)
datasets/
  rice_leaf_diseases/
    Bacterial leaf blight/
    Brown spot/
    Leaf smut/
```

### 3) Core Endpoints
- POST `/detect-disease/` (multipart form: file, language, optional location)
  - Returns: prediction, confidence, advisory (in requested language)
- POST `/advisory/` (json: crop_name, location, soil_type, query, language)
  - Returns: concise advisory in requested language
- POST `/ask-gemini/` (json: query, language)
- POST `/tts/` (json: text, language) → audio/wav
- POST `/translate/` (json: text, target_language) → translated text
- GET `/languages`, GET `/health`

### 4) Language Guarantees
- `gemini_client.py` enforces: “respond ONLY in target language, plain text, no markdown”.
- `advisory_service.py` cleans residual symbols and can translate results again to ensure full target-language output.
- Frontend can re-translate existing text at runtime via `/translate` when user switches language; no data is lost.

### 5) Training Workflow
1. Place dataset under `datasets/rice_leaf_diseases/` with folders per class.
2. Run training:
   ```bash
   cd backend
   python train_model.py
   ```
3. Artifacts saved to `backend/app/models/`:
   - `rice_disease_model.h5`, `label_map.json`, plots and summary.

Model: MobileNetV2 (ImageNet), augmentation, early-stopping, fine-tuning.

### 6) Backend Runbook
Development:
```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Production:
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Environment:
```
backend/.env
  GEMINI_API_KEY=your_key
  GEMINI_MODEL=gemini-2.5-pro
```

### 7) Frontend Runbook
```bash
cd frontend
npm install
npm run dev
```
Opens on http://127.0.0.1:5173. Ensure backend is on http://127.0.0.1:8000.

### 8) Workflow (end-to-end)
1. User selects language (en/hi/ml). UI strings use i18n. 
2. User uploads image → POST `/detect-disease/` with language (and optional location/state).
3. Backend predicts disease, confidence; builds concise advisory via Gemini in target language; cleans/returns plain text.
4. UI displays text; on language switch, calls `/translate` to convert the same advisory text without refetching.
5. Optional TTS: POST `/tts/` with current text + language.

### 9) Accuracy & Safety
- Confidence threshold handled in `disease_detector.py`. Low confidence → caution message.
- Dataset-driven labels; ensure clear images.
- Advisory prompts prioritize “causes, remedies, prevention” under 200–250 words.

### 10) Extensibility
- Add classes: extend dataset, retrain → `label_map.json` updates automatically.
- Add languages: extend contexts/translations and frontend i18n.
- Add local brands: extend `advisory_service.py` map keyed by (state, disease).

### 11) Troubleshooting
- Frontend shows “Service temporarily unavailable” → check backend running and CORS.
- English leakage → ensured by `translate_text()` and stricter prompts; verify `/translate` on language switch.
- TensorFlow import issues → verify Python version and `pip install -r backend/requirements.txt`.

---
This document is the single source for stack, workflow, run commands, and integration details.


