from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routers import qr_code, oauth
from app.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="QR Code Generator API",
    description="An API for generating, managing, and retrieving QR codes",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(oauth.router, tags=["Authentication"])
app.include_router(qr_code.router, prefix="/qr-codes", tags=["QR Codes"])

@app.on_event("startup")
async def startup_event():
    """Create necessary directories on startup"""
    try:
        settings.QR_DIRECTORY.mkdir(parents=True, exist_ok=True)
        logger.info(f"QR code directory created/verified at {settings.QR_DIRECTORY}")
    except Exception as e:
        logger.error(f"Failed to create QR code directory: {e}")
        raise

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint that provides API information"""
    return {
        "message": "Welcome to the QR Code Generator API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }
