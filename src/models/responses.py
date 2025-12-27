"""
Response models for the Photo to Marketplace Search API.

These models define the structured outputs from the Claude Vision API
and the final marketplace search response format.
"""

from typing import Literal

from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    """Individual search query generated from image analysis."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Search query text in French",
    )
    confidence: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Confidence level for this query",
    )


class MarketplaceLink(BaseModel):
    """Marketplace search link with metadata."""

    marketplace: Literal["abebooks", "vinted", "leboncoin"] = Field(
        ...,
        description="Target marketplace name",
    )
    query: str = Field(..., description="Original search query")
    url: str = Field(..., description="Full marketplace search URL")


class VisionAnalysisResult(BaseModel):
    """Structured output from Claude Vision API."""

    object_type: Literal["book", "clothing", "electronics", "furniture", "tools", "general"] = (
        Field(
            ...,
            description="Detected object category for marketplace routing",
        )
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Brief description of the detected object",
    )
    search_queries: list[SearchQuery] = Field(
        ...,
        min_length=1,
        max_length=3,
        description="Generated search queries in French",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall confidence in the analysis",
    )


class MarketplaceSearchResponse(BaseModel):
    """Final response with marketplace links."""

    analysis: VisionAnalysisResult = Field(
        ...,
        description="Vision API analysis results",
    )
    marketplace_links: list[MarketplaceLink] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="Generated marketplace search links",
    )
    processing_time_seconds: float = Field(
        ...,
        ge=0.0,
        description="Total processing time in seconds",
    )


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(default="healthy", description="Service health status")


class ErrorResponse(BaseModel):
    """Error response for API failures."""

    detail: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Error category")
