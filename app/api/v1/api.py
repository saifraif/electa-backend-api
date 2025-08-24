from fastapi import APIRouter


# Import endpoint routers for API v1
from .endpoints import admin, auth, ekyc, ideologies, ingest, public

"""
API v1 router aggregator.

Mount this from app/main.py like:
    app.include_router(api_router, prefix="/api/v1")

Effective paths:
  - /api/v1/admin/*       (admin endpoints; admin router defines /admin/login etc.)
  - /api/v1/auth/*        (citizen auth endpoints; auth router has prefix="/auth")
  - /api/v1/ekyc/*        (eKYC endpoints; ekyc router has prefix="/ekyc")
  - /api/v1/ideologies/*  (ideology endpoints)
"""

api_router = APIRouter()

# Tag routers for Swagger grouping
api_router.include_router(admin.router, tags=["admin"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(ekyc.router, tags=["ekyc"])
api_router.include_router(ideologies.router, tags=["ideologies"])
api_router.include_router(ingest.router, tags=["ingest"]) 
api_router.include_router(public.router, tags=["public"])

