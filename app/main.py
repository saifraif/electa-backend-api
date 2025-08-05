from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1.endpoints import auth, admin
from app.middleware.rate_limiter import limiter # Import our new limiter

# Create the FastAPI application instance
app = FastAPI(title="ELECTA API")

# Add the limiter to the application's state
app.state.limiter = limiter

# Add the exception handler that sends a 429 response when a limit is hit
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include our API routers
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(admin.router, prefix="/api/v1", tags=["Admin"])


@app.get("/")
def read_root():
    """
    A simple root endpoint to confirm the API is running.
    """
    return {"message": "ELECTA API is running"}