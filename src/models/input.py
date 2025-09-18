"""Input validation models for cluster generation."""

from typing import Literal
from pydantic import BaseModel, Field, field_validator


class ClusterInput(BaseModel):
    """Input parameters for cluster generation."""
    
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

    @field_validator('cluster_name')
    def validate_cluster_name(cls, v: str) -> str:
        """Validate cluster name format."""
        if not v.islower():
            raise ValueError('Cluster name must be lowercase')
        if v.startswith('-') or v.endswith('-'):
            raise ValueError('Cluster name cannot start or end with hyphen')
        return v

    @field_validator('site')
    def validate_site(cls, v: str) -> str:
        """Validate site name."""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Site name must contain only alphanumeric characters, hyphens, and underscores')
        return v

    @field_validator('mce_name')
    def validate_mce_name(cls, v: str) -> str:
        """Validate MCE name."""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('MCE name must contain only alphanumeric characters, hyphens, and underscores')
        return v

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "cluster_name": "roi-cluster",
                "site": "datacenter-1", 
                "number_of_nodes": 3,
                "mce_name": "mce-prod",
                "environment": "prod",
                "flavor": "default"
            }
        }