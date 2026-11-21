import os
import sys

from dotenv import load_dotenv

load_dotenv()


def _read_bool(name: str, default: str = "false") -> bool:
    return os.environ.get(name, default).strip().lower() in {"1", "true", "yes", "on"}


USE_MOCK_AI: bool = _read_bool("USE_MOCK_AI")
RECORD_SESSIONS: bool = _read_bool("RECORD_SESSIONS")
PROMPT_MODE: str = os.environ.get("PROMPT_MODE", "prod").strip().lower()

GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
GEMINI_LIVE_MODEL: str = os.environ.get("GEMINI_LIVE_MODEL", "gemini-3.8-live")
GEMINI_REASONING_MODEL: str = os.environ.get("GEMINI_REASONING_MODEL", "gemini-3.1-flash-lite")

SESSION_MAX_DURATION_SEC: int = 900
SYSTEM2_TIMEOUT_SEC: float = float(os.environ.get("SYSTEM2_TIMEOUT_SEC", "3.0"))
FINAL_GRADE_TIMEOUT_SEC: float = float(os.environ.get("FINAL_GRADE_TIMEOUT_SEC", "5.0"))
MOCK_REASONING_LATENCY_SEC: float = 1.5

CSV_PATH: str = os.environ.get("CSV_PATH", "data/sessions.csv")
DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./data/vocl.db")

SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
SUPABASE_PUBLISHABLE_KEY: str = os.environ.get("SUPABASE_PUBLISHABLE_KEY", "").strip()

JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", "vocl-local-dev-secret-change-in-prod-32bytes")
JWT_ALGORITHM: str = os.environ.get("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_HOURS: int = int(os.environ.get("JWT_EXPIRE_HOURS", "168"))
GOOGLE_CLIENT_ID: str = os.environ.get("GOOGLE_CLIENT_ID", "")
DEV_AUTH_BYPASS: bool = _read_bool("DEV_AUTH_BYPASS", "true")
DAILY_QUOTA_MINUTES: float = float(os.environ.get("DAILY_QUOTA_MINUTES", "15.0"))

UPSTREAM_SAMPLE_RATE: int = 16000  # Gemini Live requires 16kHz mono PCM upstream
DOWNSTREAM_SAMPLE_RATE: int = 24000  # Gemini Live emits 24kHz mono PCM

# Alias module so `settings.PROMPT_MODE` or `import app.config as settings` works everywhere
settings = sys.modules[__name__]
