"""
Advanced Advisory Service for comprehensive farming guidance with Rice Disease Support
"""
import re
import logging
from typing import Dict, List, Optional, Any
from . import gemini_client

logger = logging.getLogger(__name__)

# Strict output structure for Telangana-focused disease advisories (Gemini follows this skeleton)
TELANGANA_ADVISORY_FORMAT = """
OUTPUT FORMAT (STRICT - FOLLOW EXACTLY, use these section titles and numbering):

1. Disease Name:
* Name of the disease
* Type (Fungal / Bacterial / Viral / Pest)

2. Cause:
* Exact pathogen or reason
* Environmental conditions (humidity, temperature, soil, etc.)

3. Symptoms:
* Key visible symptoms in simple points

4. Solution:
(A) Cultural Practices:
* List 3-5 preventive actions

(B) Chemical Control:
For each recommended pesticide/fungicide:
* Chemical Name
* Dosage (per liter or per acre as appropriate)
* When to apply

(C) Telangana Popular Brands:
Suggest REAL products commonly available in Telangana from companies such as UPL, Bayer, Syngenta, Corteva, FMC, PI Industries.
For each:
* Product Name
* Company

(D) Fertilizer Recommendation:
* NPK ratio
* Micronutrients (Zn, Fe, Boron if needed)

5. Chemical Composition:
For each chemical used:
* Active Ingredient + Percentage
* Formulation type (WP / EC / SC / SL)

6. Application Method:
* Spray timing (morning/evening)
* Frequency
* Mixing instructions

7. Safety Precautions:
* Do's and Don'ts for farmers
* Avoid overuse warning

8. Crop Recommendation (IMPORTANT):
Based on the disease and Telangana conditions:
* Suggest 2-3 alternative crops suitable for current season
* Mention why (soil, climate, disease resistance)

RULES:
* Keep language simple and farmer-friendly
* Do NOT give vague answers
* Always include REAL chemical names and realistic dosages for Indian conditions
* Avoid unsafe or banned chemicals (follow Indian regulations)
* Prefer commonly used Indian/Telangana agricultural products
* Keep response structured and clearly separated by headings
"""

# Organic / sustainable farming (Telangana) — no synthetic pesticides or chemical fertilizers
ORGANIC_FARMING_FORMAT = """
OUTPUT FORMAT (STRICT - FOLLOW EXACTLY):

1. Crop Name:
* Mention the crop

2. Suitable Soil & Climate:
* Soil type best suited
* Climate conditions in Telangana

3. Organic Farming Practices:

(A) Soil Preparation:
* Organic methods to improve soil fertility
* Use of compost, vermicompost, green manure crops

(B) Seed Treatment:
* Organic seed treatment methods (e.g., Trichoderma, cow urine, neem extract)

(C) Nutrient Management:
* Organic fertilizers (FYM, vermicompost, biofertilizers)
* Recommended application quantities (per acre) — realistic ranges for India

(D) Pest & Disease Control:
* Organic solutions only (NO chemical pesticides)
* Use neem oil, garlic-chilli extract, cow-based solutions (Jeevamrutham, Panchagavya)
* Biological controls (Trichoderma, Bacillus thuringiensis, NPV) where relevant

(E) Weed Management:
* Manual/mechanical methods
* Mulching techniques

(F) Water Management:
* Irrigation methods suitable for Telangana (drip, alternate wetting, etc.)

4. Telangana-Specific Organic Inputs:
* Suggest commonly used organic products or inputs available in local markets
* Example: neem cake, vermicompost units, biofertilizers

5. Crop-wise Tips:
* 4-5 practical tips specific to the crop

6. Yield & Benefits:
* Expected yield (approximate range under good organic management)
* Benefits of organic farming (soil health, cost reduction, export value)

7. Do's and Don'ts:
* Key precautions for farmers

RULES:
* Use simple, farmer-friendly language
* Do NOT include chemical fertilizers or synthetic chemical pesticides
* Keep content practical and region-specific (Telangana)
* Provide realistic quantities and methods
* Keep response well-structured with headings
* Plain text only (no markdown symbols)
"""


class AdvisoryService:
    def __init__(self):
        # Rice disease treatments with multilingual support
        self.disease_treatments = {
            "Leaf smut": {
                "en": "Leaf smut is caused by Ustilaginoidea virens fungus. Improve drainage, ensure proper spacing, and apply fungicide treatment.",
                "hi": "लीफ स्मट Ustilaginoidea virens फंगस के कारण होता है। जल निकासी में सुधार करें, उचित दूरी सुनिश्चित करें और फफूंदनाशक दवा लगाएं।",
                "ml": "ലീഫ് സ്മട്ട് Ustilaginoidea virens ഫംഗസ് മൂലമാണ്. ജലനിർഗ്ഗമനം മെച്ചപ്പെടുത്തുക, ശരിയായ ഇടവേള പാലിക്കുക, അനുയോജ്യമായ ഫംഗിസൈഡുകൾ പ്രയോഗിക്കുക."
            }
        }
        
        self.market_info = {
            "tomato": {
                "current_price": "₹30-45 per kg",
                "forecast": "Prices expected to rise by 10-15% due to seasonal demand",
                "best_markets": ["APMC Bangalore", "Azadpur Delhi", "Vashi Mumbai"]
            },
            "potato": {
                "current_price": "₹20-30 per kg", 
                "forecast": "Stable prices expected for next month",
                "best_markets": ["Agra APMC", "Patna Market", "Kolkata APMC"]
            }
        }
        
        self.government_schemes = {
            "en": [
                "PM-KISAN: Direct income support of ₹6000 per year",
                "Soil Health Card Scheme: Free soil testing",
                "Pradhan Mantri Fasal Bima Yojana: Crop insurance",
                "MNREGA: Rural employment guarantee",
                "Kisan Credit Card: Easy agricultural loans"
            ],
            "hi": [
                "पीएम-किसान: प्रति वर्ष ₹6000 प्रत्यक्ष आय सहायता",
                "मृदा स्वास्थ्य कार्ड योजना: मुफ्त मिट्टी परीक्षण", 
                "प्रधानमंत्री फसल बीमा योजना: फसल बीमा",
                "मनरेगा: ग्रामीण रोजगार गारंटी",
                "किसान क्रेडिट कार्ड: आसान कृषि ऋण"
            ],
            "ml": [
                "പിഎം-കിസാൻ: വർഷത്തിൽ ₹6000 നേരിട്ടുള്ള വരുമാന പിന്തുണ",
                "മണ്ണ് ആരോഗ്യ കാർഡ് പദ്ധതി: സൗജന്യ മണ്ണ് പരിശോധന",
                "പ്രധാനമന്ത്രി ഫസൽ ബീമാ യോജന: കാർഷിക ബീമാ",
                "മൻരേഗ: ഗ്രാമീണ തൊഴിൽ ഗ്യാരണ്ടി",
                "കിസാൻ ക്രെഡിറ്റ് കാർഡ്: എളുപ്പമുള്ള കാർഷിക വായ്പകൾ"
            ]
        }

        # Local brand suggestions (examples) for South Indian states by disease
        # Keys will be (state_code, disease_name)
        self.local_brands = {
            ("KL", "Leaf smut"): [
                {"brand": "Tilt 250 EC", "molecule": "Propiconazole 25% EC", "dose": "1 ml/L"},
                {"brand": "Folicur 25 EC", "molecule": "Tebuconazole 25% EC", "dose": "1 ml/L"}
            ],
            ("TN", "Leaf smut"): [
                {"brand": "Score 250 EC", "molecule": "Difenoconazole 25% EC", "dose": "0.5 ml/L"}
            ],
            ("AP", "Leaf smut"): [
                {"brand": "Tilt 250 EC", "molecule": "Propiconazole 25% EC", "dose": "1 ml/L"}
            ],
            ("TS", "Leaf smut"): [
                {"brand": "Folicur 25 EC", "molecule": "Tebuconazole 25% EC", "dose": "1 ml/L"}
            ]
        }

    def infer_crop_from_detection(self, disease_name: str, model_key: Optional[str] = None) -> str:
        """Derive a display crop name from model output (e.g. PlantVillage labels) and model task."""
        d = (disease_name or "").strip()
        if not d:
            return "Crop"
        if "___" in d:
            part = d.split("___")[0].strip()
            return part.replace("_", " ").title()
        if "_" in d and d.lower() not in ("leaf smut", "model not available"):
            return d.split("_")[0].replace("_", " ").title()
        mk = (model_key or "").lower()
        if mk == "rice":
            return "Rice"
        if mk == "cotton":
            return "Cotton"
        if mk == "banana":
            return "Banana"
        return "Crop"

    def _state_from_location(self, location: Optional[str]) -> Optional[str]:
        if not location:
            return None
        loc = (location or "").strip().lower()
        if any(s in loc for s in ["kerala", "kl"]):
            return "KL"
        if any(s in loc for s in ["tamil", "tn"]):
            return "TN"
        if any(s in loc for s in ["karnataka", "ka"]):
            return "KA"
        if any(s in loc for s in ["andhra", "ap"]):
            return "AP"
        if any(s in loc for s in ["telangana", "ts"]):
            return "TS"
        return None

    def get_disease_advisory(
        self,
        disease_name: str,
        language: str = "en",
        location: Optional[str] = None,
        crop_name: Optional[str] = None,
    ) -> str:
        """
        Full Telangana-oriented structured advisory after disease detection - OPTIMIZED.
        Uses crop_name + disease_name + location (defaults to Telangana, India).
        SINGLE API call - includes language instruction in prompt to avoid separate translation.
        """
        try:
            logger.info(f"💡 [ADVISORY] 📝 Generating disease advisory")
            logger.info(f"[ADVISORY] Disease: {disease_name}, Crop: {crop_name}, Language: {language}")
            
            crop = (crop_name or self.infer_crop_from_detection(disease_name)).strip() or "Crop"
            loc = (location or "").strip() or "Telangana, India"
            if "telangana" not in loc.lower():
                loc = f"{loc}, Telangana, India" if loc else "Telangana, India"

            lang_map = {
                "en": "English",
                "hi": "Hindi (हिंदी)",
                "ml": "Malayalam (മലയാളം)",
                "te": "Telugu (తెలుగు)"
            }
            target_lang = lang_map.get(language, "English")

            system_role = f"""You are an expert agricultural advisor specialized in Indian farming, especially Telangana region practices. Generate response in {target_lang} ONLY. Do not include any English text or translation notes.
Given a detected crop disease, generate a COMPLETE and PRACTICAL solution. Your response MUST be accurate, structured, and useful for farmers.
"""

            prompt = f"""{system_role}

INPUT:
Crop Name: {crop}
Detected Disease: {disease_name}
Location: {loc}
Response Language: {target_lang}

Provide structured advisory with numbered sections (1, 2, 3, etc.) and sub-points (A, B, C). Keep response practical and farmer-friendly. No asterisks or markdown. Plain text only.

Key sections:
1. Disease Name and Type
2. Cause and Symptoms  
3. Solution (Cultural practices, Chemical control, Telangana brands, Fertilizer advice)
4. Chemical Composition and Application
5. Safety Precautions
6. Crop Recommendations
"""

            logger.info(f"[ADVISORY] ⏳ Calling Gemini for {target_lang} advisory...")
            # Single API call with language built into prompt
            ai_advisory = gemini_client.ask_gemini(prompt, language)
            
            if not ai_advisory or "Error" in ai_advisory:
                logger.error(f"[ADVISORY] ❌ Failed to generate advisory")
                return ai_advisory
            
            result = self._preserve_structure_clean(ai_advisory)
            logger.info(f"[ADVISORY] ✅ Advisory generated ({len(result)} chars)")
            logger.info(f"[ADVISORY] 📄 Preview: {result[:150]}...")
            return result

        except Exception as e:
            logger.error(f"[ADVISORY] ❌ Disease advisory error: {e}")
            return f"Error generating advisory: {str(e)[:100]}"

    def get_healthy_crop_advice(self, crop_name: str, language: str = "en") -> str:
        """Get advice for healthy crops - OPTIMIZED with single API call"""
        try:
            crop = crop_name.split("___")[0] if "___" in crop_name else crop_name
            
            lang_map = {
                "en": "English",
                "hi": "Hindi (हिंदी)",
                "ml": "Malayalam (മലയാളം)",
                "te": "Telugu (తెలుగు)"
            }
            target_lang = lang_map.get(language, "English")
            
            prompt = f"""Respond in {target_lang} ONLY. Do not include English text.

The {crop} crop appears healthy. As an agricultural expert, provide simple, practical advice in plain text format.

Include:
1. How to keep it healthy (2 simple practices)
2. Warning signs to watch for (2 early symptoms)
3. Harvest timing (best stage and month)
4. Post-harvest care (1-2 tips)

Keep response under 150 words. Use simple language. No markdown."""
            
            ai_advisory = gemini_client.ask_gemini(prompt, language)
            return self._clean_text(ai_advisory)
            
        except Exception as e:
            logger.error(f"Healthy crop advice error: {e}")
            return f"Keep your crop well-maintained with proper irrigation and pest monitoring."

    def get_organic_farming_advisory(
        self,
        crop_name: str,
        language: str = "en",
        location: Optional[str] = None,
    ) -> str:
        """
        Structured organic & sustainable farming guide for Telangana - OPTIMIZED.
        No chemical pesticides/fertilizers. SINGLE API call with language in prompt.
        """
        try:
            crop = (crop_name or "").strip() or "Crop"
            loc = (location or "").strip() or "Telangana, India"
            if "telangana" not in loc.lower():
                loc = f"{loc}, Telangana, India" if loc else "Telangana, India"

            lang_map = {
                "en": "English",
                "hi": "Hindi (हिंदी)",
                "ml": "Malayalam (മലയാളം)",
                "te": "Telugu (తెలుగు)"
            }
            target_lang = lang_map.get(language, "English")

            system_role = f"""You are an expert in organic and sustainable agriculture in India, especially Telangana farming practices. Respond in {target_lang} ONLY. Do not include English text or translation notes.
Generate practical, detailed Organic Farming Techniques. Recommend ONLY organic, biological, and natural approaches. NO synthetic chemical pesticides or fertilizers.
"""

            prompt = f"""{system_role}

Crop: {crop}
Location: {loc}
Response Language: {target_lang}

Provide structured guide with numbered sections (1, 2, 3, etc.) and sub-points (A, B, C):

1. Suitable Soil & Climate
2. Organic Farming Practices (Soil prep, Seed treatment, Nutrients, Pests/Disease, Weeds, Water)
3. Telangana-Specific Organic Inputs
4. Crop-wise Practical Tips 
5. Expected Yield & Benefits
6. Key Do's and Don'ts

Keep response practical and farmer-friendly. Plain text only. No asterisks or markdown.
"""

            # Single API call
            ai_text = gemini_client.ask_gemini(prompt, language)
            return self._preserve_structure_clean(ai_text)

        except Exception as e:
            logger.error(f"Organic farming error: {e}")
            return f"Error generating organic farming guide: {str(e)[:100]}"

    def get_comprehensive_advisory(self, crop_name: str, location: str, 
                                 soil_type: str, query: str, language: str = "en") -> str:
        """Generate comprehensive farming advisory - OPTIMIZED"""
        try:
            # Check cache first (quick optimization)
            cache_key = f"{crop_name}_{location}_{soil_type}_{language}".lower()
            
            # Create prompt that includes language instruction to avoid separate translation call
            lang_prefix = "Provide response in"
            lang_map = {
                "en": "English",
                "hi": "Hindi (हिंदी)",
                "ml": "Malayalam (മലയാളം)",
                "te": "Telugu (తెలుగు)"
            }
            target_lang = lang_map.get(language, "English")
            
            prompt = f"""Provide response in {target_lang} only. Do not include any English text.

As an agricultural expert, provide simple advice for:

Crop: {crop_name} | Location: {location} | Soil: {soil_type}
Question: {query}

Keep response under 150 words and include:
1. Direct answer to question (2-3 points)
2. What to do (2-3 easy action steps)
3. Important tips (2 key reminders)

Use simple, practical language. No bullet points or markdown - just plain text."""
            
            # Single API call with language instruction included
            ai_advisory = gemini_client.ask_gemini(prompt, language)
            return self._clean_text(ai_advisory)
            
        except Exception as e:
            logger.error(f"Error in advisory: {e}")
            return f"Please try again. Error: {str(e)[:50]}"

    def get_market_advisory(self, crop_name: str, location: str, language: str = "en") -> str:
        """Get market price and selling advice"""
        try:
            prompt = f"""
            As a market analyst and agricultural expert, provide simple market advice for:
            
            Crop: {crop_name}
            Location: {location}
            
            Keep response under 100 words and include only:
            1. Current price range (simple numbers)
            2. Best time to sell (1-2 simple tips)
            3. How to get better price (2-3 easy steps)
            
            Use simple language that farmers can easily understand. Focus on maximizing farmer income.
            """
            
            ai_advisory = gemini_client.ask_gemini(prompt, language)
            translated = gemini_client.translate_text(self._clean_text(ai_advisory), language)
            return self._clean_text(translated)
            
        except Exception as e:
            return f"Error generating market advisory: {str(e)}"

    def get_weather_advisory(self, location: str, crop_name: str, language: str = "en") -> str:
        """Get weather-based farming advice"""
        try:
            prompt = f"""
            As a weather and agriculture expert, provide simple weather advice for:
            
            Location: {location}
            Crop: {crop_name}
            
            Keep response under 100 words and include only:
            1. How weather affects the crop (1-2 simple points)
            2. What to do now (2-3 easy steps)
            3. How to protect from bad weather (1-2 simple tips)
            
            Use simple language that farmers can easily understand. Provide practical weather-based farming tips.
            """
            
            ai_advisory = gemini_client.ask_gemini(prompt, language)
            return ai_advisory
            
        except Exception as e:
            return f"Error generating weather advisory: {str(e)}"

    def _get_language_name(self, code: str) -> str:
        """Convert language code to full name"""
        lang_map = {
            "en": "English",
            "hi": "Hindi (हिंदी)", 
            "ml": "Malayalam (മലയാളം)",
            "te": "Telugu (తెలుగు)",
            "ta": "Tamil (தமிழ்)",
            "kn": "Kannada (ಕನ್ನಡ)"
        }
        return lang_map.get(code, "English")
    
    def _preserve_structure_clean(self, text: str) -> str:
        """Strip markdown only; keep numbered sections and bullets for disease advisories."""
        if not text:
            return ""
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        text = re.sub(r'`(.*?)`', r'\1', text)
        text = re.sub(r'#{1,6}\s*', '', text)
        text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.replace('*', '')
        return text.strip()

    def _clean_text(self, text: str) -> str:
        """Remove all formatting symbols and clean text for voice output"""
        if not text:
            return ""
        
        # Remove markdown formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove **bold**
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # Remove *italic*
        text = re.sub(r'`(.*?)`', r'\1', text)        # Remove `code`
        text = re.sub(r'#{1,6}\s*', '', text)         # Remove headers
        text = re.sub(r'^\s*[-*+]\s*', '', text, flags=re.MULTILINE)  # Remove bullet points
        text = re.sub(r'^\s*\d+\.\s*', '', text, flags=re.MULTILINE)  # Remove numbered lists
        
        # Remove other symbols
        text = re.sub(r'[#*_`~]', '', text)           # Remove markdown symbols
        text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)  # Remove links, keep text
        
        # Clean up whitespace
        text = re.sub(r'\n\s*\n', '\n', text)         # Remove multiple newlines
        text = re.sub(r'^\s+|\s+$', '', text, flags=re.MULTILINE)  # Trim lines
        text = text.replace('*', '')
        
        return text.strip()

    def get_farming_options_by_season(self, location: str, soil_type: str, season: str,
                                     language: str = "en") -> Dict[str, Any]:
        """Generate multiple farming options with tips based on season, soil type, and region"""
        try:
            lang_map = {
                "en": "English",
                "hi": "Hindi (हिंदी)",
                "ml": "Malayalam (മലയാളം)",
                "te": "Telugu (తెലుగు)"
            }
            target_lang = lang_map.get(language, "English")
            
            season_names = {
                "kharif": "Kharif (Monsoon/Rainy - June to October)",
                "rabi": "Rabi (Winter - October to March)",
                "summer": "Summer (March to June)",
                "spring": "Spring"
            }
            
            prompt = f"""Respond in {target_lang} only. As an agricultural expert for Telangana region, provide 3-4 BEST CROP OPTIONS for farmers based on:

Location: {location}
Soil Type: {soil_type}
Season: {season_names.get(season, season)}

For EACH crop option, provide:
1. Crop Name
2. Why it suits this season/soil
3. Key farming tips (3-4 practical tips)
4. Expected yield range
5. Market demand

Format each option clearly with the crop name first, then details.
Make it practical and actionable for farmers. Include local crop varieties if relevant to Telangana."""

            ai_response = gemini_client.ask_gemini(prompt, language)
            
            # Parse response into structured farming options
            options = self._parse_farming_options(self._clean_text(ai_response))
            
            return {
                "season": season_names.get(season, season),
                "soil_type": soil_type,
                "location": location,
                "options": options,
                "language": language
            }
            
        except Exception as e:
            logger.error(f"Error generating farming options: {e}")
            return {
                "season": season,
                "soil_type": soil_type,
                "location": location,
                "options": [],
                "error": str(e)[:100]
            }

    def _parse_farming_options(self, text: str) -> List[Dict[str, str]]:
        """Parse AI response into structured farming options"""
        try:
            options = []
            # Split by crop names or numbered patterns
            sections = re.split(r'\n(?=\d+\.|Crop:|[A-Z][a-z]+\s*:)', text)
            
            for section in sections:
                if len(section.strip()) > 20:  # Skip very short sections
                    lines = section.strip().split('\n')
                    if lines:
                        # First line is often the crop name
                        option = {
                            "crop": lines[0][:100] if lines else "Options",
                            "details": '\n'.join(lines[1:])[:500] if len(lines) > 1 else section[:500]
                        }
                        if option["crop"].strip() and option["details"].strip():
                            options.append(option)
            
            return options[:4]  # Return max 4 options
        except Exception as e:
            logger.error(f"Error parsing farming options: {e}")
            return []

# Global instance
advisory_service = AdvisoryService()

# Export functions for backward compatibility
def get_disease_advisory(
    disease_name: str,
    language: str = "en",
    location: Optional[str] = None,
    crop_name: Optional[str] = None,
) -> str:
    return advisory_service.get_disease_advisory(disease_name, language, location, crop_name)

def get_healthy_crop_advice(crop_name: str, language: str = "en") -> str:
    return advisory_service.get_healthy_crop_advice(crop_name, language)

def get_comprehensive_advisory(crop_name: str, location: str, soil_type: str, 
                             query: str, language: str = "en") -> str:
    return advisory_service.get_comprehensive_advisory(crop_name, location, soil_type, query, language)

def get_organic_farming_advisory(
    crop_name: str,
    language: str = "en",
    location: Optional[str] = None,
) -> str:
    return advisory_service.get_organic_farming_advisory(crop_name, language, location)


def infer_crop_from_detection(disease_name: str, model_key: Optional[str] = None) -> str:
    return advisory_service.infer_crop_from_detection(disease_name, model_key)

def get_farming_options_by_season(location: str, soil_type: str, season: str,
                                 language: str = "en") -> Dict[str, Any]:
    """Generate farming options based on season, soil type, and region"""
    return advisory_service.get_farming_options_by_season(location, soil_type, season, language)