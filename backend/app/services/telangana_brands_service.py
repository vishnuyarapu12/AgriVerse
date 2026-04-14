"""
Curated list of widely used agri input brands in Telangana / South India (reference for farmers).
Extend this dict as needed — not an endorsement; follow label and local dealer advice.
"""
from typing import Any, Dict, List

# Categories: seeds, fertilizer, crop_protection, bio_stimulant
TELANGANA_TOP_BRANDS: List[Dict[str, Any]] = [
    {
        "company": "UPL Ltd.",
        "products": ["Saaf (Carbendazim+Mancozeb)", "Tricyclazole brands", "Glufosinate herbicides"],
        "category": "Crop protection",
        "note": "Common in rice & chilli belts; buy from authorized dealers",
    },
    {
        "company": "Bayer CropScience",
        "products": ["Laudis (Tembotrione)", "Folicur (Tebuconazole)", "Movento"],
        "category": "Crop protection",
        "note": "Widely stocked in Hyderabad & district agri hubs",
    },
    {
        "company": "Syngenta India",
        "products": ["Amistar (Azoxystrobin)", "Virtako", "Touchdown herbicides"],
        "category": "Crop protection",
        "note": "Popular for vegetables & cotton IPM programs",
    },
    {
        "company": "Corteva Agriscience",
        "products": ["Rinskor herbicide", "Lannate (Methomyl) where registered", "Pioneer® seeds"],
        "category": "Seeds & crop protection",
        "note": "Maize & cotton hybrid seeds common in Telangana",
    },
    {
        "company": "FMC India",
        "products": ["Coragen (Chlorantraniliprole)", "Authority herbicides"],
        "category": "Crop protection",
        "note": "Used in fruit & vegetable protective sprays",
    },
    {
        "company": "PI Industries",
        "products": ["Nominee Gold (Bispyribac)", "Osheen", "Biological adjuvants"],
        "category": "Crop protection",
        "note": "Strong presence in rice herbicide segment",
    },
    {
        "company": "Dhanuka Agritech",
        "products": ["Targa Super", "Maxim", "Various generics"],
        "category": "Crop protection",
        "note": "Affordable range in rural retail",
    },
    {
        "company": "IFFCO / NFL / Coromandel",
        "products": ["DAP", "Urea", "NPK complexes", "IFFCO Nano Urea"],
        "category": "Fertilizers",
        "note": "Soil-test based NPK; Nano Urea pilot use as per extension advice",
    },
    {
        "company": "National Seeds / State federations",
        "products": ["Groundnut, pigeon pea, cotton notified varieties"],
        "category": "Seeds",
        "note": "Prefer certified / truthfully labelled seed from licensed sellers",
    },
]


def list_telangana_brands() -> List[Dict[str, Any]]:
    return TELANGANA_TOP_BRANDS
