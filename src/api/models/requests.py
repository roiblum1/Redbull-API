"""Request models for API endpoints."""

from typing import Optional, Literal
from pydantic import BaseModel, Field


class GenerateClusterRequest(BaseModel):
    """Request model for cluster generation."""
    
    cluster_name: str = Field(
        ...,
        min_length=1,
        max_length=63,
        pattern=r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?$',
        description="Cluster name following Kubernetes naming conventions"
    )
    site: str = Field(
        ...,
        min_length=1,
        description="Site where the cluster will be deployed"
    )
    number_of_nodes: int = Field(
        ...,
        ge=1,
        le=100,
        description="Number of worker nodes in the cluster"
    )
    mce_name: str = Field(
        ...,
        min_length=1,
        description="MCE instance name"
    )
    environment: Literal["prod", "prep"] = Field(
        ...,
        description="Environment type: production or preparation"
    )
    flavor: str = Field(
        default="default",
        description="Cluster flavor template to use"
    )
    repo_path: Optional[str] = Field(
        default=None,
        description="Path to GitOps repository (if not provided, dry-run mode)"
    )
    remote_url: Optional[str] = Field(
        default=None,
        description="Remote repository URL for cloning"
    )
    author_name: str = Field(
        default="MCE API",
        description="Author name for Git commits"
    )
    author_email: str = Field(
        default="mce-api@company.com",
        description="Author email for Git commits"
    )

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "cluster_name": "api-cluster",
                "site": "datacenter-1",
                "number_of_nodes": 3,
                "mce_name": "mce-prod",
                "environment": "prod",
                "flavor": "default",
                "repo_path": "/path/to/gitops/repo",
                "author_name": "API User",
                "author_email": "user@company.com"
            }
        }


class PreviewClusterRequest(BaseModel):
    """Request model for cluster configuration preview."""
    
    cluster_name: str = Field(
        ...,
        min_length=1,
        max_length=63,
        pattern=r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?$',
        description="Cluster name following Kubernetes naming conventions"
    )
    site: str = Field(
        ...,
        min_length=1,
        description="Site where the cluster will be deployed"
    )
    number_of_nodes: int = Field(
        ...,
        ge=1,
        le=100,
        description="Number of worker nodes in the cluster"
    )
    mce_name: str = Field(
        ...,
        min_length=1,
        description="MCE instance name"
    )
    environment: Literal["prod", "prep"] = Field(
        ...,
        description="Environment type: production or preparation"
    )
    flavor: str = Field(
        default="default",
        description="Cluster flavor template to use"
    )

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "cluster_name": "preview-cluster",
                "site": "datacenter-1",
                "number_of_nodes": 3,
                "mce_name": "mce-prod",
                "environment": "prod",
                "flavor": "default"
            }
        }