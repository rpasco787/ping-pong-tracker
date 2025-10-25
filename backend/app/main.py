from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings

app = FastAPI(title="PingPong API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.API_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz")
def health_check():
    return {"ok": True, "service": "pingpong-api"}