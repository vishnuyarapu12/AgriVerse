import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import Optional, Dict, Any
import json

load_dotenv()

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("⚠️ Please set GEMINI_API_KEY in .env or environment")

genai.configure(api_key=API_KEY)

# Use Gemini 2.5 Pro model
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")

def ask_gemini(query: str, language: str = "en") -> str:
    """
    Enhanced Gemini client with language support for agricultural advisory
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        
        # Add language-specific context to the prompt
        language_context = _get_language_context(language)
        enhanced_query = f"{language_context}\n\n{query}"
        
        response = model.generate_content(enhanced_query)
        
        # Extract text from response
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
        return f"Gemini API error: {str(e)}"

def ask_gemini_with_context(query: str, context: Dict[str, Any], language: str = "en") -> str:
    """
    Ask Gemini with structured agricultural context
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        
        # Build context-aware prompt
        context_prompt = _build_context_prompt(query, context, language)
        
        response = model.generate_content(context_prompt)
        
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
        return f"Gemini API error: {str(e)}"

def _get_language_context(language: str) -> str:
    """Get language-specific context for better responses (strict single-language, plain text)."""
    contexts = {
        "en": "You are an expert agricultural advisor. Respond ONLY in English. Use plain text only. Do not include any other language, symbols, markdown, bullets, or numbering.",
        "hi": "आप एक विशेषज्ञ कृषि सलाहकार हैं। केवल हिंदी में उत्तर दें। सादा पाठ लिखें। किसी भी अन्य भाषा, प्रतीक, मार्कडाउन, बुलेट या नंबरिंग का उपयोग न करें।",
        "ml": "നിങ്ങൾ വിദഗ്ധ കാർഷിക ഉപദേഷ്ടാവാണ്. മലയാളത്തിൽ മാത്രം മറുപടി നൽകുക. സാധാരണ ടെക്സ്റ്റ് മാത്രം ഉപയോഗിക്കുക. മറ്റ് ഭാഷകൾ, ചിഹ്നങ്ങൾ, മാർക്ക്ഡൗൺ, ബുള്ളറ്റുകൾ, നമ്പറിംഗ് ഒന്നും ഉപയോഗിക്കരുത്."
    }
    return contexts.get(language, contexts["en"])

def _build_context_prompt(query: str, context: Dict[str, Any], language: str) -> str:
    """Build a structured prompt with agricultural context"""
    language_context = _get_language_context(language)
    
    context_info = ""
    if context:
        context_info = "\n\nContext Information:\n"
        for key, value in context.items():
            if value:
                context_info += f"- {key.replace('_', ' ').title()}: {value}\n"
    
    return f"""{language_context}

{context_info}

Farmer's Query: {query}

Provide concise, practical advice (under 200 words), plain text only (no bullets/markdown),
direct and actionable, suitable for 1-2 minute audio reading. Respond ONLY in the target language.
Do not include any English or other languages."""


def translate_text(text: str, target_language: str) -> str:
    """Translate given text to target_language as plain text only, no formatting."""
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        lang_context = _get_language_context(target_language)
        prompt = (
            f"{lang_context}\n\n"
            f"Translate the following to the target language. Return ONLY plain text in the target language.\n"
            f"Do not add or remove content. Do not include explanations.\n\n"
            f"Text:\n{text}"
        )
        response = model.generate_content(prompt)
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
        return f"Gemini API error: {str(e)}"
