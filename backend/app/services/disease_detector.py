import os
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import numpy as np
from PIL import Image
import logging

# Handle TensorFlow/Keras imports with fallback
try:
    from tensorflow.keras.models import load_model  # type: ignore
    from tensorflow.keras.preprocessing.image import img_to_array  # type: ignore
except Exception:
    from keras.models import load_model  # type: ignore
    from keras.preprocessing.image import img_to_array  # type: ignore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Repo root: backend/app/services -> backend/app -> backend -> project root
_SERVICE_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_APP_DIR = os.path.dirname(_SERVICE_DIR)  # backend/app
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_BACKEND_APP_DIR))  # parent of backend/
_ROOT_APP_MODELS = os.path.join(_PROJECT_ROOT, "app", "models")
_LEGACY_MODELS = os.path.join(_BACKEND_APP_DIR, "models")

# Search order: <project>/app/models (canonical), then backend/app/models
_MODEL_DIRS: List[str] = []
if os.path.isdir(_ROOT_APP_MODELS):
    _MODEL_DIRS.append(_ROOT_APP_MODELS)
if os.path.isdir(_LEGACY_MODELS) and os.path.normpath(_LEGACY_MODELS) != os.path.normpath(_ROOT_APP_MODELS):
    _MODEL_DIRS.append(_LEGACY_MODELS)

# Auto-select order when model_key is omitted (first match wins)
_MODEL_PRIORITY = ("archive", "rice", "cotton", "banana", "crops")

_model = None
_labels = None
_loaded_task = None
_model_dir = None
_paths_cache: Optional[List[Tuple[str, str, str, str]]] = None

TARGET_DISEASE = "Leaf smut"
CONFIDENCE_THRESHOLD = 0.7


def _discover_in_directory(models_dir: str) -> List[Tuple[str, str, str]]:
    """Return list of (model_file, label_file, task_id) for one models directory."""
    md = Path(models_dir)
    if not md.is_dir():
        return []

    raw: List[Tuple[str, str, str]] = []

    if (md / "rice_disease_model.h5").is_file() and (md / "label_map.json").is_file():
        raw.append(("rice_disease_model.h5", "label_map.json", "rice"))

    if (md / "crop_model.h5").is_file() and (md / "crop_label_map.json").is_file():
        raw.append(("crop_model.h5", "crop_label_map.json", "crops"))

    for p in sorted(md.glob("*_disease_model.h5")):
        name = p.name
        base = name[: -len("_disease_model.h5")]
        if base == "rice":
            continue
        lf = f"{base}_label_map.json"
        if (md / lf).is_file():
            raw.append((name, lf, base))

    by_tid: Dict[str, Tuple[str, str]] = {}
    for mf, lf, tid in raw:
        if tid not in by_tid:
            by_tid[tid] = (mf, lf)

    ordered: List[Tuple[str, str, str]] = []
    for tid in _MODEL_PRIORITY:
        if tid in by_tid:
            mf, lf = by_tid[tid]
            ordered.append((mf, lf, tid))
            del by_tid[tid]
    for tid in sorted(by_tid.keys()):
        mf, lf = by_tid[tid]
        ordered.append((mf, lf, tid))

    return ordered


def build_model_paths() -> List[Tuple[str, str, str, str]]:
    """All (models_dir, model_file, label_file, task_id); repo-root dir wins per task_id."""
    result: List[Tuple[str, str, str, str]] = []
    seen = set()
    for models_dir in _MODEL_DIRS:
        for mf, lf, tid in _discover_in_directory(models_dir):
            if tid in seen:
                continue
            seen.add(tid)
            result.append((models_dir, mf, lf, tid))
    return result


def list_available_models() -> List[Dict[str, str]]:
    """Task ids and files for API / UI."""
    out: List[Dict[str, str]] = []
    for models_dir, mf, lf, tid in build_model_paths():
        out.append({
            "task_id": tid,
            "model_file": mf,
            "label_file": lf,
            "directory": models_dir,
        })
    return out


def initialize_models(model_key: Optional[str] = None) -> bool:
    """
    Pre-load models at startup for optimal performance.
    Called during app initialization to warm up the model cache.
    Returns True if successful, False otherwise.
    """
    try:
        logger.info(f"🚀 Initializing disease detection models (model_key={model_key})...")
        _load(model_key=model_key)
        if _model is not None:
            logger.info(f"✅ Model initialization successful - loaded task: {_loaded_task}")
            return True
        else:
            logger.warning("⚠️  Model initialization returned None - models may not be available")
            return False
    except Exception as e:
        logger.error(f"❌ Model initialization failed: {type(e).__name__}: {str(e)}")
        return False


def _get_paths() -> List[Tuple[str, str, str, str]]:
    global _paths_cache
    if _paths_cache is None:
        _paths_cache = build_model_paths()
    return _paths_cache


def invalidate_model_cache() -> None:
    """Call after deploying new .h5 files if the process stays up."""
    global _model, _labels, _loaded_task, _model_dir, _paths_cache
    _model = None
    _labels = None
    _loaded_task = None
    _model_dir = None
    _paths_cache = None


def _load(model_key: Optional[str] = None) -> None:
    """Load model for task_id model_key, or first available if model_key is None."""
    global _model, _labels, _loaded_task, _model_dir

    logger.info(f"[_LOAD] START - model_key={model_key}, current_loaded_task={_loaded_task}")
    
    paths = _get_paths()
    logger.info(f"[_LOAD] Found {len(paths) if paths else 0} available models")
    
    if not paths:
        logger.warning("[_LOAD] ❌ No disease model files found under app/models.")
        _model = None
        return

    if model_key:
        key = model_key.strip().lower()
        logger.info(f"[_LOAD] Searching for model_key: {key}")
        matches = [p for p in paths if p[3] == key]
        if not matches:
            logger.warning(f"[_LOAD] ❌ No model found for task_id={key!r}")
            logger.info(f"[_LOAD] Available task_ids: {[p[3] for p in paths]}")
            _model = None
            return
        chosen = matches[0]
        logger.info(f"[_LOAD] ✅ Found model for {key}")
    else:
        chosen = paths[0]
        logger.info(f"[_LOAD] Using first available model: {chosen[3]}")

    models_dir, mf, lf, tid = chosen

    if _model is not None and _loaded_task == tid and _model_dir == models_dir:
        logger.info(f"[_LOAD] ✅ Model already loaded for {tid}, skipping reload")
        return

    model_path = os.path.join(models_dir, mf)
    label_path = os.path.join(models_dir, lf)

    logger.info(f"[_LOAD] 📦 Loading model from: {model_path}")
    try:
        _model = load_model(model_path)
        _loaded_task = tid
        _model_dir = models_dir
        logger.info(f"[_LOAD] ✅ Loaded {tid} disease model successfully")
    except Exception as e:
        logger.error(f"[_LOAD] ❌ Error loading {model_path}: {type(e).__name__}: {str(e)}")
        _model = None
        _loaded_task = None
        _model_dir = None
        return

    _labels = None
    logger.info(f"[_LOAD] 📂 Loading labels from: {label_path}")
    try:
        with open(label_path, "r", encoding="utf-8") as f:
            _labels = json.load(f)
        logger.info(f"[_LOAD] ✅ Loaded label mappings for {len(_labels)} classes")
    except Exception as e:
        logger.error(f"[_LOAD] ❌ Error loading label map: {e}")
        _labels = {"0": {"en": "Unknown", "ml": "അജ്ഞാതം"}}


def preprocess_image(file_stream, target_size=(224, 224)) -> np.ndarray:
    try:
        img = Image.open(file_stream).convert("RGB")
        img = img.resize(target_size)
        arr = img_to_array(img) / 255.0
        arr = np.expand_dims(arr, axis=0)
        return arr
    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        raise


def predict(file_stream, model_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Predict disease from image. model_key selects task_id (e.g. rice, cotton, archive).
    If None, uses the first model in priority order.
    """
    try:
        logger.info(f"🔥 [PREDICT] START - model_key={model_key}")
        logger.info(f"[PREDICT] 📦 Loading model...")
        _load(model_key=model_key)

        if _model is None:
            logger.error(f"[PREDICT] ❌ Model is None after _load()")
            avail = [m["task_id"] for m in list_available_models()]
            hint = f" Available: {', '.join(avail)}." if avail else " Train with: python backend/train_unified.py --task cotton --data_dir datasets/cotton_leaf_diseases"
            return {
                "prediction": "Model not available",
                "prediction_ml": "മോഡൽ ലഭ്യമല്ല",
                "confidence": 0.0,
                "label_id": "0",
                "is_reliable": False,
                "leaf_smut_detected": False,
                "confidence_threshold": CONFIDENCE_THRESHOLD,
                "top_predictions": [],
                "model_key": model_key,
                "warning": f"No model loaded for {model_key!r}.{hint}" if model_key else f"No disease model found.{hint}",
            }

        logger.info(f"[PREDICT] ✅ Model loaded: {_loaded_task}")
        logger.info(f"[PREDICT] 🖼️ Preprocessing image...")
        x = preprocess_image(file_stream, target_size=(224, 224))
        logger.info(f"[PREDICT] ✅ Image preprocessed - Shape: {x.shape}")
        
        logger.info(f"[PREDICT] 🧠 Running model prediction...")
        preds = _model.predict(x, verbose=0)[0]
        logger.info(f"[PREDICT] ✅ Predictions received - {len(preds)} classes")

        idx = int(np.argmax(preds))
        confidence = float(preds[idx])
        logger.info(f"[PREDICT] Top prediction - Class {idx}, Confidence: {confidence:.4f}")

        label_info = _labels.get(str(idx), {"en": f"Unknown_Class_{idx}", "ml": f"അജ്ഞാത_ക്ലാസ്_{idx}"})

        predicted_label_en = label_info.get("en", f"Unknown_Class_{idx}")

        is_reliable = confidence >= CONFIDENCE_THRESHOLD
        logger.info(f"[PREDICT] Reliability: {is_reliable} (threshold: {CONFIDENCE_THRESHOLD})")

        task = _loaded_task or "rice"
        if task == "rice":
            leaf_smut_detected = is_reliable and (predicted_label_en.lower() == TARGET_DISEASE.lower())
        else:
            leaf_smut_detected = is_reliable and ("healthy" not in predicted_label_en.lower())

        top_indices = np.argsort(preds)[::-1][:3]
        top_predictions = []
        for i in top_indices:
            label_info_top = _labels.get(str(i), {"en": f"Unknown_Class_{i}", "ml": f"അജ്ഞാത_ക്ലാസ്_{i}"})
            top_predictions.append({
                "label": label_info_top,
                "confidence": float(preds[i])
            })

        if leaf_smut_detected:
            result = {
                "prediction": TARGET_DISEASE,
                "prediction_ml": label_info.get("ml", TARGET_DISEASE),
                "confidence": round(confidence, 4),
                "label_id": str(idx),
                "is_reliable": True,
                "leaf_smut_detected": True,
                "confidence_threshold": CONFIDENCE_THRESHOLD,
                "top_predictions": top_predictions,
                "warning": None,
                "model_key": task,
            }
        else:
            warn_msg = (f"Low confidence ({confidence:.2f}). Top: {predicted_label_en}. "
                        "Try a clearer, close-up leaf image.") if task == "rice" else (
                        f"Low confidence ({confidence:.2f}). Top: {predicted_label_en}.")
            result = {
                "prediction": predicted_label_en,
                "prediction_ml": label_info.get("ml", predicted_label_en),
                "confidence": round(confidence, 4),
                "label_id": str(idx),
                "is_reliable": is_reliable,
                "leaf_smut_detected": False,
                "confidence_threshold": CONFIDENCE_THRESHOLD,
                "top_predictions": top_predictions,
                "warning": None if is_reliable else warn_msg,
                "model_key": task,
            }

        logger.info(f"[PREDICT] ✅ COMPLETE - Prediction: {result['prediction']} (confidence: {confidence:.3f}, task={task})")
        return result
    except Exception as e:
        logger.exception(f"[PREDICT] ❌ ERROR: {type(e).__name__}: {str(e)}")
        raise

    except Exception as e:
        logger.error(f"Error during prediction: {e}")
        # Return safe error response instead of raising
        return {
            "prediction": "Error during prediction",
            "prediction_ml": "പ്രവചനത്തിൽ പിശക്",
            "confidence": 0.0,
            "label_id": "-1",
            "is_reliable": False,
            "leaf_smut_detected": False,
            "confidence_threshold": CONFIDENCE_THRESHOLD,
            "top_predictions": [],
            "model_key": None,
            "warning": f"An error occurred during disease detection: {str(e)}"
        }


def get_disease_info(disease_name: str) -> Dict[str, Any]:
    disease_info = {
        "Bacterial leaf blight": {
            "symptoms": ["Yellowing leaves", "Water-soaked lesions", "Leaf wilting"],
            "causes": ["Xanthomonas oryzae bacteria", "High humidity", "Poor drainage"],
            "prevention": ["Use resistant varieties", "Proper irrigation", "Crop rotation"],
            "treatment": ["Copper-based fungicides", "Remove affected plants", "Improve drainage"]
        },
        "Brown spot": {
            "symptoms": ["Brown circular spots", "Leaf yellowing", "Reduced yield"],
            "causes": ["Bipolaris oryzae fungus", "Poor nutrition", "High humidity"],
            "prevention": ["Balanced fertilization", "Good field hygiene", "Proper spacing"],
            "treatment": ["Fungicide application", "Improve nutrition", "Remove debris"]
        }
    }

    return disease_info.get(disease_name, {
        "symptoms": ["Symptoms vary by disease"],
        "causes": ["Multiple factors possible"],
        "prevention": ["General preventive measures"],
        "treatment": ["Consult agricultural expert"]
    })


def validate_image_file(file_stream) -> bool:
    try:
        file_stream.seek(0)
        img = Image.open(file_stream)
        img.verify()
        file_stream.seek(0, 2)
        file_size = file_stream.tell()
        file_stream.seek(0)
        if file_size > 6 * 1024 * 1024:
            return False
        return True
    except Exception as e:
        logger.error(f"Image validation failed: {e}")
        return False


def is_leaf_image(file_stream) -> Tuple[bool, str]:
    """
    Validate if the image appears to be a leaf/plant image.
    Returns (is_leaf, message) tuple.
    Uses color analysis to detect if image contains leaf-like colors (greens, browns).
    """
    try:
        file_stream.seek(0)
        img = Image.open(file_stream).convert("RGB")
        file_stream.seek(0)
        
        # Resize for faster processing
        img_small = img.resize((100, 100))
        pixels = np.array(img_small)
        
        # Extract RGB channels
        red = pixels[:, :, 0].astype(float)
        green = pixels[:, :, 1].astype(float)
        blue = pixels[:, :, 2].astype(float)
        
        # Calculate color metrics
        # Greenness: high green relative to red and blue
        greenness = green - (red + blue) / 2
        # Check for natural colors: green for leaves, brown for diseased areas
        green_pixels = np.sum(greenness > 10)
        brown_pixels = np.sum((red > 100) & (green < 150) & (blue < 100))
        
        total_pixels = pixels.shape[0] * pixels.shape[1]
        green_ratio = green_pixels / total_pixels
        brown_ratio = brown_pixels / total_pixels
        
        # Check for predominantly white/gray background (not leaf)
        gray_pixels = np.sum(np.abs(red - green) < 20) & np.sum(np.abs(green - blue) < 20)
        gray_ratio = gray_pixels / total_pixels if isinstance(gray_pixels, (int, float)) else 0
        
        # A leaf image should have reasonable amount of green or brown colors
        # and not be mostly white/uniform background
        is_leaf = (green_ratio > 0.15 or brown_ratio > 0.1) and gray_ratio < 0.7
        
        if not is_leaf:
            return False, "Not a valid leaf/plant image. Please upload a clear image of a leaf or crop."
        
        return True, "Valid leaf image"
        
    except Exception as e:
        logger.error(f"Leaf image validation failed: {e}")
        return False, f"Error validating image: {str(e)}"
