import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1) Cargar .env desde la raíz del proyecto
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("Falta GOOGLE_API_KEY")

genai.configure(api_key=API_KEY)
_MODEL = genai.GenerativeModel("gemini-2.5-flash")

def analizar_sentimiento(texto: str) -> str:
    """
    Devuelve: 'positivo' | 'negativo' | 'neutro'
    """
    prompt = (
        "Clasifica el sentimiento del siguiente texto como exactamente una palabra: "
        "'positivo', 'negativo' o 'neutro'. Responde solo con una de esas tres palabras.\n\n"
        f"Texto: {texto}"
    )
    resp = _MODEL.generate_content(prompt)
    raw = (getattr(resp, "text", "") or "").strip().lower()

    if "positivo" in raw:
        return "positivo"
    if "negativo" in raw:
        return "negativo"
    if "neutro" in raw:
        return "neutro"
    return "neutro"
