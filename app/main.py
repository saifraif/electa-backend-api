from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1.endpoints import auth, admin, ekyc, charter, compliance
from app.middleware.rate_limiter import limiter

app = FastAPI(title="ELECTA API")

# Set up CORS middleware
origins = [
    "http://localhost:3000", # The origin for our React Admin Panel
    "http://localhost:8080", # A common alternative port for web development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include API routers
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(admin.router, prefix="/api/v1", tags=["Admin"])
app.include_router(ekyc.router, prefix="/api/v1", tags=["e-KYC"])
app.include_router(charter.router, prefix="/api/v1", tags=["Charter Management"])
app.include_router(compliance.router, prefix="/api/v1", tags=["Compliance Management"])

@app.get("/")
def read_root():
    """A simple root endpoint to confirm the API is running."""
    return {"message": "ELECTA API is running"}