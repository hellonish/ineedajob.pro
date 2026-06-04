"""
Wand API - FastAPI Backend
"""

import os
import time
import psutil
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from dotenv import load_dotenv

_start_time = time.time()
_proc = psutil.Process()

load_dotenv()

from .routers import auth, jobs, cover_letters, news, ws, profile
from .routers import billing as billing_router
from .database import engine, Base, ensure_sqlite_schema, seed_plans, backfill_subscriptions, SessionLocal
from . import models  # Import models to register them
from .limiter import limiter
from .billing.ledger import sweep_orphaned_reservations

# Create all tables (billing tables picked up automatically via Base)
Base.metadata.create_all(bind=engine)
ensure_sqlite_schema(engine)

# Seed plan catalogue and create Free subscriptions for all existing users
seed_plans(engine)
backfill_subscriptions(engine)

# Refund any reservations orphaned by a crash/restart mid-task (idempotent).
_sweep_db = SessionLocal()
try:
    _refunded = sweep_orphaned_reservations(_sweep_db)
    if _refunded:
        import logging
        logging.getLogger(__name__).info("Refunded %d orphaned reservation(s) on startup.", _refunded)
finally:
    _sweep_db.close()

app = FastAPI(
    title="Wand API",
    description="Resume analysis and job tracking platform",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


# Session middleware for OAuth
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("JWT_SECRET_KEY", "change-me-in-production")
)

# CORS — set ALLOWED_ORIGINS env var as comma-separated list in production
_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
_allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files (avatars, profile docs, etc.)
os.makedirs("api/uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="api/uploads"), name="uploads")

# Include routers
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(cover_letters.router)
app.include_router(news.router)
app.include_router(ws.router)
app.include_router(profile.router)
app.include_router(billing_router.router)


# Health check
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/metrics")
async def metrics():
    """Live process stats — memory, CPU, uptime. Local dev + ops use only."""
    mem = _proc.memory_info()
    cpu = _proc.cpu_percent(interval=0.1)
    vm = psutil.virtual_memory()
    return {
        "uptime_seconds": round(time.time() - _start_time),
        "process": {
            "rss_mb": round(mem.rss / 1024 / 1024, 1),
            "vms_mb": round(mem.vms / 1024 / 1024, 1),
            "cpu_percent": cpu,
            "threads": _proc.num_threads(),
            "open_files": len(_proc.open_files()),
        },
        "system": {
            "total_ram_mb": round(vm.total / 1024 / 1024),
            "available_ram_mb": round(vm.available / 1024 / 1024),
            "used_percent": vm.percent,
            "cpu_count": psutil.cpu_count(),
            "load_avg_1m": round(psutil.getloadavg()[0], 2),
        },
    }


@app.get("/")
async def root():
    return {"message": "Wand API", "docs": "/docs"}
