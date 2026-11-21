from contextlib import asynccontextmanager
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.db.database import dispose_database, init_database
from app.routers import api, auth, ws

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_database()
    logging.getLogger(__name__).info(
        "Vocl started (AI=%s, DB=%s)",
        "MOCK" if settings.USE_MOCK_AI else "LIVE",
        settings.DATABASE_URL,
    )
    yield
    await dispose_database()


app = FastAPI(
    title="Vocl",
    description="Audio-first technical interview simulator",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(api.router)
app.include_router(ws.router)


@app.get("/dev-test", include_in_schema=False)
async def dev_test_page() -> FileResponse:
    return FileResponse(_STATIC_DIR / "dev-test.html")


@app.api_route("/downloads/vocl-release.apk", methods=["GET", "HEAD"], include_in_schema=False)
async def download_release_apk() -> FileResponse:
    # Explicit Android MIME type prevents mobile browsers from appending .zip
    return FileResponse(
        path=_STATIC_DIR / "downloads" / "vocl-release.apk",
        media_type="application/vnd.android.package-archive",
        filename="vocl-release.apk",
    )


app.mount("/", StaticFiles(directory=str(_STATIC_DIR), html=True), name="static")
