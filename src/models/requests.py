"""
Request models for the Photo to Marketplace Search API.

These models validate incoming data and provide type safety
for request handling.
"""

from pydantic import BaseModel, Field


class ImageUploadResponse(BaseModel):
    """Response from image upload validation."""

    filename: str = Field(..., description="Original filename of the uploaded image")
    size: int = Field(..., ge=0, description="File size in bytes")
    content_type: str = Field(..., description="MIME type of the image")
