# D:\Application\Electa\app\app\electa-backend-api\app\main.py
from __future__ import annotations

import importlib
import logging
from typing import List

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings

# Optional: slowapi (rate limiting)
try:
    from slowapi import Limiter
    from slowapi.errors import RateLimitExceeded
    from slowapi.middleware import SlowAPIMiddleware
    from slowapi.util import get_remote_address

    _SLOWAPI_AVAILABLE = True
except Exception:
    _SLOWAPI_AVAILABLE = False

log = logging.getLogger("uvicorn.error")


def _include_known_routers(app: FastAPI) -> None:
    """
    Import routers if present. Each router must expose a module-level variable named `router`.
    They will be mounted under /api/v1.
    """
    modules: List[str] = [
        "app.api.v1.endpoints.auth",
        "app.api.v1.endpoints.admin",
        "app.api.v1.endpoints.ekyc",
        "app.api.v1.endpoints.charter",
        "app.api.v1.endpoints.compliance",
    ]
    for module_path in modules:
        try:
            module = importlib.import_module(module_path)
            router = getattr(module, "router", None)
            if router is not None:
                app.include_router(router, prefix="/api/v1")
                log.info("Included router from %s", module_path)
            else:
                log.warning("No `router` exported by %s (skipping)", module_path)
        except ModuleNotFoundError:
            log.warning("Router module not found: %s (skipping)", module_path)
        except Exception as e:
            log.exception("Failed to include router from %s: %s", module_path, e)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.project_name,
        version="1.0.0",
    )

    # CORS
    cors_origins = settings.cors_origins_normalized()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins or ["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rate limiting (optional)
    if _SLOWAPI_AVAILABLE:
        limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
        app.state.limiter = limiter
        app.add_middleware(SlowAPIMiddleware)

        @app.exception_handler(RateLimitExceeded)
        async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})

    @app.get("/healthz")
    async def healthz():
        return {"status": "ok"}

    @app.get("/readyz")
    async def readyz():
        return {"status": "ready"}

    @app.get("/")
    async def root():
        return {"name": settings.project_name, "env": settings.env}

    _include_known_routers(app)
    return app


app = create_app()
