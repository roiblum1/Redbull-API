"""Input validation models for cluster generation.

This module defines Pydantic models for validating user input
when generating cluster configurations.
"""

from typing import List, Literal
from pydantic import BaseModel, Field, field_validator


class VendorConfig(BaseModel):
    """Configuration for a specific vendor nodepool."""
    
    vendor: str = Field(
        ...,
        description="Hardware vendor name"
    )
    number_of_nodes: int = Field(
        ...,
        ge=1,
        le=100,
        description="Number of worker nodes for this vendor"
    )
    infra_env_name: str = Field(
        ...,
        min_length=1,
        description="Infrastructure environment name for this vendor"
    )
    
    @field_validator('vendor')
    @classmethod
    def validate_vendor(cls, v: str) -> str:
        """Validate vendor name."""
        valid_vendors = {"cisco", "dell", "dell-data", "h100-gpu", "h200-gpu"}
        if v not in valid_vendors:
            raise ValueError(
                f"Invalid vendor '{v}'. Valid vendors: {', '.join(sorted(valid_vendors))}"
            )
        return v


class ClusterGenerationInput(BaseModel):
    """Input parameters for cluster generation.
    
    This model validates all input required to generate a cluster configuration,
    supporting multiple vendors with individual node counts and infra environments.
    """
    
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
    
    vendor_configs: List[VendorConfig] = Field(
        ...,
        min_length=1,
        description="List of vendor configurations with nodes and infra_env per vendor"
    )
    
    ocp_version: Literal["4.15", "4.16"] = Field(
        default="4.16",
        description="OpenShift version (determines imageContentSources)"
    )
    
    dns_domain: str = Field(
        default="example.company.com",
        description="DNS domain/zone for the cluster"
    )
    
    # Optional configs
    include_var_lib_containers: bool = Field(
        default=False,
        description="Include 98-var-lib-containers machine config"
    )
    
    include_ringsize: bool = Field(
        default=False,
        description="Include ringsize machine config"
    )
    
    custom_configs: List[str] = Field(
        default_factory=list,
        description="Additional custom machine config names to include"
    )

    @field_validator('cluster_name')
    @classmethod
    def validate_cluster_name(cls, v: str) -> str:
        """Validate cluster name format."""
        if not v.islower():
            raise ValueError('Cluster name must be lowercase')
        if v.startswith('-') or v.endswith('-'):
            raise ValueError('Cluster name cannot start or end with hyphen')
        return v

    @field_validator('site')
    @classmethod
    def validate_site(cls, v: str) -> str:
        """Validate site name."""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Site name must contain only alphanumeric characters, hyphens, and underscores')
        return v
    
    @field_validator('custom_configs')
    @classmethod
    def validate_custom_configs(cls, v: List[str]) -> List[str]:
        """Validate and clean custom config names."""
        return [config.strip() for config in v if config.strip()]
    
    @property
    def vendors(self) -> List[str]:
        """Get list of vendor names."""
        return [vc.vendor for vc in self.vendor_configs]

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "cluster_name": "my-production-cluster",
                "site": "datacenter-1",
                "vendor_configs": [
                    {"vendor": "dell", "number_of_nodes": 5, "infra_env_name": "dell-prod-env"},
                    {"vendor": "cisco", "number_of_nodes": 3, "infra_env_name": "cisco-prod-env"}
                ],
                "ocp_version": "4.16",
                "dns_domain": "prod.company.com",
                "include_var_lib_containers": True,
                "include_ringsize": False,
                "custom_configs": ["custom-network-config"]
            }
        }
