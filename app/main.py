from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.v1.api import api_router

# ---- SlowAPI (rate limiting) via shared limiter ----
# If you remove slowapi from dependencies, you can delete this block safely.
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.limits import limiter  # single shared Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.project_name,
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_normalized() or ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(_: Request, __: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})

# Health endpoints
@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/readyz")
async def readyz():
    return {"status": "ready"}

@app.get("/")
async def root():
    return {"name": settings.project_name, "env": settings.env}

# API v1
app.include_router(api_router, prefix="/api/v1")
