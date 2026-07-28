import logging
import os
from contextlib import asynccontextmanager

from database import Base, engine
from fastapi import FastAPI, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from routers import auth, clothing, outfits
from upload import UPLOAD_DIR

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, FastAPIHTTPException):
        return await http_exception_handler(request, exc)

    logger.exception("Unhandled exception: %s", exc)

    is_production = os.environ.get("APP_ENV", "").lower() == "production"
    if is_production:
        return JSONResponse(
            status_code=500,
            content={"detail": "Interner Serverfehler"},
        )
    raise exc


app.include_router(auth.router)
app.include_router(clothing.router)
app.include_router(outfits.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


static_dir = os.environ.get("STATIC_DIR", "../frontend/dist")
if os.path.isdir(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if UPLOAD_DIR.is_dir():
    app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
