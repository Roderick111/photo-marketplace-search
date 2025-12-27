"""
Photo to Marketplace Search - Main FastAPI Application.

A web application that converts photos into French marketplace search links
using Claude Vision API for object detection and categorization.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from src.api.routes import router
from src.core.config import get_settings
from src.core.exceptions import ImageValidationError, MarketplaceRoutingError, VisionAPIError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events for resource management.
    """
    # Startup
    logger.info("Starting Photo to Marketplace Search API...")

    # Ensure upload directory exists
    settings = get_settings()
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(exist_ok=True)
    logger.info(f"Upload directory ready: {upload_dir}")

    yield

    # Shutdown
    logger.info("Shutting down Photo to Marketplace Search API...")


# Create FastAPI application
app = FastAPI(
    title="Photo to Marketplace Search",
    description=(
        "Upload a photo and get French marketplace search links. "
        "Supports Abebooks.fr (books), Vinted (clothing), and Leboncoin (general)."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(ImageValidationError)
async def image_validation_error_handler(
    request: Request,
    exc: ImageValidationError,
) -> JSONResponse:
    """Handle image validation errors with user-friendly messages."""
    logger.warning(f"Image validation error: {exc.message}")
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message, "error_type": "validation_error"},
    )


@app.exception_handler(VisionAPIError)
async def vision_api_error_handler(
    request: Request,
    exc: VisionAPIError,
) -> JSONResponse:
    """Handle Vision API errors without exposing internal details."""
    logger.error(f"Vision API error: {exc.message}")
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Image analysis failed. Please try again later.",
            "error_type": "api_error",
        },
    )


@app.exception_handler(MarketplaceRoutingError)
async def marketplace_routing_error_handler(
    request: Request,
    exc: MarketplaceRoutingError,
) -> JSONResponse:
    """Handle marketplace routing errors."""
    logger.error(f"Marketplace routing error: {exc.message}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Failed to generate marketplace links.",
            "error_type": "routing_error",
        },
    )


# Include API routes
app.include_router(router)

# Mount static files directory
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    logger.info(f"Static files mounted from: {static_dir}")


@app.get("/")
async def root() -> dict[str, str]:
    """
    Root endpoint redirecting to the upload interface.

    Returns:
        Message with links to available interfaces.
    """
    return {
        "message": "Photo to Marketplace Search API",
        "docs": "/docs",
        "interface": "/static/index.html",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
