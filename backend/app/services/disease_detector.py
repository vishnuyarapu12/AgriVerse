import os
import json
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "disease_model.h5")
LABEL_MAP_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "label_map.json")

_model = None
_labels = None

def _load():
    global _model, _labels
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at {MODEL_PATH}. Train and save model as disease_model.h5")
        _model = load_model(MODEL_PATH)
    if _labels is None:
        if not os.path.exists(LABEL_MAP_PATH):
            raise FileNotFoundError(f"Label map not found at {LABEL_MAP_PATH}. Create label_map.json when training.")
        with open(LABEL_MAP_PATH, "r") as f:
            _labels = json.load(f)

def preprocess_image(file_stream, target_size=(224,224)):
    img = Image.open(file_stream).convert("RGB")
    img = img.resize(target_size)
    arr = img_to_array(img) / 255.0
    arr = np.expand_dims(arr, axis=0)
    return arr

def predict(file_stream):
    """
    Returns: { "prediction": str, "confidence": float }
    """
    _load()
    x = preprocess_image(file_stream, target_size=(224,224))
    preds = _model.predict(x)[0]  # shape (num_classes,)
    idx = int(np.argmax(preds))
    label = _labels.get(str(idx), f"label_{idx}")
    confidence = float(preds[idx])
    return {"prediction": label, "confidence": round(confidence, 4)}
