"""Defaults manager for cluster configuration.

This module provides a centralized way to manage default values
for cluster generation, including version-specific image content sources.
"""

import yaml
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from functools import lru_cache

from config.constants import Vendor, OCPVersion, MaxPods, ConfigNames, ClusterDefaults

logger = logging.getLogger(__name__)


class DefaultsManager:
    """Manages default values for cluster configuration.

    This class focuses on loading version-specific data (like image content sources)
    and providing access to configuration constants. Config building logic has been
    moved to ConfigListBuilder service to follow Single Responsibility Principle.
    """
    
    def __init__(self, defaults_dir: Optional[Path] = None):
        """Initialize the defaults manager.
        
        Args:
            defaults_dir: Directory containing default configuration files.
                         Defaults to the 'defaults' directory in the package.
        """
        if defaults_dir is None:
            self.defaults_dir = Path(__file__).parent
        else:
            self.defaults_dir = Path(defaults_dir)
        
        self.image_sources_dir = self.defaults_dir / "image_content_sources"
        logger.info(f"DefaultsManager initialized with directory: {self.defaults_dir}")
    
    @lru_cache(maxsize=10)
    def get_image_content_sources(self, version: str) -> List[Dict[str, Any]]:
        """Get image content sources for a specific OpenShift version.

        Args:
            version: OpenShift version string.

        Returns:
            List of image content source dictionaries.

        Raises:
            ValueError: If version is not supported.
            FileNotFoundError: If version file doesn't exist.
        """
        supported_versions = OCPVersion.values()
        if version not in supported_versions:
            raise ValueError(
                f"Unsupported version '{version}'. "
                f"Supported versions: {', '.join(supported_versions)}"
            )

        version_file = self.image_sources_dir / f"{version}.yaml"

        if not version_file.exists():
            raise FileNotFoundError(
                f"Image content sources file not found for version {version}: {version_file}"
            )

        with open(version_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        sources = data.get('imageContentSources', [])
        logger.debug(f"Loaded {len(sources)} image content sources for version {version}")
        return sources

    @staticmethod
    def get_supported_versions() -> List[str]:
        """Get list of supported OpenShift versions."""
        return OCPVersion.values()

    @staticmethod
    def get_supported_vendors() -> List[str]:
        """Get list of supported hardware vendors."""
        return Vendor.values()

    @staticmethod
    def get_supported_max_pods() -> List[int]:
        """Get list of supported max pods values."""
        return [MaxPods.STANDARD.value, MaxPods.HIGH_DENSITY.value]

    @staticmethod
    def get_default_dns_domain() -> str:
        """Get the default DNS domain."""
        return ClusterDefaults.DNS_DOMAIN
    
    def build_config_list(
        self,
        cluster_name: str,
        vendor: str,
        max_pods: int = MaxPods.STANDARD.value,
        include_var_lib_containers: bool = False,
        include_ringsize: bool = False,
        custom_configs: Optional[List[str]] = None
    ) -> List[Dict[str, str]]:
        """Build the complete config list for a nodepool.

        DEPRECATED: This method is maintained for backward compatibility.
        New code should use ConfigListBuilder.build_for_nodepool() directly.

        Args:
            cluster_name: Name of the cluster.
            vendor: Vendor name for nm-conf.
            max_pods: Maximum pods per node.
            include_var_lib_containers: Whether to include var-lib-containers config.
            include_ringsize: Whether to include ringsize config.
            custom_configs: Additional custom config names to include.

        Returns:
            List of config dictionaries with 'name' key.
        """
        from services.config_builder import ConfigListBuilder

        config_names = ConfigListBuilder.build_for_nodepool(
            cluster_name=cluster_name,
            vendor=vendor,
            max_pods=max_pods,
            include_var_lib_containers=include_var_lib_containers,
            include_ringsize=include_ringsize,
            custom_configs=custom_configs
        )

        return [{"name": name} for name in config_names]

    def build_mc_files_list(
        self,
        cluster_name: str,
        vendors: List[str],
        max_pods: int = MaxPods.STANDARD.value,
        include_var_lib_containers: bool = False,
        include_ringsize: bool = False,
        custom_configs: Optional[List[str]] = None
    ) -> List[str]:
        """Build the mcFiles list for cluster configuration.

        DEPRECATED: This method is maintained for backward compatibility.
        New code should use ConfigListBuilder.build_mc_files() directly.

        Args:
            cluster_name: Name of the cluster.
            vendors: List of vendors.
            max_pods: Maximum pods per node.
            include_var_lib_containers: Whether to include var-lib-containers config.
            include_ringsize: Whether to include ringsize config.
            custom_configs: Additional custom config names to include.

        Returns:
            List of mcFiles names.
        """
        from services.config_builder import ConfigListBuilder

        return ConfigListBuilder.build_mc_files(
            cluster_name=cluster_name,
            vendors=vendors,
            max_pods=max_pods,
            include_var_lib_containers=include_var_lib_containers,
            include_ringsize=include_ringsize,
            custom_configs=custom_configs
        )


# Global defaults manager instance
defaults_manager = DefaultsManager()
