"""
Dictionary-based mock database for one-tap disease solution cards.
Extend DISEASE_SOLUTIONS with more keys (normalized lowercase).
"""
import logging
import re
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Keys are normalized: lowercase, spaces, no extra punctuation
DISEASE_SOLUTIONS: Dict[str, Dict[str, str]] = {
    "leaf spot": {
        "disease": "Leaf Spot",
        "medicine": "Mancozeb 75% WP",
        "dosage": "2 g per liter of water",
        "time": "Morning (before 9 AM)",
        "note": "Repeat every 7 days; avoid spraying during rain",
    },
    "rice blast": {
        "disease": "Rice Blast",
        "medicine": "Tricyclazole 75% WP",
        "dosage": "0.6 g per liter (or as per label)",
        "time": "Evening",
        "note": "Start at tillering; repeat if disease persists",
    },
    "wheat rust": {
        "disease": "Wheat Rust",
        "medicine": "Propiconazole 25% EC",
        "dosage": "1 ml per liter",
        "time": "Morning",
        "note": "Repeat every 10–14 days; alternate chemistry next season",
    },
    "early blight": {
        "disease": "Early Blight",
        "medicine": "Chlorothalonil 75% WP",
        "dosage": "2 g per liter",
        "time": "Morning or late evening",
        "note": "Repeat every 7 days; improve air circulation in field",
    },
}


def normalize_disease_key(raw: str) -> str:
    """Turn URL/path segment into lookup key: 'Leaf-Spot' -> 'leaf spot'."""
    s = raw.strip().lower()
    s = s.replace("_", " ").replace("-", " ")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def get_solution(raw_disease: str) -> Optional[Dict[str, str]]:
    """Return solution dict or None if disease not in mock DB."""
    key = normalize_disease_key(raw_disease)
    row = DISEASE_SOLUTIONS.get(key)
    if row:
        logger.info("Solution card hit: %s", key)
    else:
        logger.info("Solution card miss: %s (normalized: %s)", raw_disease, key)
    return row


def list_supported_diseases() -> list:
    """For docs / UI: canonical disease names."""
    return sorted({v["disease"] for v in DISEASE_SOLUTIONS.values()})
