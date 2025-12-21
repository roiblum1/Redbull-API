"""Request models for API endpoints."""

from typing import Literal, List
from pydantic import BaseModel, Field
from config.constants import Vendor, OCPVersion, MaxPods, ClusterDefaults


class VendorConfigRequest(BaseModel):
    """Configuration for a specific vendor nodepool."""

    vendor: str = Field(
        ...,
        description=f"Hardware vendor name ({', '.join(Vendor.values())})"
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


class ClusterRequestBase(BaseModel):
    """Base class for cluster request models.

    Contains shared fields and validation for both generate and preview requests.
    Follows DRY principle by centralizing common request structure.
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
    vendor_configs: List[VendorConfigRequest] = Field(
        ...,
        min_length=1,
        description="List of vendor configurations (each with vendor, nodes, and infra_env)"
    )
    ocp_version: Literal["4.15", "4.16"] = Field(
        default=ClusterDefaults.OCP_VERSION,
        description="OpenShift version (determines imageContentSources)"
    )
    dns_domain: str = Field(
        default=ClusterDefaults.DNS_DOMAIN,
        description="DNS domain/zone for the cluster"
    )
    max_pods: Literal[250, 500] = Field(
        default=ClusterDefaults.MAX_PODS,
        description=f"Maximum pods per node ({MaxPods.HIGH_DENSITY.value} requires var-lib-containers)"
    )
    include_var_lib_containers: bool = Field(
        default=False,
        description=f"Include 98-var-lib-containers machine config (auto-enabled for {MaxPods.HIGH_DENSITY.value} pods)"
    )
    include_ringsize: bool = Field(
        default=False,
        description="Include ringsize machine config"
    )
    custom_configs: List[str] = Field(
        default_factory=list,
        description="Additional custom machine config names to include"
    )


class GenerateClusterRequest(ClusterRequestBase):
    """Request model for cluster generation.

    Inherits all fields from ClusterRequestBase to eliminate duplication.
    """

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
                "max_pods": 250,
                "include_var_lib_containers": False,
                "include_ringsize": False,
                "custom_configs": []
            }
        }


class PreviewClusterRequest(ClusterRequestBase):
    """Request model for cluster configuration preview.

    Inherits all fields from ClusterRequestBase to eliminate duplication.
    """

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
                "max_pods": 250
            }
        }
