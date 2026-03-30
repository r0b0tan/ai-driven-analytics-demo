"""
AI-Driven Analytics Demo — FastAPI entry point.
"""
from __future__ import annotations

import os
import sys

# Ensure backend/ is on the path regardless of how uvicorn is invoked
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from config.llm_config import LLM_MODEL, LLM_PROVIDER
from llm_layer.factory import set_provider

app = FastAPI(
    title="AI-Driven Analytics Demo",
    description="Explainable AI analytics for marketing performance data.",
    version="1.0.0",
)

# CORS — allow Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://aidata.christophbauer.dev"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.on_event("startup")
async def on_startup():
    # Initialize provider from env / config defaults
    set_provider(LLM_PROVIDER, LLM_MODEL)
    print(f"[startup] LLM provider: {LLM_PROVIDER!r}, model: {LLM_MODEL!r}")


@app.get("/")
def root():
    return {
        "service": "AI-Driven Analytics Demo",
        "docs": "/docs",
        "api": "/api",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
