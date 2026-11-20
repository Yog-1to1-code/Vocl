from functools import lru_cache

from google import genai

from app.config import GEMINI_API_KEY


@lru_cache(maxsize=1)
def gemini_client() -> genai.Client:
    # Created lazily so mock mode boots without an API key
    return genai.Client(api_key=GEMINI_API_KEY)
