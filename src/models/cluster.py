"""Cluster configuration models.

This module defines the data models for cluster configuration,
following the structure required for MCE cluster generation.
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field


class ConfigItem(BaseModel):
    """Configuration item with a name."""
    name: str = Field(..., description="Configuration name")


class AgentLabelSelector(BaseModel):
    """Agent label selector for nodepool configuration."""
    nodeLabelKey: str = Field(
        default="infraenvs.agent-install.openshift.io",
        description="Label key for agent selection"
    )
    nodeLabelValue: str = Field(
        ...,
        description="Label value (typically the infra_env_name)"
    )


class NodePoolLabels(BaseModel):
    """Labels for nodepool configuration."""
    maxReplicas: str = Field(..., description="Maximum number of replicas")
    minReplicas: str = Field(..., description="Minimum number of replicas")


class NodePool(BaseModel):
    """Nodepool configuration for a specific vendor."""
    name: str = Field(..., description="Nodepool name (cluster-vendor-nodepool)")
    replicas: int = Field(..., ge=1, description="Number of replicas")
    labels: NodePoolLabels = Field(..., description="Nodepool labels")
    agentLabelSelector: AgentLabelSelector = Field(..., description="Agent selection criteria")
    config: List[ConfigItem] = Field(..., description="List of machine configs")


class DNSConfig(BaseModel):
    """DNS configuration for the cluster."""
    site: str = Field(..., description="Site identifier")
    zone: str = Field(..., description="DNS zone/domain name")


class ImageContentSource(BaseModel):
    """Image content source configuration for registry mirroring."""
    source: str = Field(..., description="Source registry")
    mirrors: List[str] = Field(..., description="Mirror registries")


class ClusterConfig(BaseModel):
    """Complete cluster configuration model.
    
    This model represents the full cluster configuration YAML structure
    that will be generated and applied to MCE.
    """
    clusterName: str = Field(..., description="Name of the cluster")
    platform: str = Field(default="agent", description="Platform type")
    hostInventory: str = Field(default="inventory", description="Host inventory reference")
    nodepool: List[NodePool] = Field(..., description="List of nodepools (one per vendor)")
    mcFiles: List[str] = Field(..., description="Machine config files list")
    dns: DNSConfig = Field(..., description="DNS configuration")
    imageContentSources: List[ImageContentSource] = Field(
        default_factory=list,
        description="Image content sources for registry mirroring"
    )

    def to_yaml_dict(self) -> Dict[str, Any]:
        """Convert to dictionary suitable for YAML output.
        
        Returns:
            Dictionary representation of the cluster config.
        """
        return self.model_dump(by_alias=True, exclude_none=True)
