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
    """Get language-specific context for better responses (strict single-language, plain text, simple terms)."""
    contexts = {
        "en": "You are an expert agricultural advisor. Respond ONLY in English using simple, easy-to-understand language. Use plain text only. Explain diseases and remedies in simple terms that farmers can easily understand. Do not use complex technical terms.",
        "hi": "आप एक विशेषज्ञ कृषि सलाहकार हैं। केवल हिंदी में सरल, आसान भाषा में उत्तर दें। रोगों और उपचारों को सरल शब्दों में समझाएं जो किसान आसानी से समझ सकें। जटिल तकनीकी शब्दों का उपयोग न करें।",
        "ml": "നിങ്ങൾ വിദഗ്ധ കാർഷിക ഉപദേഷ്ടാവാണ്. മലയാളത്തിൽ മാത്രം ലളിതവും എളുപ്പത്തിൽ മനസ്സിലാക്കാവുന്ന ഭാഷയിൽ മറുപടി നൽകുക. രോഗങ്ങളും പരിഹാരങ്ങളും കർഷകർക്ക് എളുപ്പത്തിൽ മനസ്സിലാക്കാവുന്ന ലളിത പദങ്ങളിൽ വിവരിക്കുക. സങ്കീർണ്ണമായ സാങ്കേതിക പദങ്ങൾ ഉപയോഗിക്കരുത്.",
        "te": "మీరు నిపుణ వ్యవసాయ సలహాదారు. తెలుగులో మాత్రమే సరళమైన, సులభంగా అర్థమయ్యే భాషలో సమాధానం ఇవ్వండి. వ్యాధులను మరియు పరిహారాలను రైతులు సులభంగా అర్థం చేసుకోగల సరళ పదాలలో వివరించండి. సంక్లిష్టమైన సాంకేతిక పదాలను వాడకండి."
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

Provide simple, practical advice (under 100 words), plain text only (no bullets/markdown),
direct and actionable, suitable for 1 minute audio reading. Use simple language that farmers can easily understand.
Respond ONLY in the target language. Do not include any English or other languages."""


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
