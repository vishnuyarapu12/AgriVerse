import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import Optional, Dict, Any
import json
import logging
import time

# Configure logging
logger = logging.getLogger(__name__)

load_dotenv()

# Try both API_KEY and GEMINI_API_KEY for compatibility
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    logger.warning(
        "GEMINI_API_KEY not set. Gemini features (advisory, TTS, translate) will fail until .env is configured."
    )

# Use Gemini 2.5 Pro model
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")

def ask_gemini(query: str, language: str = "en") -> str:
    """
    Enhanced Gemini client with language support for agricultural advisory
    FIXED: Strictly enforces response language using system prompt and explicit instructions
    ADDED: Response time logging for performance monitoring
    """
    try:
        start_time = time.time()
        logger.info(f"🤖 [GEMINI] 📤 Calling {MODEL_NAME} API for language: {language}")
        logger.info(f"[GEMINI] Query: {query[:100]}..." if len(query) > 100 else f"[GEMINI] Query: {query}")
        
        logger.info(f"[GEMINI] Model selected: {MODEL_NAME}")
        model = genai.GenerativeModel(MODEL_NAME)
        logger.info(f"[GEMINI] ✅ Model loaded successfully")
        
        # Add STRICT language-specific context to the prompt
        language_context = _get_language_context(language)
        
        # Enhanced query with strict language enforcement
        enhanced_query = f"""{language_context}

QUERY:
{query}

STRICT INSTRUCTIONS:
1. Respond ONLY in {_get_language_name(language)} language
2. Do NOT mix languages
3. Do NOT include any English text or translation notes
4. Do NOT add any meta-information or disclaimers
5. Return ONLY the response text in the target language"""
        
        logger.info(f"[GEMINI] ⏳ Waiting for response (timeout: 30s)...")
        response = model.generate_content(enhanced_query, request_options={"timeout": 30})
        
        elapsed_time = time.time() - start_time
        
        logger.info(f"[GEMINI] Response object received: {type(response)}")
        logger.info(f"[GEMINI] Response status: {getattr(response, 'prompt_feedback', 'N/A')}")
        
        # Extract text from response
        txt = getattr(response, "text", None)
        logger.info(f"[GEMINI] Direct .text attribute: {txt is not None}")
        
        if not txt:
            candidates = getattr(response, "candidates", None)
            logger.info(f"[GEMINI] Candidates available: {candidates is not None}, count: {len(candidates) if candidates else 0}")
            
            if candidates and len(candidates) > 0:
                content = candidates[0].get("content")
                if content and hasattr(content, "parts"):
                    txt = content.parts[0].text if content.parts else None
                else:
                    txt = str(candidates[0])
        
        if not txt:
            logger.error(f"[GEMINI] ❌ No text extracted from response!")
            logger.error(f"[GEMINI] Full response: {response}")
            logger.error(f"[GEMINI] Response __dict__: {getattr(response, '__dict__', 'N/A')}")
            return ""
        
        response_preview = txt[:150] + "..." if len(txt) > 150 else txt
        logger.info(f"[GEMINI] ✅ Response received in {elapsed_time:.2f}s ({len(txt)} chars)")
        logger.info(f"[GEMINI] 📄 Preview: {response_preview}")
        return (txt or "").strip()
    except Exception as e:
        import traceback
        logger.error(f"[GEMINI] ❌ API error for language {language}: {type(e).__name__}: {str(e)}")
        logger.error(f"[GEMINI] Full traceback:\n{traceback.format_exc()}")
        return f"Error: Could not generate advisory in {_get_language_name(language)}"

def ask_gemini_with_context(query: str, context: Dict[str, Any], language: str = "en") -> str:
    """
    Ask Gemini with structured agricultural context
    FIXED: Strictly enforces response language
    ADDED: Response time logging
    """
    try:
        start_time = time.time()
        logger.info(f"🤖 [GEMINI-CTX] 📤 Calling {MODEL_NAME} with context for language: {language}")
        logger.info(f"[GEMINI-CTX] Context keys: {list(context.keys())}")
        
        logger.info(f"[GEMINI-CTX] Model selected: {MODEL_NAME}")
        model = genai.GenerativeModel(MODEL_NAME)
        logger.info(f"[GEMINI-CTX] ✅ Model loaded successfully")
        
        # Build context-aware prompt with strict language enforcement
        context_prompt = _build_context_prompt(query, context, language)
        
        logger.info(f"[GEMINI-CTX] ⏳ Waiting for response (timeout: 30s)...")
        response = model.generate_content(context_prompt, request_options={"timeout": 30})
        
        elapsed_time = time.time() - start_time
        
        logger.info(f"[GEMINI-CTX] Response object received: {type(response)}")
        logger.info(f"[GEMINI-CTX] Response status: {getattr(response, 'prompt_feedback', 'N/A')}")
        
        txt = getattr(response, "text", None)
        logger.info(f"[GEMINI-CTX] Direct .text attribute: {txt is not None}")
        
        if not txt:
            candidates = getattr(response, "candidates", None)
            logger.info(f"[GEMINI-CTX] Candidates available: {candidates is not None}, count: {len(candidates) if candidates else 0}")
            
            if candidates and len(candidates) > 0:
                content = candidates[0].get("content")
                if content and hasattr(content, "parts"):
                    txt = content.parts[0].text if content.parts else None
                else:
                    txt = str(candidates[0])
        
        if not txt:
            logger.error(f"[GEMINI-CTX] ❌ No text extracted from response!")
            logger.error(f"[GEMINI-CTX] Full response: {response}")
            logger.error(f"[GEMINI-CTX] Response __dict__: {getattr(response, '__dict__', 'N/A')}")
            return ""
        
        response_preview = txt[:150] + "..." if len(txt) > 150 else txt
        logger.info(f"[GEMINI-CTX] ✅ Response received in {elapsed_time:.2f}s ({len(txt)} chars)")
        logger.info(f"[GEMINI-CTX] 📄 Preview: {response_preview}")
        return (txt or "").strip()
    except Exception as e:
        import traceback
        logger.error(f"[GEMINI-CTX] ❌ API error for language {language}: {type(e).__name__}: {str(e)}")
        logger.error(f"[GEMINI-CTX] Full traceback:\n{traceback.format_exc()}")
        return f"Error: Could not generate advisory in {_get_language_name(language)}"

def _get_language_name(language: str) -> str:
    """Get language name for display"""
    names = {
        "en": "English",
        "hi": "Hindi (हिंदी)",
        "ml": "Malayalam (മലയാളം)",
        "te": "Telugu (తెలుగు)",
        "ta": "Tamil (தமிழ்)"
    }
    return names.get(language, "English")

def _get_language_context(language: str) -> str:
    """Get language-specific context for better responses - STRICT single-language enforcement"""
    contexts = {
        "en": """You are an expert agricultural advisor. 

CRITICAL RULES:
1. Respond ONLY in English
2. Do NOT include any Hindi, Telugu, Malayalam, Tamil, or any other language
3. Do NOT add translation notes or meta-information
4. Use simple, easy-to-understand language
5. Explain diseases and remedies in simple terms that farmers can easily understand
6. Do not use complex technical terms
7. Return ONLY plain text - no markdown, no bullets, no asterisks""",

        "hi": """आप एक विशेषज्ञ कृषि सलाहकार हैं।

गंभीर नियम:
1. केवल हिंदी में उत्तर दें
2. अंग्रेजी, तेलुगु, मलयालम, तमिल या कोई अन्य भाषा न जोड़ें
3. अनुवाद नोट्स या मेटा-जानकारी न जोड़ें
4. सरल, आसान भाषा का उपयोग करें
5. रोगों और उपचारों को सरल शब्दों में समझाएं
6. जटिल तकनीकी शब्दों का उपयोग न करें
7. केवल सादा पाठ लौटाएं - कोई मार्कडाउन, कोई बुलेट, कोई एस्टरिस्क नहीं""",

        "ml": """നിങ്ങൾ വിദഗ്ധ കാർഷിക ഉപദേഷ്ടാവാണ്.

നിർണായക നിയമങ്ങൾ:
1. മലയാളത്തിൽ മാത്രം മറുപടി നൽകുക
2. ഇംഗ്ലീഷ്, തെലുഗു, തമിഴ് അല്ലെങ്കിൽ മറ്റേതെങ്കിലും ഭാഷ ചേർക്കരുത്
3. വിവർത്തന കുറിപ്പുകൾ അല്ലെങ്കിൽ മെറ്റാ-വിവരങ്ങൾ ചേർക്കരുത്
4. ലളിതവും എളുപ്പത്തിൽ മനസ്സിലാക്കാവുന്ന ഭാഷ ഉപയോഗിക്കുക
5. രോഗങ്ങളും പരിഹാരങ്ങളും ലളിത പദങ്ങളിൽ വിവരിക്കുക
6. സങ്കീർണ്ണമായ സാങ്കേതിക പദങ്ങൾ ഉപയോഗിക്കരുത്
7. സാധാരണ ടെക്സ്റ്റ് മാത്രം നൽകുക - മാർക്ക്ഡൗൺ ഇല്ല, വിരാമചിഹ്നം ഇല്ല""",

        "te": """మీరు నిపుణ వ్యవసాయ సలహాదారు.

సమాలోచన చేయవలసిన నిబంధనలు:
1. తెలుగులో మాత్రమే సమాధానం ఇవ్వండి
2. ఆంగ్లం, హిందీ, మలయాళం, తమిళం లేదా ఇతర భాషలను జోడించవద్దు
3. అనువాద నోట్‌లు లేదా మెటా-సమాచారాన్ని జోడించవద్దు
4. సులభమైన, సరళమైన భాషను ఉపయోగించండి
5. వ్యాధులు మరియు నివారణలను సరళ పదాలలో వివరించండి
6. సంక్లిష్టమైన సాంకేతిక పదాలను ఉపయోగించవద్దు
7. సాధారణ పాఠ్యమాత్రమే చేర్చండి - మార్కడౌన్ లేదు, బుల్లెట్‌లు లేదు"""
    }
    return contexts.get(language, contexts["en"])

def _build_context_prompt(query: str, context: Dict[str, Any], language: str) -> str:
    """Build a structured prompt with agricultural context and STRICT language enforcement"""
    language_context = _get_language_context(language)
    language_name = _get_language_name(language)
    
    context_info = ""
    if context:
        context_info = "\n\nContext Information:\n"
        for key, value in context.items():
            if value:
                context_info += f"- {key.replace('_', ' ').title()}: {value}\n"
    
    return f"""{language_context}

{context_info}

FARMER'S QUERY: {query}

INSTRUCTIONS FOR RESPONSE:
1. Respond ONLY in {language_name}
2. Do NOT use any other language
3. Provide simple, practical advice (under 100 words)
4. Use plain text only - no bullets, no markdown, no asterisks
5. Make response direct and actionable
6. Keep language suitable for 1 minute audio reading
7. Use simple language that farmers can easily understand
8. Do NOT add any English text or translation notes
9. Respond ONLY in the target language"""


def translate_text(text: str, target_language: str, preserve_structure: bool = False) -> str:
    """Translate given text to target_language as plain text only, no formatting.
    ADDED: Response time logging for performance monitoring"""
    try:
        start_time = time.time()
        model = genai.GenerativeModel(MODEL_NAME)
        lang_context = _get_language_context(target_language)
        language_name = _get_language_name(target_language)
        extra = ""
        if preserve_structure:
            extra = (
                " Preserve all section numbers (1-8), headings, labels (A-D), and line breaks exactly. "
                "Do not merge sections.\n"
            )
        prompt = (
            f"{lang_context}\n\n"
            f"Translate the following to {language_name}. Return ONLY plain text in {language_name}.\n"
            f"Do not add or remove content. Do not include explanations or translation metadata.{extra}\n"
            f"Text:\n{text}"
        )
        response = model.generate_content(prompt, request_options={"timeout": 30})
        
        elapsed_time = time.time() - start_time
        logger.info(f"Translation completed in {elapsed_time:.2f}s to {language_name}")
        
        txt = getattr(response, "text", None)
        if not txt:
            candidates = getattr(response, "candidates", None)
            if candidates and len(candidates) > 0:
                content = candidates[0].get("content")
                if content and hasattr(content, "parts"):
                    txt = content.parts[0].text if content.parts else None
                else:
                    txt = str(candidates[0])
        return (txt or "").strip()
    except Exception as e:
        logger.error(f"Translation error to {target_language}: {type(e).__name__}: {str(e)}")
        return text  # Return original text on translation failure
