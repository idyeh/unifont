from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import get_connection, init_db
from app.routers import font_config, fonts, unicode
from app.services.unicode_service import seed_unicode_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    with get_connection() as connection:
        seed_unicode_data(connection)
    yield


app = FastAPI(title="Unicode Font Browser API", version="0.1.0", lifespan=lifespan)

origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(unicode.router)
app.include_router(fonts.router)
app.include_router(font_config.router)
