from functools import lru_cache

from google import genai

from app.config import GEMINI_API_KEY


@lru_cache(maxsize=1)
def gemini_client() -> genai.Client:
    # Live bidiGenerateContent requires v1beta; lazy init keeps mock mode key-free
    return genai.Client(api_key=GEMINI_API_KEY, http_options={"api_version": "v1beta"})
