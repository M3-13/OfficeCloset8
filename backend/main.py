import os
from contextlib import asynccontextmanager

from database import Base, engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import auth, clothing, outfits

from upload import UPLOAD_DIR


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

app.include_router(auth.router)
app.include_router(clothing.router)
app.include_router(outfits.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


if UPLOAD_DIR.exists():
    app.mount("/upload", StaticFiles(directory=str(UPLOAD_DIR)), name="upload")

static_dir = os.environ.get("STATIC_DIR", "../frontend/dist")
if os.path.isdir(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
