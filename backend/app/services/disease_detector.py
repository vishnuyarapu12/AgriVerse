import os
import json
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from typing import Dict, Any, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "rice_disease_model.h5")
LABEL_MAP_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "label_map.json")

# Confidence threshold for reliable predictions
CONFIDENCE_THRESHOLD = 0.7

_model = None
_labels = None
TARGET_DISEASE = "Leaf smut"

def _load():
    """Load the trained rice disease model and label mappings"""
    global _model, _labels
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Rice disease model not found at {MODEL_PATH}. Please train the model first using train_rice_disease.py")
        try:
            _model = load_model(MODEL_PATH)
            logger.info(f"Loaded rice disease model from {MODEL_PATH}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    if _labels is None:
        if not os.path.exists(LABEL_MAP_PATH):
            raise FileNotFoundError(f"Label map not found at {LABEL_MAP_PATH}. Please create label_map.json when training.")
        try:
            with open(LABEL_MAP_PATH, "r", encoding="utf-8") as f:
                _labels = json.load(f)
            logger.info(f"Loaded label mappings for {len(_labels)} classes")
        except Exception as e:
            logger.error(f"Error loading label map: {e}")
            raise

def preprocess_image(file_stream, target_size=(224, 224)) -> np.ndarray:
    """
    Preprocess image for model input
    """
    try:
        img = Image.open(file_stream).convert("RGB")
        img = img.resize(target_size)
        arr = img_to_array(img) / 255.0  # Normalize to [0, 1]
        arr = np.expand_dims(arr, axis=0)  # Add batch dimension
        return arr
    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        raise

def predict(file_stream) -> Dict[str, Any]:
    """
    Predict rice disease from image
    
    Returns:
        Dict containing prediction, confidence, label_id, and safety flags
    """
    try:
        _load()
        x = preprocess_image(file_stream, target_size=(224, 224))
        preds = _model.predict(x, verbose=0)[0]  # shape (num_classes,)
        
        idx = int(np.argmax(preds))
        confidence = float(preds[idx])

        # Get label information
        label_info = _labels.get(str(idx), {"en": f"Unknown_Class_{idx}", "ml": f"അജ്ഞാത_ക്ലാസ്_{idx}"})

        predicted_label_en = label_info.get("en", f"Unknown_Class_{idx}")

        # Determine if prediction is reliable
        is_reliable = confidence >= CONFIDENCE_THRESHOLD

        # Restrict to single-disease classification (Leaf smut)
        leaf_smut_detected = is_reliable and (predicted_label_en.lower() == TARGET_DISEASE.lower())

        # Get top 3 predictions for additional context
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
                "warning": None
            }
        else:
            # Not confidently Leaf smut → treat as negative
            result = {
                "prediction": predicted_label_en,
                "prediction_ml": label_info.get("ml", predicted_label_en),
                "confidence": round(confidence, 4),
                "label_id": str(idx),
                "is_reliable": False,
                "leaf_smut_detected": False,
                "confidence_threshold": CONFIDENCE_THRESHOLD,
                "top_predictions": top_predictions,
                "warning": f"Not confidently {TARGET_DISEASE} (top: {predicted_label_en}, {confidence:.2f}). Please try a clearer, close-up leaf image."
            }
        
        logger.info(f"Prediction: {result['prediction']} (confidence: {confidence:.3f}, leaf_smut={result.get('leaf_smut_detected')})")
        return result
        
    except Exception as e:
        logger.error(f"Error during prediction: {e}")
        raise

def get_disease_info(disease_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific rice disease
    """
    # Rice disease information database
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
    """
    Validate that the uploaded file is a valid image
    """
    try:
        # Reset stream position
        file_stream.seek(0)
        
        # Try to open and verify image
        img = Image.open(file_stream)
        img.verify()
        
        # Check file size (limit to 6MB)
        file_stream.seek(0, 2)  # Seek to end
        file_size = file_stream.tell()
        file_stream.seek(0)  # Reset position
        
        if file_size > 6 * 1024 * 1024:  # 6MB limit
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Image validation failed: {e}")
        return False
