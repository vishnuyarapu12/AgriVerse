"""
Advanced Advisory Service for comprehensive farming guidance with Rice Disease Support
"""
import os
import re
from typing import Dict, List, Optional
from . import gemini_client

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

    def get_disease_advisory(self, disease_name: str, language: str = "en", location: Optional[str] = None) -> str:
        """Get disease-specific treatment advisory"""
        try:
            # Check if we have predefined treatment
            if disease_name in self.disease_treatments:
                base_treatment = self.disease_treatments[disease_name].get(language, 
                    self.disease_treatments[disease_name]["en"])
            else:
                base_treatment = f"Disease detected: {disease_name}"
            
            # Enhance with AI advisory - concise (~100 words) and product-focused
            prompt = f"""
            As an agricultural expert, give a short, farmer-friendly advisory for {disease_name} in about 100 words.
            Include:
            - Cause in simple words (1 line)
            - What to do now: 2–3 clear steps (spray/field hygiene/irrigation)
            - Recommend 2–3 effective products by active ingredient with typical dose (e.g., Propiconazole 25% EC – 1 ml/L; Copper Oxychloride 50% WP – 2.5 g/L)
            - One prevention tip (1 line)
            Keep language simple and direct. No bullets or numbering, plain text only.
            """
            
            ai_advisory = gemini_client.ask_gemini(prompt, language)

            # Local brands by state
            state = self._state_from_location(location)
            brand_lines = []
            if state:
                options = self.local_brands.get((state, disease_name), [])
                if options:
                    brand_lines.append("Local products:")
                    for b in options[:5]:
                        brand_lines.append(f"{b['brand']} - {b['molecule']} ({b['dose']})")
            brand_text = ("\n" + "\n".join(brand_lines)) if brand_lines else ""

            combined = f"{base_treatment}\n\n{ai_advisory}{brand_text}"

            # Ensure strict target language
            translated = gemini_client.translate_text(self._clean_text(combined), language)
            return self._clean_text(translated)
            
        except Exception as e:
            return f"Error generating advisory: {str(e)}"

    def get_healthy_crop_advice(self, crop_name: str, language: str = "en") -> str:
        """Get advice for healthy crops"""
        try:
            crop = crop_name.split("___")[0] if "___" in crop_name else crop_name
            
            prompt = f"""
            The {crop} crop appears healthy. As an agricultural expert, provide simple advice.
            
            Keep response under 80 words and include only:
            1. How to keep it healthy (2 simple tips)
            2. What to watch for (1-2 warning signs)
            3. When to harvest (1 simple guideline)
            
            Use simple language that farmers can easily understand.
            """
            
            ai_advisory = gemini_client.ask_gemini(prompt, language)
            translated = gemini_client.translate_text(self._clean_text(ai_advisory), language)
            return self._clean_text(translated)
            
        except Exception as e:
            return f"Error generating healthy crop advice: {str(e)}"

    def get_comprehensive_advisory(self, crop_name: str, location: str, 
                                 soil_type: str, query: str, language: str = "en") -> str:
        """Generate comprehensive farming advisory"""
        try:
            # Get market information if available
            market_data = self.market_info.get(crop_name.lower(), {})
            market_info = ""
            if market_data:
                market_info = f"""
                **Market Information:**
                - Current Price: {market_data.get('current_price', 'N/A')}
                - Forecast: {market_data.get('forecast', 'N/A')}
                - Recommended Markets: {', '.join(market_data.get('best_markets', []))}
                """
            
            # Get government schemes
            schemes = self.government_schemes.get(language, self.government_schemes["en"])
            schemes_info = "\n".join([f"- {scheme}" for scheme in schemes[:3]])
            
            # Create simple prompt for AI
            prompt = f"""
            As an agricultural expert, provide simple advice for:
            
            Crop: {crop_name} | Location: {location} | Soil: {soil_type}
            Question: {query}
            
            Keep response under 100 words and include only:
            1. Direct answer to question (1-2 simple points)
            2. What to do (2-3 easy steps)
            3. Important things to remember (1-2 simple tips)
            
            Use simple language that farmers can easily understand. Be practical and actionable.
            """
            
            ai_advisory = gemini_client.ask_gemini(prompt, language)
            translated = gemini_client.translate_text(self._clean_text(ai_advisory), language)
            return self._clean_text(translated)
            
        except Exception as e:
            return f"Error generating comprehensive advisory: {str(e)}"

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
        
        return text.strip()

# Global instance
advisory_service = AdvisoryService()

# Export functions for backward compatibility
def get_disease_advisory(disease_name: str, language: str = "en") -> str:
    return advisory_service.get_disease_advisory(disease_name, language)

def get_healthy_crop_advice(crop_name: str, language: str = "en") -> str:
    return advisory_service.get_healthy_crop_advice(crop_name, language)

def get_comprehensive_advisory(crop_name: str, location: str, soil_type: str, 
                             query: str, language: str = "en") -> str:
    return advisory_service.get_comprehensive_advisory(crop_name, location, soil_type, query, language)