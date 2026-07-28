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
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(clothing.router)
app.include_router(outfits.router)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR), check_dir=False), name="uploads")


@app.get("/api/health")
def health():
    return {"status": "ok"}
