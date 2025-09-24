"""Cluster configuration models."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AgentLabelSelector(BaseModel):
    """Agent label selector configuration."""
    
    nodeLabelKey: str = Field(default="infraenv")
    nodeLabelValue: str = Field(default="classic-baremetal")


class NodePoolLabels(BaseModel):
    """Node pool labels configuration."""
    
    allowDeletion: bool = Field(default=False)
    minReplicas: str
    maxReplicas: str


class NodePoolConfig(BaseModel):
    """Node pool configuration."""
    
    name: str
    replicas: int = Field(ge=1)
    labels: NodePoolLabels
    agentLabelSelector: AgentLabelSelector = Field(default_factory=AgentLabelSelector)
    configs: List[str]


class MCConfig(BaseModel):
    """Machine config configuration."""
    
    configs: List[str]


class IDMSConfig(BaseModel):
    """IDMS (Image Digest Mirror Set) configuration."""
    
    mirrors: List[Dict[str, Any]] = Field(default_factory=list)


class ClusterConfig(BaseModel):
    """Complete cluster configuration model."""
    
    clusterName: str
    platform: str = Field(default="agent")
    nodePool: List[NodePoolConfig]
    mcConfig: List[str]
    idms: Optional[IDMSConfig] = Field(default=None)

