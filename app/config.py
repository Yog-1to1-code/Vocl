import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
GEMINI_LIVE_MODEL: str = os.environ.get("GEMINI_LIVE_MODEL", "gemini-2.0-flash-live-001")
GEMINI_REASONING_MODEL: str = os.environ.get("GEMINI_REASONING_MODEL", "gemini-2.5-flash")

SESSION_MAX_DURATION_SEC: int = 900
SYSTEM2_TIMEOUT_SEC: float = 8.0

CSV_PATH: str = os.environ.get("CSV_PATH", "data/sessions.csv")

UPSTREAM_SAMPLE_RATE: int = 16000  # 16 kHz mono PCM from client
DOWNSTREAM_SAMPLE_RATE: int = 24000  # 24 kHz mono PCM to client
