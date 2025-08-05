from fastapi import FastAPI
from app.api.v1.endpoints import auth

# Create the FastAPI application instance
app = FastAPI(title="ELECTA API")

# Include the authentication router
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])

@app.get("/")
def read_root():
    """
    A simple root endpoint to confirm the API is running.
    """
    return {"message": "ELECTA API is running"}