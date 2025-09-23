"""
Advanced Advisory Service for comprehensive farming guidance
"""
import os
from typing import Dict, List
from . import gemini_client

class AdvisoryService:
    def __init__(self):
        self.disease_treatments = {
            "Tomato___Late_blight": {
                "en": "Late blight is a serious fungal disease. Use copper-based fungicides, ensure good air circulation, and avoid overhead watering.",
                "hi": "लेट ब्लाइट एक गंभीर फंगल बीमारी है। कॉपर आधारित फंगिसाइड का उपयोग करें, अच्छी हवा का संचार सुनिश्चित करें।",
                "te": "లేట్ బ్లైట్ ఒక తీవ్రమైన ఫంగల్ వ్యాధి. రాగి ఆధారిత శిలీంద్రనాశకాలను ఉపయోగించండి, మంచి గాలి ప్రసరణను నిర్ధారించండి।"
            },
            "Tomato___Bacterial_spot": {
                "en": "Bacterial spot affects leaves and fruits. Use copper sprays, practice crop rotation, and remove affected plant debris.",
                "hi": "बैक्टीरियल स्पॉट पत्तियों और फलों को प्रभावित करता है। कॉपर स्प्रे का उपयोग करें, फसल चक्रीकरण का अभ्यास करें।",
                "te": "బాక్టీరియల్ స్పాట్ ఆకులను మరియు పండ్లను ప్రభావితం చేస్తుంది. రాగి స్ప్రే ఉపయోగించండి, పంట మార్పిడిని అభ్యసించండి।"
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
            "te": [
                "పిఎం-కిసాన్: సంవత్సరానికి ₹6000 ప్రత్యక్ష ఆదాయ మద్దతు",
                "మృత్తిక ఆరోగ్య కార్డ్ పథకం: ఉచిత మట్టి పరీక్ష",
                "ప్రధానమంత్రి ఫసల్ బీమా యోజన: పంట బీమా", 
                "మనరేగా: గ్రామీణ ఉపాధి హామీ",
                "కిసాన్ క్రెడిట్ కార్డ్: సులభ వ్యవసాయ రుణాలు"
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
            
            # Enhance with AI advisory
            prompt = f"""
            As an agricultural expert, provide detailed treatment advice for {disease_name}.
            Include:
            1. Immediate treatment steps
            2. Prevention methods  
            3. Organic alternatives
            4. Expected recovery time
            5. When to consult an agricultural expert
            
            Respond in {self._get_language_name(language)} language.
            Keep the response practical and farmer-friendly.
            """
            
            ai_advisory = gemini_client.ask_gemini(prompt)
            
            return f"{base_treatment}\n\n**Detailed Advisory:**\n{ai_advisory}"
            
        except Exception as e:
            return f"Error generating advisory: {str(e)}"

    def get_healthy_crop_advice(self, crop_name: str, language: str = "en") -> str:
        """Get advice for healthy crops"""
        try:
            crop = crop_name.split("___")[0] if "___" in crop_name else crop_name
            
            prompt = f"""
            The {crop} crop appears healthy. As an agricultural expert, provide advice on:
            1. Maintaining crop health
            2. Optimal harvesting time
            3. Post-harvest handling
            4. Market timing suggestions
            5. Preventive measures for common diseases
            
            Respond in {self._get_language_name(language)} language.
            Keep advice practical and actionable for farmers.
            """
            
            ai_advisory = gemini_client.ask_gemini(prompt)
            return ai_advisory
            
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
            
            # Create comprehensive prompt for AI
            prompt = f"""
            As an expert agricultural advisor, help a farmer with the following details:
            
            Crop: {crop_name}
            Location: {location}  
            Soil Type: {soil_type}
            Farmer's Question: {query}
            
            Provide comprehensive advice covering:
            
            1. **Specific Solution** to the farmer's question
            2. **Crop Management** recommendations for current season
            3. **Soil-specific** advice for {soil_type} soil
            4. **Weather considerations** for {location}
            5. **Pest and Disease Prevention** strategies
            6. **Fertilizer and Nutrition** recommendations
            7. **Water Management** best practices
            8. **Harvesting and Post-harvest** guidance
            
            {market_info}
            
            **Relevant Government Schemes:**
            {schemes_info}
            
            Respond in {self._get_language_name(language)} language.
            Make the advice practical, actionable, and suitable for small-scale farmers.
            Use simple language and provide step-by-step instructions where possible.
            """
            
            ai_advisory = gemini_client.ask_gemini(prompt)
            return ai_advisory
            
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
            "te": "Telugu (తెలుగు)",
            "ta": "Tamil (தமிழ்)",
            "kn": "Kannada (ಕನ್ನಡ)"
        }
        return lang_map.get(code, "English")

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