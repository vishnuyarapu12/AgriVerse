import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("⚠️ Please set GEMINI_API_KEY in .env or environment")

genai.configure(api_key=API_KEY)

# Select a model available to your account. Use "gemini-1.5" or the appropriate name.
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-pro")

def ask_gemini(query: str) -> str:
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        # generate_content accepts either prompt or structured request depending on SDK version;
        # the simple call below works for typical text generation.
        response = model.generate_content(query)
        # Different SDKs return different shapes; adapt if yours uses 'candidates' etc.
        # Here we try to extract .text or .content fallback.
        txt = getattr(response, "text", None)
        if not txt:
            # fallback: maybe response.candidates[0].content?
            candidates = getattr(response, "candidates", None)
            if candidates and len(candidates) > 0:
                txt = candidates[0].get("content") or candidates[0].get("text") or str(candidates[0])
        return (txt or "").strip()
    except Exception as e:
        return f"Gemini API error: {str(e)}"
