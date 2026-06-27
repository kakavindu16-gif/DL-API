from __future__ import annotations

import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import engine  # api/engine.py

# ─────────────────────────────────────────────
#  App setup
# ─────────────────────────────────────────────
app = FastAPI(
    title="Syntiox Smart DL API",
    description="An API that provides direct download links along with video details",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
#  Request Models
# ─────────────────────────────────────────────
class InfoRequest(BaseModel):
    url: str

# ─────────────────────────────────────────────
#  Routes
# ─────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    """API health check."""
    return {"status": "ok", "service": "Syntiox DL API", "version": "2.0.0"}


@app.get("/ffmpeg", tags=["Health"])
def ffmpeg_check():
    """Check whether ffmpeg is available on the server."""
    ok = engine.check_ffmpeg()
    return {"ffmpeg_available": ok}


@app.post("/info", tags=["Info"])
def get_info(body: InfoRequest):
    """
    Provide a YouTube URL to get direct download links along with video details (Thumbnail, Title).
    """
    result = engine.get_info(body.url)
    if result.get("type") == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    # Map the raw URLs to the expected keys for the client
    if "best_video" in result:
        result["best_video_download_url"] = result.pop("best_video")
    if "best_audio" in result:
        result["audio_download_url"] = result.pop("best_audio")
        
    if "formats" in result:
        for fmt in result["formats"]:
            fmt["download_url"] = fmt.get("url", "")

    return result
