"""Response models for API endpoints."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


class FlavorInfo(BaseModel):
    """Flavor information model."""
    
    name: str = Field(..., description="Flavor name")
    valid: bool = Field(..., description="Whether the flavor is valid")
    description: Optional[str] = Field(default=None, description="Flavor description")


class FlavorListResponse(BaseModel):
    """Response model for listing flavors."""
    
    flavors: List[FlavorInfo] = Field(..., description="List of available flavors")
    total: int = Field(..., description="Total number of flavors")


class ValidateFlavorResponse(BaseModel):
    """Response model for flavor validation."""
    
    flavor: str = Field(..., description="Flavor name")
    valid: bool = Field(..., description="Whether the flavor is valid")
    message: str = Field(..., description="Validation message")


class PreviewClusterResponse(BaseModel):
    """Response model for cluster preview."""
    
    cluster_name: str = Field(..., description="Cluster name")
    output_path: str = Field(..., description="Expected output file path")
    yaml_content: str = Field(..., description="Generated YAML content")
    flavor_used: str = Field(..., description="Flavor template used")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")


class GitInfo(BaseModel):
    """Git operation information."""
    
    branch_name: str = Field(..., description="Created branch name")
    commit_message: str = Field(..., description="Commit message used")
    file_path: str = Field(..., description="Path to generated file")
    pushed: bool = Field(..., description="Whether branch was pushed to remote")
    
    
class GenerateClusterResponse(BaseModel):
    """Response model for cluster generation."""
    
    cluster_name: str = Field(..., description="Cluster name")
    output_path: str = Field(..., description="Output file path")
    flavor_used: str = Field(..., description="Flavor template used")
    dry_run: bool = Field(..., description="Whether this was a dry run")
    git_info: Optional[GitInfo] = Field(default=None, description="Git operation details")
    yaml_content: Optional[str] = Field(default=None, description="Generated YAML content (dry-run only)")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    message: str = Field(..., description="Success message")


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")