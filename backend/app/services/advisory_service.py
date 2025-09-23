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
            "Bacterial leaf blight": {
                "en": "Bacterial leaf blight is caused by Xanthomonas oryzae. Use copper-based fungicides, ensure proper drainage, and practice crop rotation.",
                "hi": "बैक्टीरियल लीफ ब्लाइट Xanthomonas oryzae के कारण होता है। कॉपर आधारित फंगिसाइड का उपयोग करें, उचित जल निकासी सुनिश्चित करें।",
                "ml": "ബാക്ടീരിയൽ ലീഫ് ബ്ലൈറ്റ് Xanthomonas oryzae എന്ന ബാക്ടീരിയയാൽ ഉണ്ടാകുന്നു. ചെമ്പ് അടിസ്ഥാന ഫംഗിസൈഡുകൾ ഉപയോഗിക്കുക, ഉചിതമായ ജലനിർഗ്ഗമനം ഉറപ്പാക്കുക।"
            },
            "Brown spot": {
                "en": "Brown spot is a fungal disease caused by Bipolaris oryzae. Improve nutrition, ensure good field hygiene, and apply fungicides.",
                "hi": "ब्राउन स्पॉट Bipolaris oryzae के कारण होने वाली फंगल बीमारी है। पोषण में सुधार करें, अच्छी फील्ड स्वच्छता सुनिश्चित करें।",
                "ml": "ബ്രൗൺ സ്പോട്ട് Bipolaris oryzae എന്ന ഫംഗസ് മൂലമുണ്ടാകുന്ന രോഗമാണ്. പോഷണം മെച്ചപ്പെടുത്തുക, നല്ല ഫീൽഡ് ശുചിത്വം ഉറപ്പാക്കുക।"
            },
            "Leaf smut": {
                "en": "Leaf smut is caused by Ustilaginoidea virens fungus. Improve drainage, ensure proper spacing, and apply fungicide treatment.",
                "hi": "लीफ स्मट Ustilaginoidea virens फंगस के कारण होता है। जल निकासी में सुधार करें, उचित दूरी सुनिश्चित करें।",
                "ml": "ലീഫ് സ്മട്ട് Ustilaginoidea virens ഫംഗസ് മൂലമുണ്ടാകുന്നു. ജലനിർഗ്ഗമനം മെച്ചപ്പെടുത്തുക, ഉചിതമായ ഇടവേള ഉറപ്പാക്കുക।"
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

    def get_disease_advisory(self, disease_name: str, language: str = "en") -> str:
        """Get disease-specific treatment advisory"""
        try:
            # Check if we have predefined treatment
            if disease_name in self.disease_treatments:
                base_treatment = self.disease_treatments[disease_name].get(language, 
                    self.disease_treatments[disease_name]["en"])
            else:
                base_treatment = f"Disease detected: {disease_name}"
            
            # Enhance with AI advisory - concise version
            prompt = f"""
            As an agricultural expert, provide concise treatment advice for {disease_name} in {self._get_language_name(language)}.
            
            Keep response under 200 words and include only:
            1. Disease causes (2-3 points)
            2. Immediate remedies (3-4 steps)
            3. Prevention tips (2-3 points)
            
            Make it practical and suitable for 1-2 minute audio reading.
            """
            
            ai_advisory = gemini_client.ask_gemini(prompt)
            
            # Clean the response - remove all formatting symbols
            clean_advisory = self._clean_text(ai_advisory)
            clean_base = self._clean_text(base_treatment)
            
            return f"{clean_base}\n\n{clean_advisory}"
            
        except Exception as e:
            return f"Error generating advisory: {str(e)}"

    def get_healthy_crop_advice(self, crop_name: str, language: str = "en") -> str:
        """Get advice for healthy crops"""
        try:
            crop = crop_name.split("___")[0] if "___" in crop_name else crop_name
            
            prompt = f"""
            The {crop} crop appears healthy. As an agricultural expert, provide concise advice in {self._get_language_name(language)}.
            
            Keep response under 150 words and include only:
            1. Health maintenance tips (2-3 points)
            2. Preventive measures (2-3 points)
            3. Harvest timing (1-2 points)
            
            Make it suitable for 1-2 minute audio reading.
            """
            
            ai_advisory = gemini_client.ask_gemini(prompt)
            return self._clean_text(ai_advisory)
            
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
            
            # Create concise prompt for AI
            prompt = f"""
            As an agricultural expert, provide concise advice in {self._get_language_name(language)} for:
            
            Crop: {crop_name} | Location: {location} | Soil: {soil_type}
            Question: {query}
            
            Keep response under 250 words and include only:
            1. Direct answer to question (2-3 points)
            2. Practical steps (3-4 actions)
            3. Important precautions (2-3 points)
            
            Make it suitable for 1-2 minute audio reading. Be practical and actionable.
            """
            
            ai_advisory = gemini_client.ask_gemini(prompt)
            return self._clean_text(ai_advisory)
            
        except Exception as e:
            return f"Error generating comprehensive advisory: {str(e)}"

    def get_market_advisory(self, crop_name: str, location: str, language: str = "en") -> str:
        """Get market price and selling advice"""
        try:
            prompt = f"""
            As a market analyst and agricultural expert, provide market advisory for:
            
            Crop: {crop_name}
            Location: {location}
            
            Include:
            1. Current market prices and trends
            2. Best time to sell
            3. Quality parameters that affect pricing
            4. Nearby market recommendations
            5. Transportation and storage tips
            6. Price negotiation strategies
            
            Respond in {self._get_language_name(language)} language.
            Focus on maximizing farmer income.
            """
            
            ai_advisory = gemini_client.ask_gemini(prompt)
            return ai_advisory
            
        except Exception as e:
            return f"Error generating market advisory: {str(e)}"

    def get_weather_advisory(self, location: str, crop_name: str, language: str = "en") -> str:
        """Get weather-based farming advice"""
        try:
            prompt = f"""
            As a weather and agriculture expert, provide weather-based advice for:
            
            Location: {location}
            Crop: {crop_name}
            
            Include:
            1. Current weather impact on the crop
            2. Upcoming weather precautions
            3. Irrigation recommendations
            4. Protection measures for extreme weather
            5. Optimal timing for farming activities
            
            Respond in {self._get_language_name(language)} language.
            Provide practical weather-based farming tips.
            """
            
            ai_advisory = gemini_client.ask_gemini(prompt)
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