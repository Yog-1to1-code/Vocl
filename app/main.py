import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import USE_MOCK_AI
from app.routers import api, ws
from app.services.csv_storage import ensure_csv_exists

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="Vocl", description="Audio-first technical interview simulator", version="0.1.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(api.router)
app.include_router(ws.router)


@app.get("/dev-test", include_in_schema=False)
async def dev_test_page() -> FileResponse:
    return FileResponse(_STATIC_DIR / "dev-test.html")


app.mount("/", StaticFiles(directory=str(_STATIC_DIR), html=True), name="static")

ensure_csv_exists()
logging.getLogger(__name__).info("Vocl AI mode: %s", "MOCK" if USE_MOCK_AI else "LIVE")
