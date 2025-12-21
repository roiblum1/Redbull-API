"""Request models for API endpoints."""

from typing import Literal, List
from pydantic import BaseModel, Field


class VendorConfigRequest(BaseModel):
    """Configuration for a specific vendor nodepool."""
    
    vendor: str = Field(
        ...,
        description="Hardware vendor name (cisco, dell, dell-data, h100-gpu, h200-gpu)"
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
    vendor_configs: List[VendorConfigRequest] = Field(
        ...,
        min_length=1,
        description="List of vendor configurations (each with vendor, nodes, and infra_env)"
    )
    ocp_version: Literal["4.15", "4.16"] = Field(
        default="4.16",
        description="OpenShift version (determines imageContentSources)"
    )
    dns_domain: str = Field(
        default="example.company.com",
        description="DNS domain/zone for the cluster"
    )
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
    vendor_configs: List[VendorConfigRequest] = Field(
        ...,
        min_length=1,
        description="List of vendor configurations"
    )
    ocp_version: Literal["4.15", "4.16"] = Field(
        default="4.16",
        description="OpenShift version"
    )
    dns_domain: str = Field(
        default="example.company.com",
        description="DNS domain/zone"
    )
    include_var_lib_containers: bool = Field(
        default=False,
        description="Include 98-var-lib-containers config"
    )
    include_ringsize: bool = Field(
        default=False,
        description="Include ringsize config"
    )
    custom_configs: List[str] = Field(
        default_factory=list,
        description="Additional custom configs"
    )

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "cluster_name": "preview-cluster",
                "site": "datacenter-1",
                "vendor_configs": [
                    {"vendor": "dell", "number_of_nodes": 3, "infra_env_name": "test-infra-env"}
                ],
                "ocp_version": "4.16",
                "dns_domain": "test.company.com"
            }
        }
