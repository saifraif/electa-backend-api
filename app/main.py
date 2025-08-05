from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1.endpoints import auth, admin, ekyc # Import the new ekyc router
from app.middleware.rate_limiter import limiter

# Create the FastAPI application instance
app = FastAPI(title="ELECTA API")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include our API routers
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(admin.router, prefix="/api/v1", tags=["Admin"])
app.include_router(ekyc.router, prefix="/api/v1", tags=["e-KYC"]) # Add the new router

@app.get("/")
def read_root():
    """
    A simple root endpoint to confirm the API is running.
    """
    return {"message": "ELECTA API is running"}