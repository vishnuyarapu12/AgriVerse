from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from app.services import gemini_client, disease_detector, voice_service, advisory_service
from pydantic import BaseModel
from typing import Optional
import io
import json
import datetime

app = FastAPI(title="Farmer Advisory API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request bodies
class AdvisoryRequest(BaseModel):
    crop_name: str
    location: str
    soil_type: str
    query: str
    language: Optional[str] = "en"

class FeedbackRequest(BaseModel):
    query_id: str
    feedback: str  # "positive" or "negative"
    comments: Optional[str] = None

class TTSRequest(BaseModel):
    text: str
    language: Optional[str] = "en"

class TranslateRequest(BaseModel):
    text: str
    target_language: str

# In-memory storage for demo (use database in production)
query_history = []
feedback_data = []

@app.get("/")
def root():
    return {
        "msg": "Farmer Advisory API v2.0 - Advanced AI Assistant for Farmers",
        "features": [
            "Disease Detection",
            "Crop Advisory", 
            "Voice Input/Output",
            "Multilingual Support",
            "Market Information",
            "Government Schemes"
        ]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.datetime.now().isoformat()}

@app.post("/detect-disease/")
async def detect_disease(file: UploadFile = File(...), language: str = Form("en"), location: str = Form(None)):
    """
    Detect rice disease from uploaded image and provide comprehensive advisory
    """
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read file into BytesIO to allow multiple reads
        contents = await file.read()
        buf = io.BytesIO(contents)
        
        # Validate image file
        if not disease_detector.validate_image_file(buf):
            raise HTTPException(status_code=400, detail="Invalid image file or file too large (>6MB)")
        
        # Reset buffer position
        buf.seek(0)
        
        # Get disease prediction
        result = disease_detector.predict(buf)
        
        # Generate advisory based on disease prediction
        if result["is_reliable"]:
            # High confidence prediction - provide detailed advisory
            if "healthy" not in result["prediction"].lower():
                advisory = advisory_service.get_disease_advisory(result["prediction"], language)
            else:
                advisory = advisory_service.get_healthy_crop_advice(result["prediction"], language)
        else:
            # Low confidence prediction - provide cautious advisory
            advisory = f"⚠️ {result['warning']}\n\n" + advisory_service.get_disease_advisory(result["prediction"], language)
        
        # Store query in history
        query_id = f"disease_{len(query_history)}"
        query_record = {
            "id": query_id,
            "type": "disease_detection",
            "filename": file.filename,
            "prediction": result["prediction"],
            "prediction_ml": result.get("prediction_ml", result["prediction"]),
            "confidence": result["confidence"],
            "is_reliable": result["is_reliable"],
            "advisory": advisory,
            "language": language,
            "location": location,
            "timestamp": datetime.datetime.now().isoformat()
        }
        query_history.append(query_record)
        
        return {
            "query_id": query_id,
            "filename": file.filename,
            "prediction": result["prediction"],
            "prediction_ml": result.get("prediction_ml", result["prediction"]),
            "confidence": result["confidence"],
            "is_reliable": result["is_reliable"],
            "confidence_threshold": result["confidence_threshold"],
            "warning": result.get("warning"),
            "top_predictions": result.get("top_predictions", []),
            "advisory": advisory,
            "language": language,
            "location": location
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/advisory/")
async def get_advisory(request: AdvisoryRequest):
    """
    Get comprehensive farming advisory based on crop, location, and query
    """
    try:
        # Generate comprehensive advisory
        advisory = advisory_service.get_comprehensive_advisory(
            crop_name=request.crop_name,
            location=request.location,
            soil_type=request.soil_type,
            query=request.query,
            language=request.language
        )
        
        # Store query in history
        query_id = f"advisory_{len(query_history)}"
        query_record = {
            "id": query_id,
            "type": "advisory",
            "crop_name": request.crop_name,
            "location": request.location,
            "soil_type": request.soil_type,
            "query": request.query,
            "advisory": advisory,
            "language": request.language,
            "timestamp": datetime.datetime.now().isoformat()
        }
        query_history.append(query_record)
        
        return {
            "query_id": query_id,
            "advisory": advisory,
            "language": request.language
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/speech-to-text/")
async def speech_to_text(audio_file: UploadFile = File(...), language: str = Form("en")):
    """
    Convert speech to text for voice queries
    """
    try:
        if not audio_file.content_type.startswith("audio/"):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        contents = await audio_file.read()
        buf = io.BytesIO(contents)
        
        text = voice_service.speech_to_text(buf, language)
        
        return {
            "text": text,
            "language": language
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/text-to-speech/")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech for voice output
    """
    try:
        audio_buffer = voice_service.text_to_speech(request.text, request.language)
        
        return StreamingResponse(
            io.BytesIO(audio_buffer),
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=response.wav"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback/")
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback for improving the advisory system
    """
    try:
        feedback_record = {
            "id": f"feedback_{len(feedback_data)}",
            "query_id": request.query_id,
            "feedback": request.feedback,
            "comments": request.comments,
            "timestamp": datetime.datetime.now().isoformat()
        }
        feedback_data.append(feedback_record)
        
        return {
            "message": "Feedback submitted successfully",
            "feedback_id": feedback_record["id"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
def get_query_history(limit: int = 10):
    """
    Get recent query history
    """
    return {
        "history": query_history[-limit:],
        "total": len(query_history)
    }

@app.get("/languages")
def get_supported_languages():
    """
    Get list of supported languages
    """
    return {
        "languages": [
            {"code": "en", "name": "English"},
            {"code": "hi", "name": "हिंदी (Hindi)"},
            {"code": "ml", "name": "മലയാളം (Malayalam)"},
            {"code": "te", "name": "తెలుగు (Telugu)"},
            {"code": "ta", "name": "தமிழ் (Tamil)"},
            {"code": "kn", "name": "ಕನ್ನಡ (Kannada)"}
        ]
    }

@app.post("/ask-gemini/")
async def ask_gemini_direct(request: dict):
    """
    Direct Gemini API endpoint for testing
    """
    try:
        query = request.get("query", "")
        language = request.get("language", "en")
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        response = gemini_client.ask_gemini(query, language)
        
        return {
            "query": query,
            "response": response,
            "language": language
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tts/")
async def text_to_speech_enhanced(request: dict):
    """
    Enhanced text-to-speech with language support
    """
    try:
        text = request.get("text", "")
        language = request.get("language", "en")
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Map language codes to TTS language codes
        tts_language_map = {
            "en": "en",
            "hi": "hi", 
            "ml": "ml",  # Malayalam support
            "te": "te",
            "ta": "ta",
            "kn": "kn"
        }
        
        tts_lang = tts_language_map.get(language, "en")
        audio_buffer = voice_service.text_to_speech(text, tts_lang)
        
        return StreamingResponse(
            io.BytesIO(audio_buffer),
            media_type="audio/wav",
            headers={
                "Content-Disposition": f"attachment; filename=response_{language}.wav",
                "Content-Length": str(len(audio_buffer))
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/translate/")
async def translate_text_endpoint(req: TranslateRequest):
    try:
        text = req.text or ""
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        translated = gemini_client.translate_text(text, req.target_language)
        return {"text": translated, "language": req.target_language}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
