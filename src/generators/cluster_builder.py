"""Cluster configuration builder.

This module provides a builder class for constructing cluster configurations
following the Builder pattern for flexibility and extensibility.
"""

import yaml
import logging
from typing import Dict, Any, List, Optional

from models.input import ClusterGenerationInput, VendorConfig
from models.cluster import (
    ClusterConfig,
    NodePool,
    NodePoolLabels,
    AgentLabelSelector,
    ConfigItem,
    DNSConfig,
    ImageContentSource
)
from defaults.defaults_manager import DefaultsManager

logger = logging.getLogger(__name__)


class ClusterBuilder:
    """Builder class for constructing cluster configurations."""
    
    def __init__(self, defaults_manager: Optional[DefaultsManager] = None):
        """Initialize the cluster builder."""
        self.defaults_manager = defaults_manager or DefaultsManager()
        self._reset()
    
    def _reset(self) -> None:
        """Reset the builder to initial state."""
        self._cluster_name: Optional[str] = None
        self._site: Optional[str] = None
        self._dns_domain: Optional[str] = None
        self._max_pods: int = 250
        self._nodepools: List[NodePool] = []
        self._mc_files: List[str] = []
        self._image_content_sources: List[ImageContentSource] = []
    
    def set_cluster_name(self, name: str) -> "ClusterBuilder":
        """Set the cluster name."""
        self._cluster_name = name
        return self
    
    def set_site(self, site: str) -> "ClusterBuilder":
        """Set the deployment site."""
        self._site = site
        return self
    
    def set_dns_domain(self, domain: str) -> "ClusterBuilder":
        """Set the DNS domain."""
        self._dns_domain = domain
        return self
    
    def set_max_pods(self, max_pods: int) -> "ClusterBuilder":
        """Set the maximum pods per node."""
        self._max_pods = max_pods
        return self
    
    def add_nodepool(
        self,
        vendor: str,
        replicas: int,
        infra_env_name: str,
        include_var_lib_containers: bool = False,
        include_ringsize: bool = False,
        custom_configs: Optional[List[str]] = None
    ) -> "ClusterBuilder":
        """Add a nodepool for a specific vendor."""
        if not self._cluster_name:
            raise ValueError("Cluster name must be set before adding nodepools")
        
        # Build config list for this nodepool (passes max_pods for kubeletconfig)
        config_items = self.defaults_manager.build_config_list(
            cluster_name=self._cluster_name,
            vendor=vendor,
            max_pods=self._max_pods,
            include_var_lib_containers=include_var_lib_containers,
            include_ringsize=include_ringsize,
            custom_configs=custom_configs
        )
        
        nodepool = NodePool(
            name=f"{self._cluster_name}-{vendor}-nodepool",
            replicas=replicas,
            labels=NodePoolLabels(
                maxReplicas=str(replicas),
                minReplicas=str(max(1, replicas - 1))
            ),
            agentLabelSelector=AgentLabelSelector(
                nodeLabelValue=infra_env_name
            ),
            config=[ConfigItem(name=c["name"]) for c in config_items]
        )
        
        self._nodepools.append(nodepool)
        logger.debug(f"Added nodepool for vendor: {vendor} with {replicas} nodes")
        return self
    
    def set_mc_files(
        self,
        vendors: List[str],
        include_var_lib_containers: bool = False,
        include_ringsize: bool = False,
        custom_configs: Optional[List[str]] = None
    ) -> "ClusterBuilder":
        """Set the mcFiles list."""
        if not self._cluster_name:
            raise ValueError("Cluster name must be set before setting mcFiles")
        
        self._mc_files = self.defaults_manager.build_mc_files_list(
            cluster_name=self._cluster_name,
            vendors=vendors,
            max_pods=self._max_pods,
            include_var_lib_containers=include_var_lib_containers,
            include_ringsize=include_ringsize,
            custom_configs=custom_configs
        )
        return self
    
    def set_image_content_sources(self, version: str) -> "ClusterBuilder":
        """Set image content sources based on OCP version."""
        sources = self.defaults_manager.get_image_content_sources(version)
        self._image_content_sources = [
            ImageContentSource(
                source=s["source"],
                mirrors=s["mirrors"]
            )
            for s in sources
        ]
        return self
    
    def build(self) -> ClusterConfig:
        """Build the final cluster configuration."""
        if not self._cluster_name:
            raise ValueError("Cluster name is required")
        if not self._site:
            raise ValueError("Site is required")
        if not self._nodepools:
            raise ValueError("At least one nodepool is required")
        
        dns_domain = self._dns_domain or self.defaults_manager.get_default_dns_domain()
        
        config = ClusterConfig(
            clusterName=self._cluster_name,
            platform="agent",
            hostInventory="inventory",
            nodepool=self._nodepools,
            mcFiles=self._mc_files,
            dns=DNSConfig(site=self._site, zone=dns_domain),
            imageContentSources=self._image_content_sources
        )
        
        self._reset()
        logger.info(f"Built cluster configuration for: {config.clusterName}")
        return config


class ClusterConfigGenerator:
    """High-level generator for cluster configurations."""
    
    def __init__(self, defaults_manager: Optional[DefaultsManager] = None):
        """Initialize the generator."""
        self.defaults_manager = defaults_manager or DefaultsManager()
        self.builder = ClusterBuilder(self.defaults_manager)
    
    def generate(self, input_params: ClusterGenerationInput) -> ClusterConfig:
        """Generate a cluster configuration from input parameters."""
        logger.info(f"Generating cluster config for: {input_params.cluster_name}")
        
        # Set basic cluster info
        self.builder.set_cluster_name(input_params.cluster_name)
        self.builder.set_site(input_params.site)
        self.builder.set_dns_domain(input_params.dns_domain)
        self.builder.set_max_pods(input_params.max_pods)
        
        # Add nodepools for each vendor config
        for vendor_config in input_params.vendor_configs:
            self.builder.add_nodepool(
                vendor=vendor_config.vendor,
                replicas=vendor_config.number_of_nodes,
                infra_env_name=vendor_config.infra_env_name,
                include_var_lib_containers=input_params.include_var_lib_containers,
                include_ringsize=input_params.include_ringsize,
                custom_configs=input_params.custom_configs
            )
        
        # Set mcFiles
        vendors = [vc.vendor for vc in input_params.vendor_configs]
        self.builder.set_mc_files(
            vendors=vendors,
            include_var_lib_containers=input_params.include_var_lib_containers,
            include_ringsize=input_params.include_ringsize,
            custom_configs=input_params.custom_configs
        )
        
        # Set image content sources based on version
        self.builder.set_image_content_sources(input_params.ocp_version)
        
        return self.builder.build()
    
    def generate_yaml(self, input_params: ClusterGenerationInput) -> str:
        """Generate YAML content for a cluster configuration."""
        config = self.generate(input_params)
        
        config_dict = config.model_dump(by_alias=True, exclude_none=True)
        
        yaml_content = yaml.dump(
            config_dict,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            indent=2
        )
        
        return yaml_content
    
    def get_supported_versions(self) -> List[str]:
        """Get list of supported OpenShift versions."""
        return self.defaults_manager.get_supported_versions()
    
    def get_supported_vendors(self) -> List[str]:
        """Get list of supported vendors."""
        return self.defaults_manager.get_supported_vendors()
    
    def get_supported_max_pods(self) -> List[int]:
        """Get list of supported max pods values."""
        return self.defaults_manager.get_supported_max_pods()
    
    def get_default_configs(self, max_pods: int = 250) -> List[str]:
        """Get list of default configs."""
        return self.defaults_manager.get_default_configs(max_pods)
    
    def get_optional_configs(self) -> Dict[str, str]:
        """Get dictionary of optional configs."""
        return self.defaults_manager.get_optional_configs()
    
    def get_default_dns_domain(self) -> str:
        """Get default DNS domain."""
        return self.defaults_manager.get_default_dns_domain()
