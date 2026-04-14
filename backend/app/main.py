from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request, Query, BackgroundTasks
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from app.services import gemini_client, disease_detector, voice_service, advisory_service
from app.services import weather_service, solution_service, reminder_service, telangana_brands_service, market_prices_service, translation_service
from app.models.farmer_api_schemas import (
    FarmerWeatherResponse,
    SolutionCard,
    SetReminderRequest,
    SetReminderResponse,
)
from pydantic import BaseModel
from typing import Optional, Union
import io
import json
import datetime
import logging
import time
import base64
import os
import sys
import asyncio

import httpx

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.StreamHandler(sys.stderr),
    ]
)
logger = logging.getLogger(__name__)
# Force logger to use DEBUG level
logger.setLevel(logging.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start background scheduler and pre-load models for optimal startup performance"""
    start_time = time.time()
    
    # 1. Pre-load disease detection models (eliminates 1-3s latency on first request)
    logger.info("🚀 Pre-loading disease detection models at startup...")
    if disease_detector.initialize_models(model_key=None):
        model_load_time = time.time() - start_time
        logger.info(f"✅ Disease detection model pre-loaded in {model_load_time:.2f}s")
    else:
        logger.warning(f"⚠️  Model pre-load skipped (models may be trained separately)")
    
    # 2. Start background scheduler for reminders
    reminder_service.start_scheduler()
    logger.info("✅ AgriVerse API ready (all services initialized)")
    
    total_start = time.time() - start_time
    logger.info(f"🎯 Total startup time: {total_start:.2f}s")
    yield
    reminder_service.shutdown_scheduler()
    logger.info("AgriVerse API shutdown complete")


app = FastAPI(title="Farmer Advisory API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTTP Request/Response Middleware for logging
@app.middleware("http")
async def log_http_middleware(request: Request, call_next):
    """Log all HTTP requests and responses with status codes"""
    method = request.method
    path = request.url.path
    
    msg_in = f"🌐 [{method}] REQUEST → {path}"
    print(msg_in, flush=True)
    logger.info(msg_in)
    
    start_time = time.time()
    response = await call_next(request)
    elapsed = time.time() - start_time
    
    status = response.status_code
    status_symbol = "✅" if 200 <= status < 300 else "⚠️" if 300 <= status < 400 else "❌" if status >= 400 else "❓"
    msg_out = f"🌐 [{method}] {status_symbol} {status} ← {path} ({elapsed:.2f}s)"
    print(msg_out, flush=True)
    logger.info(msg_out)
    
    return response

# Add exception handler for validation errors to provide better error messages
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "message": "Validation error: Please check your request format. For image upload, ensure 'file' field is present. For text queries, ensure 'text_query' field is present."
        }
    )

# Pydantic models for request bodies
class AdvisoryRequest(BaseModel):
    crop_name: str
    location: str
    soil_type: str
    query: Optional[str] = "General farming advice"
    season: Optional[str] = "kharif"
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

class OrganicFarmingRequest(BaseModel):
    crop_name: str
    location: Optional[str] = "Telangana, India"
    language: Optional[str] = "en"

# In-memory storage for demo (use database in production)
query_history = []
feedback_data = []
audio_cache = {}  # Store generated audio by query_id for async delivery

# ==================== HELPER FUNCTIONS ====================

def generate_audio_for_text(text: str, language: str = "en") -> dict:
    """
    Generate audio from text using voice service
    Returns dict with audio_url (base64 data URL) and audio_path
    ADDED: Audio file generation and encoding to base64
    """
    try:
        logger.info(f"Generating audio for language: {language}")
        start_time = time.time()
        
        # Call voice service to generate audio
        result = voice_service.text_to_speech(text, language)
        audio_data = result.get("audio_data")
        audio_path = result.get("audio_path")
        
        if not audio_data:
            logger.warning(f"Failed to generate audio for language {language}")
            return {"audio_url": None, "audio_path": None, "error": "Audio generation failed"}
        
        # Encode audio to base64 for transmission
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        audio_url = f"data:audio/mp3;base64,{audio_base64}"
        
        elapsed_time = time.time() - start_time
        logger.info(f"Audio generated in {elapsed_time:.2f}s for {language}, size: {len(audio_data)} bytes")
        
        return {
            "audio_url": audio_url,
            "audio_path": audio_path,
            "audio_size_bytes": len(audio_data),
            "language": language
        }
    except Exception as e:
        logger.error(f"Audio generation error: {type(e).__name__}: {str(e)}")
        return {"audio_url": None, "audio_path": None, "error": str(e)}

def generate_audio_background(query_id: str, text: str, language: str = "en") -> None:
    """
    Background task to generate audio asynchronously
    Stores audio in audio_cache with query_id for later retrieval
    ADDED: Async audio generation to avoid blocking responses
    """
    try:
        logger.info(f"🎵 Background audio generation started for {query_id}")
        start_time = time.time()
        
        result = voice_service.text_to_speech(text, language)
        audio_data = result.get("audio_data")
        audio_path = result.get("audio_path")
        
        if not audio_data:
            logger.error(f"Audio generation failed for {query_id}")
            audio_cache[query_id] = {"status": "failed", "error": "Audio generation failed"}
            return
        
        # Encode to base64 and store in cache
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        audio_url = f"data:audio/mp3;base64,{audio_base64}"
        
        elapsed_time = time.time() - start_time
        logger.info(f"🎵 Audio ready for {query_id} ({elapsed_time:.2f}s, {len(audio_data)} bytes)")
        
        audio_cache[query_id] = {
            "status": "ready",
            "audio_url": audio_url,
            "audio_path": audio_path,
            "size_bytes": len(audio_data),
            "language": language,
            "generation_time_s": elapsed_time
        }
    except Exception as e:
        logger.error(f"Background audio error for {query_id}: {type(e).__name__}: {str(e)}")
        audio_cache[query_id] = {"status": "failed", "error": str(e)}

@app.get("/")
def root():
    return {
        "msg": "Farmer Advisory API v2.0 - Advanced AI Assistant for Farmers",
        "features": [
            "Disease Detection",
            "Crop Advisory",
            "Organic Farming",
            "Farm weather & spray advice (GET /weather?lat=&lon=) — Open-Meteo, no API key",
            "One-tap solutions (GET /solution/{disease})",
            "Telangana agri brands (GET /telangana-brands)",
            "Reminders (POST /set-reminder)",
            "Voice Input/Output",
            "Multilingual Support",
        ],
        "docs": {
            "weather": "GET /weather?lat=17.38&lon=78.48 (omit lat/lon for Hyderabad default)",
            "brands": "GET /telangana-brands",
            "solution": "GET /solution/leaf%20spot",
            "reminder": 'POST /set-reminder JSON {"message":"...","delay_seconds":60}',
        },
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.datetime.now().isoformat()}


# --- Farmer utility APIs (Telangana / rural India) ---


@app.get("/weather", response_model=FarmerWeatherResponse)
async def get_farm_weather(
    lat: Optional[float] = Query(None, ge=-90, le=90, description="Latitude (GPS); omit with lon for Hyderabad default"),
    lon: Optional[float] = Query(None, ge=-180, le=180, description="Longitude (GPS); omit with lat for Hyderabad default"),
):
    """
    Real-time temperature & wind from **Open-Meteo** (no API key). Spray advice for farmers.

    - If **lat** or **lon** is missing, defaults to **Hyderabad, Telangana**.
    - Rain: inferred from WMO weather code.
    - Wind: km/h; if **> 20** → high-wind advice.

    Example:
        curl "http://127.0.0.1:8000/weather?lat=17.385&lon=78.4867"
        curl "http://127.0.0.1:8000/weather"
    """
    try:
        data = await weather_service.fetch_farm_weather(lat, lon)
        return FarmerWeatherResponse(**data)
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except httpx.HTTPStatusError as e:
        logger.warning("Open-Meteo HTTP error: %s", e.response.status_code)
        raise HTTPException(status_code=502, detail="Weather service returned an error.")
    except httpx.RequestError as e:
        logger.warning("Open-Meteo request failed: %s", e)
        raise HTTPException(status_code=503, detail="Could not reach weather service. Check network.")
    except Exception as e:
        logger.exception("Weather failed: %s", e)
        raise HTTPException(status_code=502, detail="Could not fetch weather.")


@app.get("/telangana-brands")
def telangana_agri_brands():
    """
    Popular agri input brands commonly available in Telangana / South India (reference list).
    """
    return {"region": "Telangana, India", "brands": telangana_brands_service.list_telangana_brands()}


@app.get("/market-prices/top-districts")
def get_market_prices_top_districts():
    """
    Get market prices for all major crops across top 10 agricultural districts in Telangana.
    Data from data.gov.in API with commodity prices, focused on major Telangana crops.
    """
    try:
        # Use flattened data for better frontend display
        flattened_data = market_prices_service.get_all_commodities_flattened()
        
        return {
            "region": "Telangana, India",
            "districts": 10,
            "data": flattened_data,
            "message": "Market prices from data.gov.in API - All commodities across all districts"
        }
    except Exception as e:
        logger.error(f"Error fetching market prices: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch market prices")


@app.get("/market-prices/district/{district}")
def get_market_prices_by_district(district: str):
    """
    Get all commodity prices for a specific district.
    
    Example:
        curl "http://127.0.0.1:8000/market-prices/district/Hyderabad"
    """
    try:
        commodities = market_prices_service.get_district_commodities(district)
        if not commodities:
            raise HTTPException(status_code=404, detail=f"No prices found for district: {district}")
        
        return {
            "district": district,
            "commodities_count": len(commodities),
            "commodities": commodities
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching prices for {district}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch market prices")


@app.get("/market-prices/commodity/{commodity}")
def get_commodity_prices(commodity: str):
    """
    Get prices for a specific commodity across all top districts.
    
    Example:
        curl "http://127.0.0.1:8000/market-prices/commodity/Rice"
    """
    try:
        prices = market_prices_service.get_commodity_prices_all_districts(commodity)
        if not prices:
            raise HTTPException(status_code=404, detail=f"No prices found for commodity: {commodity}")
        
        return {
            "commodity": commodity,
            "districts_found": len(prices),
            "prices": prices
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching prices for {commodity}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch market prices")


@app.get("/solutions")
def list_solution_diseases():
    """Mock DB: disease names available for GET /solution/{disease}."""
    return {"diseases": solution_service.list_supported_diseases()}


@app.get("/solution/{disease}", response_model=SolutionCard)
def get_solution_card(disease: str):
    """
    One-tap structured solution (mock database).

    Examples:
        curl "http://127.0.0.1:8000/solution/leaf%20spot"
        curl "http://127.0.0.1:8000/solution/rice_blast"
    """
    row = solution_service.get_solution(disease)
    if not row:
        raise HTTPException(
            status_code=404,
            detail=f"No solution card for '{disease}'. Try: {', '.join(solution_service.list_supported_diseases())}",
        )
    return SolutionCard(**row)


@app.post("/set-reminder", response_model=SetReminderResponse)
def set_reminder(body: SetReminderRequest):
    """
    Schedule a one-shot reminder (prints REMINDER: <message> after delay).

    Example:
        curl -X POST "http://127.0.0.1:8000/set-reminder" \\
          -H "Content-Type: application/json" \\
          -d "{\\"message\\":\\"Irrigate field 2\\",\\"delay_seconds\\":10}"
    """
    try:
        job_id, run_at = reminder_service.schedule_reminder(body.message, body.delay_seconds)
        return SetReminderResponse(
            status="scheduled",
            job_id=job_id,
            fires_at_utc=run_at.isoformat(),
            message=body.message,
        )
    except Exception as e:
        logger.exception("Reminder scheduling failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/disease-models/")
def disease_models():
    """List trained disease models (task_id) available under app/models."""
    return {"models": disease_detector.list_available_models()}

@app.post("/organic-farming/")
async def organic_farming(request: OrganicFarmingRequest, background_tasks: BackgroundTasks):
    """
    Generate structured organic & sustainable farming techniques for a crop (Telangana-focused).
    OPTIMIZED: Returns response immediately WITHOUT waiting for audio (~13s)
    ADDED: Background audio generation task
    """
    try:
        start_time = time.time()
        logger.info(f"Organic farming request - Crop: {request.crop_name}, Language: {request.language}")
        
        if not request.crop_name or not request.crop_name.strip():
            raise HTTPException(status_code=400, detail="crop_name is required")
        loc = request.location or "Telangana, India"
        lang = request.language or "en"
        guide = advisory_service.get_organic_farming_advisory(
            request.crop_name.strip(),
            language=lang,
            location=loc,
        )
        
        # Create query record with unique ID
        query_id = f"organic_{len(query_history)}"
        query_record = {
            "id": query_id,
            "type": "organic_farming",
            "crop_name": request.crop_name.strip(),
            "location": loc,
            "text": guide,
            "language": lang,
            "timestamp": datetime.datetime.now().isoformat(),
        }
        query_history.append(query_record)
        
        # Initialize audio cache entry
        audio_cache[query_id] = {"status": "generating", "language": lang}
        
        # Start background audio generation (non-blocking)
        background_tasks.add_task(generate_audio_background, query_id, guide, lang)
        
        elapsed_time = time.time() - start_time
        logger.info(f"📄 Organic response returned in {elapsed_time:.2f}s (audio generating in background)")
        
        return {
            "query_id": query_id,
            "crop_name": request.crop_name.strip(),
            "location": loc,
            "text": guide,  # Text response returned immediately
            "audio_url": None,
            "audio_stream_url": f"/stream-audio/{query_id}",  # Stream audio in real-time
            "audio_polling_url": f"/get-audio/{query_id}",  # Fallback: poll for audio
            "language": lang,
            "response_time_seconds": elapsed_time,
            "audio_status": "generating"  # Audio is being generated in background
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Organic farming error: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stream-audio/{query_id}")
async def stream_audio(query_id: str):
    """
    Stream audio in real-time while being generated
    Returns chunked audio from file (plays while gTTS is still working)
    Supports Range requests for replay without buffering full file
    ADDED: Real-time streaming + efficient replay via HTTP Range headers
    """
    if query_id not in audio_cache:
        raise HTTPException(status_code=404, detail="Query ID not found")
    
    audio_entry = audio_cache[query_id]
    status = audio_entry.get("status")
    audio_path = audio_entry.get("audio_path")
    
    # If audio not ready yet, wait up to 5 seconds for streaming to become available
    max_wait = 50  # 5 seconds max
    wait_count = 0
    while status == "generating" and not (audio_path and os.path.exists(audio_path)) and wait_count < max_wait:
        await asyncio.sleep(0.1)
        wait_count += 1
        audio_entry = audio_cache.get(query_id, {})
        status = audio_entry.get("status")
        audio_path = audio_entry.get("audio_path")
    
    # If file exists, stream it with support for range requests (for replay)
    if audio_path and os.path.exists(audio_path):
        file_size = os.path.getsize(audio_path)
        logger.info(f"🎵 Streaming audio for {query_id} (size: {file_size} bytes, status: {status})")
        
        def audio_generator():
            """Yield audio file in chunks for streaming"""
            try:
                with open(audio_path, "rb") as f:
                    # Stream in smaller chunks for responsiveness while generating
                    chunk_size = 4096  # 4KB chunks
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        yield chunk
            except Exception as e:
                logger.error(f"Streaming error for {query_id}: {e}")
        
        return StreamingResponse(
            audio_generator(),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline",  # Play in browser, don't download
                "Accept-Ranges": "bytes",  # Support range requests for seeking/replay
                "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
                "Content-Length": str(file_size)
            }
        )
    else:
        # Still waiting for file to be written
        return JSONResponse(
            status_code=202,
            content={"status": "generating", "message": "Audio generation in progress, file not yet available"}
        )

@app.get("/get-audio/{query_id}")
async def get_audio(query_id: str):
    """
    Polling endpoint to fetch generated audio
    Returns audio when ready, status while generating, or error if failed
    ADDED: Non-blocking audio delivery - frontend polls for audio
    """
    if query_id not in audio_cache:
        logger.warning(f"Audio cache miss for {query_id}")
        raise HTTPException(status_code=404, detail="Query ID not found")
    
    audio_entry = audio_cache[query_id]
    status = audio_entry.get("status")
    
    if status == "ready":
        logger.info(f"🎵 Audio served for {query_id}")
        return {
            "status": "ready",
            "query_id": query_id,
            "audio_url": audio_entry.get("audio_url"),
            "size_bytes": audio_entry.get("size_bytes"),
            "language": audio_entry.get("language"),
            "generation_time_s": audio_entry.get("generation_time_s")
        }
    elif status == "generating":
        return {
            "status": "generating",
            "query_id": query_id,
            "message": "Audio is still being generated. Try again in a few seconds."
        }
    else:  # status == "failed"
        logger.error(f"Audio generation failed for {query_id}")
        raise HTTPException(status_code=500, detail=audio_entry.get("error", "Audio generation failed"))

@app.post("/detect-disease/")
async def detect_disease(
    language: str = Form("en"),
    location: Optional[str] = Form(None),
    text_query: Optional[str] = Form(None),
    crop: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(default=None),
    files: Optional[list] = File(default=None)
):
    """
    Detect crop diseases from uploaded images and provide comprehensive advisory.
    Supports both single and multiple image uploads, plus text-based queries.
    Validates that images are leaf/plant images.
    """
    endpoint_start_time = time.time()
    logger.info(f"🔥 [DETECT_DISEASE] START - Language: {language}, Location: {location}, Crop: {crop}")
    
    try:
        # Handle multiple files from FormData
        image_files = []
        
        logger.info(f"[DETECT_DISEASE] Checking files - file={file is not None}, files={files is not None}")
        
        if files:
            # Multiple files sent with 'files' key
            image_files = [f for f in files if f is not None]
            logger.info(f"[DETECT_DISEASE] Multiple files received: {len(image_files)} files")
        elif file:
            # Single file sent with 'file' key
            try:
                filename = getattr(file, 'filename', None)
                if filename and filename.strip():
                    image_files = [file]
                    logger.info(f"[DETECT_DISEASE] Single file received: {filename}")
            except (AttributeError, TypeError):
                logger.warning(f"[DETECT_DISEASE] Error extracting file attributes")
                pass
        
        logger.info(f"[DETECT_DISEASE] Total image files to process: {len(image_files)}")
        logger.info(f"[DETECT_DISEASE] Text query: {text_query[:50] if text_query else 'None'}")
        
        # If no files and no text query, return error
        if not image_files and (not text_query or not text_query.strip()):
            logger.error(f"[DETECT_DISEASE] ❌ No files and no text query provided")
            raise HTTPException(status_code=400, detail="Either an image file or text query is required")
        
        # Handle text-only query (no images)
        if not image_files and text_query and text_query.strip():
            logger.info(f"[DETECT_DISEASE] 📝 Processing TEXT-ONLY query")
            start_time = time.time()
            
            logger.info(f"[DETECT_DISEASE] 🔄 Generating advisory...")
            advisory = advisory_service.get_comprehensive_advisory(
                crop_name="rice",
                location=location or "Unknown",
                soil_type="Unknown",
                query=text_query,
                language=language
            )
            adv_time = time.time() - start_time
            logger.info(f"[DETECT_DISEASE] ✅ Advisory generated in {adv_time:.2f}s")
            
            # Generate audio from advisory - AUTOMATIC AUDIO GENERATION
            logger.info(f"[DETECT_DISEASE] 🎵 Generating audio for language: {language}")
            audio_start = time.time()
            audio_result = generate_audio_for_text(advisory, language)
            audio_time = time.time() - audio_start
            logger.info(f"[DETECT_DISEASE] ✅ Audio generated in {audio_time:.2f}s, size: {audio_result.get('audio_size_bytes', 0)} bytes")
            
            query_id = f"disease_text_{len(query_history)}"
            query_record = {
                "id": query_id,
                "type": "disease_detection_text",
                "text_query": text_query,
                "prediction": "Text-based query",
                "confidence": 0.0,
                "is_reliable": False,
                "text": advisory,
                "language": language,
                "location": location,
                "audio_generated": audio_result.get("audio_url") is not None,
                "timestamp": datetime.datetime.now().isoformat()
            }
            query_history.append(query_record)
            
            elapsed_time = time.time() - endpoint_start_time
            logger.info(f"[DETECT_DISEASE] ✅ COMPLETE - Text query processed in {elapsed_time:.2f}s")
            
            return {
                "query_id": query_id,
                "filename": None,
                "prediction": "Text-based advisory",
                "confidence": 0.0,
                "is_reliable": False,
                "confidence_threshold": 0.7,
                "warning": "This is a text-based advisory. For accurate disease detection, please upload an image.",
                "top_predictions": [],
                "text": advisory,  # Text response in selected language
                "audio_url": audio_result.get("audio_url"),  # Audio as base64 data URL
                "language": language,
                "location": location,
                "response_time_seconds": elapsed_time
            }
        
        # Process images
        results = []
        logger.info(f"[DETECT_DISEASE] 🖼️ Processing {len(image_files)} image(s)")
        
        for idx, img_file in enumerate(image_files):
            try:
                file_num = idx + 1
                file_start = time.time()
                logger.info(f"[DETECT_DISEASE] 📷 [File {file_num}/{len(image_files)}] Processing: {img_file.filename}")
                logger.info(f"[DETECT_DISEASE] [File {file_num}] Content-Type: {img_file.content_type}")
                
                # Validate file type
                if img_file.content_type is None or not img_file.content_type.startswith("image/"):
                    logger.error(f"[DETECT_DISEASE] [File {file_num}] ❌ Invalid content-type: {img_file.content_type}")
                    results.append({
                        "error": f"File {file_num} is not a valid image",
                        "filename": img_file.filename,
                        "is_valid": False
                    })
                    continue
                
                # Read file into BytesIO
                logger.info(f"[DETECT_DISEASE] [File {file_num}] 📥 Reading file...")
                contents = await img_file.read()
                buf = io.BytesIO(contents)
                logger.info(f"[DETECT_DISEASE] [File {file_num}] ✅ File read complete - Size: {len(contents)} bytes")
                
                # Validate image file
                logger.info(f"[DETECT_DISEASE] [File {file_num}] 🔍 Validating image...")
                if not disease_detector.validate_image_file(buf):
                    logger.error(f"[DETECT_DISEASE] [File {file_num}] ❌ Invalid image or too large (>6MB)")
                    results.append({
                        "error": f"File {file_num} is invalid or too large (>6MB)",
                        "filename": img_file.filename,
                        "is_valid": False
                    })
                    continue
                logger.info(f"[DETECT_DISEASE] [File {file_num}] ✅ Image validation passed")
                
                # Validate that it's a leaf image
                logger.info(f"[DETECT_DISEASE] [File {file_num}] 🌿 Checking if leaf image...")
                buf.seek(0)
                is_leaf, leaf_msg = disease_detector.is_leaf_image(buf)
                if not is_leaf:
                    logger.warning(f"[DETECT_DISEASE] [File {file_num}] ⚠️ Not a leaf image: {leaf_msg}")
                    results.append({
                        "error": leaf_msg,
                        "filename": img_file.filename,
                        "prediction": "Not a valid leaf/plant image",
                        "prediction_ml": "സാധുവായ ഇലയോ ചെടിയോ അല്ല",
                        "confidence": 0.0,
                        "is_reliable": False,
                        "is_valid": False,
                        "warning": leaf_msg
                    })
                    continue
                logger.info(f"[DETECT_DISEASE] [File {file_num}] ✅ Leaf validation passed")
                
                # Get disease prediction
                logger.info(f"[DETECT_DISEASE] [File {file_num}] 🤖 Running disease detection...")
                predict_start = time.time()
                buf.seek(0)
                mk = crop.strip().lower() if crop and crop.strip() else None
                result = disease_detector.predict(buf, model_key=mk)
                predict_time = time.time() - predict_start
                logger.info(f"[DETECT_DISEASE] [File {file_num}] ✅ Disease detected in {predict_time:.2f}s: {result['prediction']} (confidence: {result['confidence']})")
                
                # Generate advisory
                logger.info(f"[DETECT_DISEASE] [File {file_num}] 💡 Generating advisory...")
                adv_start = time.time()
                crop_hint = advisory_service.infer_crop_from_detection(
                    result["prediction"], result.get("model_key")
                )
                loc_hint = location or "Telangana, India"
                logger.info(f"[DETECT_DISEASE] [File {file_num}] Crop hint: {crop_hint}, Location: {loc_hint}")
                
                if "error" in result["prediction"].lower() or result["prediction"] == "Model not available":
                    logger.warning(f"[DETECT_DISEASE] [File {file_num}] Model error detected")
                    advisory = result.get("warning") or "Disease detection failed. Please try again with a different image."
                elif result["is_reliable"]:
                    if "healthy" not in result["prediction"].lower():
                        logger.info(f"[DETECT_DISEASE] [File {file_num}] Getting disease advisory")
                        advisory = advisory_service.get_disease_advisory(
                            result["prediction"],
                            language,
                            location=loc_hint,
                            crop_name=crop_hint,
                        )
                    else:
                        logger.info(f"[DETECT_DISEASE] [File {file_num}] Crop is healthy, getting health advice")
                        advisory = advisory_service.get_healthy_crop_advice(crop_hint, language)
                else:
                    logger.warning(f"[DETECT_DISEASE] [File {file_num}] Low confidence prediction")
                    w = result.get("warning")
                    prefix = f"⚠️ {w}\n\n" if w else ""
                    advisory = prefix + advisory_service.get_disease_advisory(
                        result["prediction"],
                        language,
                        location=loc_hint,
                        crop_name=crop_hint,
                    )
                adv_time = time.time() - adv_start
                logger.info(f"[DETECT_DISEASE] [File {file_num}] ✅ Advisory generated in {adv_time:.2f}s")
                
                # Add to results with audio generation
                logger.info(f"[DETECT_DISEASE] [File {file_num}] 🎵 Generating audio for language {language}...")
                audio_start = time.time()
                audio_result = generate_audio_for_text(advisory, language)
                audio_time = time.time() - audio_start
                logger.info(f"[DETECT_DISEASE] [File {file_num}] ✅ Audio generated in {audio_time:.2f}s, size: {audio_result.get('audio_size_bytes', 0)} bytes")
                
                results.append({
                    "filename": img_file.filename,
                    "prediction": result["prediction"],
                    "prediction_ml": result.get("prediction_ml", result["prediction"]),
                    "confidence": result["confidence"],
                    "is_reliable": result["is_reliable"],
                    "confidence_threshold": result["confidence_threshold"],
                    "warning": result.get("warning"),
                    "top_predictions": result.get("top_predictions", []),
                    "model_key": result.get("model_key"),
                    "text": advisory,  # Text response in selected language
                    "audio_url": audio_result.get("audio_url"),  # Audio as base64 data URL
                    "is_valid": True
                })
                
                # Store in query history
                query_id = f"disease_{len(query_history)}"
                query_record = {
                    "id": query_id,
                    "type": "disease_detection",
                    "filename": img_file.filename,
                    "prediction": result["prediction"],
                    "prediction_ml": result.get("prediction_ml", result["prediction"]),
                    "confidence": result["confidence"],
                    "is_reliable": result["is_reliable"],
                    "text": advisory,
                    "language": language,
                    "location": location,
                    "audio_generated": audio_result.get("audio_url") is not None,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                query_history.append(query_record)
                file_time = time.time() - file_start
                logger.info(f"[DETECT_DISEASE] [File {file_num}/{len(image_files)}] ✅ COMPLETE in {file_time:.2f}s - Query ID: {query_id}")
                
            except Exception as e:
                logger.exception(f"[DETECT_DISEASE] [File {idx + 1}] ❌ ERROR: {type(e).__name__}: {str(e)}")
                results.append({
                    "error": f"Error processing image: {str(e)}",
                    "filename": img_file.filename if hasattr(img_file, 'filename') else f"File {idx + 1}",
                    "is_valid": False
                })
        
        # Return single result if only one image, array if multiple
        total_endpoint_time = time.time() - endpoint_start_time
        
        if len(results) == 1:
            result = results[0]
            result["language"] = language
            result["location"] = location
            result["response_time_seconds"] = total_endpoint_time
            logger.info(f"[DETECT_DISEASE] ✅ ENDPOINT COMPLETE - Total time: {total_endpoint_time:.2f}s - Returning single result")
            return result
        else:
            response = [
                {
                    **r,
                    "language": language,
                    "location": location,
                    "response_time_seconds": total_endpoint_time
                }
                for r in results
            ]
            logger.info(f"[DETECT_DISEASE] ✅ ENDPOINT COMPLETE - Total time: {total_endpoint_time:.2f}s - Returning {len(response)} results")
            return response
            
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[DETECT_DISEASE] ❌ FATAL ERROR: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Disease detection error: {str(e)}")

@app.post("/advisory/")
async def get_advisory(request: AdvisoryRequest):
    """
    Get comprehensive farming advisory based on crop, location, soil type, and season.
    FIXED: Now generates audio automatically and returns both text + audio URL
    ADDED: Response time logging and language logging
    """
    try:
        start_time = time.time()
        logger.info(f"Advisory request - Crop: {request.crop_name}, Language: {request.language}, Location: {request.location}")
        
        # Generate comprehensive advisory
        advisory = advisory_service.get_comprehensive_advisory(
            crop_name=request.crop_name,
            location=request.location,
            soil_type=request.soil_type,
            query=request.query,
            language=request.language
        )
        
        # Generate farming options based on season, soil type, and location
        farming_options = advisory_service.get_farming_options_by_season(
            location=request.location,
            soil_type=request.soil_type,
            season=request.season or "kharif",
            language=request.language
        )
        
        # Generate audio from advisory text - AUTOMATIC AUDIO GENERATION
        audio_result = generate_audio_for_text(advisory, request.language)
        
        # Store query in history
        query_id = f"advisory_{len(query_history)}"
        query_record = {
            "id": query_id,
            "type": "advisory",
            "crop_name": request.crop_name,
            "location": request.location,
            "soil_type": request.soil_type,
            "season": request.season,
            "query": request.query,
            "advisory": advisory,
            "language": request.language,
            "audio_generated": audio_result.get("audio_url") is not None,
            "timestamp": datetime.datetime.now().isoformat()
        }
        query_history.append(query_record)
        
        elapsed_time = time.time() - start_time
        logger.info(f"Advisory generated in {elapsed_time:.2f}s for language: {request.language}, audio: {audio_result.get('audio_url') is not None}")
        
        return {
            "query_id": query_id,
            "text": advisory,  # Text response in selected language
            "audio_url": audio_result.get("audio_url"),  # Audio as base64 data URL
            "farming_options": farming_options,
            "season": request.season or "kharif",
            "language": request.language,
            "response_time_seconds": elapsed_time
        }
    except Exception as e:
        logger.exception("Error in advisory generation: %s", e)
        raise HTTPException(status_code=500, detail=f"Advisory generation error: {str(e)}")

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
    FIXED: Properly handles language parameter for multilingual TTS
    ADDED: Returns standard audio format with language logging
    """
    try:
        logger.info(f"TTS request - Language: {request.language}, Text length: {len(request.text)}")
        start_time = time.time()
        
        # Call voice service to generate audio
        tts_result = voice_service.text_to_speech(request.text, request.language)
        audio_data = tts_result.get("audio_data")
        audio_path = tts_result.get("audio_path")
        
        if not audio_data:
            raise HTTPException(status_code=500, detail="Failed to generate audio")
        
        elapsed_time = time.time() - start_time
        logger.info(f"TTS completed in {elapsed_time:.2f}s for language: {request.language}, size: {len(audio_data)} bytes")
        
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/mp3",
            headers={"Content-Disposition": "attachment; filename=response.mp3"}
        )
    except Exception as e:
        logger.error(f"TTS error for language {request.language}: {type(e).__name__}: {str(e)}")
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
            {"code": "te", "name": "తెలుగు (Telugu)"}
        ]
    }

# ==================== TRANSLATION ENDPOINTS ====================

class TranslateRequest(BaseModel):
    text: str
    target_language: str = "te"
    source_language: str = "en"

class TranslateBatchRequest(BaseModel):
    texts: list[str]
    target_language: str = "te"
    source_language: str = "en"

@app.post("/translate")
async def translate(request: TranslateRequest):
    """
    Translate text to target language
    
    Args:
        text: Text to translate
        target_language: Target language code (en, te, hi, ml)
        source_language: Source language code (default: en)
    
    Returns:
        Translated text
    """
    try:
        translated = translation_service.translate_text_cached(
            request.text,
            request.target_language,
            request.source_language
        )
        return {
            "original_text": request.text,
            "translated_text": translated,
            "target_language": request.target_language,
            "source_language": request.source_language
        }
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@app.post("/translate-batch")
async def translate_batch(request: TranslateBatchRequest):
    """
    Translate multiple texts at once
    
    Args:
        texts: List of texts to translate
        target_language: Target language code
        source_language: Source language code
    
    Returns:
        List of translated texts
    """
    try:
        translated = translation_service.translate_batch(
            request.texts,
            request.target_language,
            request.source_language
        )
        return {
            "translated_texts": translated,
            "target_language": request.target_language,
            "count": len(translated)
        }
    except Exception as e:
        logger.error(f"Batch translation error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch translation failed: {str(e)}")

@app.post("/translate")
async def translate_query_param(text: str = Query(...), lang: str = Query("te")):
    """
    Alternative translation endpoint using query parameters
    
    Usage: GET /translate?text=hello&lang=te
    """
    try:
        translated = translation_service.translate_text_cached(text, lang, "en")
        return {
            "text": text,
            "translated": translated,
            "language": lang
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/translation/cache-stats")
def get_translation_cache_stats():
    """Get translation cache statistics"""
    cache_info = translation_service.translate_text_cached.cache_info()
    return {
        "cache_hits": cache_info.hits,
        "cache_misses": cache_info.misses,
        "cache_size": cache_info.currsize,
        "cache_maxsize": cache_info.maxsize
    }

@app.post("/translation/clear-cache")
def clear_translation_cache():
    """Clear translation cache (useful for testing)"""
    translation_service.clear_translation_cache()
    return {"status": "Cache cleared successfully"}

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

# ==================== DEBUG & DIAGNOSTICS ====================

@app.get("/debug/voice-status")
def get_voice_status():
    """
    Debug endpoint to check voice service status and capabilities
    """
    try:
        from app.services.voice_service import get_voice_capabilities, GTTS_AVAILABLE, PYTTSX3_AVAILABLE
        
        capabilities = get_voice_capabilities()
        
        # Get pyttsx3 voice info if available
        pyttsx3_info = {}
        if PYTTSX3_AVAILABLE:
            try:
                import pyttsx3
                engine = pyttsx3.init()
                voices = engine.getProperty('voices')
                pyttsx3_info = {
                    "available": True,
                    "voices_count": len(voices),
                    "voices": [
                        {
                            "name": v.name,
                            "id": v.id,
                            "languages": v.languages if hasattr(v, 'languages') else []
                        }
                        for v in voices
                    ]
                }
            except Exception as e:
                pyttsx3_info = {"available": False, "error": str(e)}
        
        return {
            "status": "ok",
            "timestamp": datetime.datetime.now().isoformat(),
            "engines": {
                "gtts": {
                    "available": GTTS_AVAILABLE,
                    "name": "Google Text-to-Speech",
                    "requires_internet": True,
                    "languages": ["en", "hi", "ml", "te", "ta", "kn"]
                },
                "pyttsx3": {
                    "available": PYTTSX3_AVAILABLE,
                    "name": "Offline Text-to-Speech",
                    "requires_internet": False,
                    **pyttsx3_info
                }
            },
            "capabilities": capabilities,
            "supported_languages": {
                "en": "English",
                "hi": "हिंदी (Hindi)",
                "ml": "മലയാളം (Malayalam)",
                "te": "తెలుగు (Telugu)",
                "ta": "தமிழ் (Tamil)",
                "kn": "ಕನ್ನಡ (Kannada)"
            }
        }
    except Exception as e:
        logger.error(f"Error getting voice status: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }

@app.post("/debug/test-tts")
async def test_tts(request: dict):
    """
    Test TTS for a specific language with detailed diagnostics
    """
    try:
        text = request.get("text", "नमस्ते")  # Default to Hindi greeting
        language = request.get("language", "hi")
        
        logger.info(f"Testing TTS with language: {language}, text: {text}")
        
        # Get audio
        audio_buffer = voice_service.text_to_speech(text, language)
        
        return {
            "status": "success",
            "language": language,
            "text": text,
            "audio_size_bytes": len(audio_buffer),
            "message": "Audio generated successfully" if len(audio_buffer) > 500 else "Warning: Audio may be silence fallback"
        }
    except Exception as e:
        logger.error(f"TTS test error: {e}", exc_info=True)
        return {
            "status": "error",
            "language": request.get("language", "hi"),
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }
