"""Defaults manager for cluster configuration.

This module provides a centralized way to manage default values
for cluster generation, including version-specific image content sources.
"""

import yaml
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)


class DefaultsManager:
    """Manages default values for cluster configuration.
    
    This class follows the Single Responsibility Principle - it only handles
    loading and providing default values.
    """
    
    # Available OpenShift versions
    SUPPORTED_VERSIONS: List[str] = ["4.15", "4.16"]
    
    # Available vendors for nodepools
    SUPPORTED_VENDORS: List[str] = [
        "cisco",
        "dell", 
        "dell-data",
        "h100-gpu",
        "h200-gpu"
    ]
    
    # Default configs that are always included
    DEFAULT_CONFIGS: List[str] = [
        "workers-chrony-configuration",
        "worker-kubeletconfig"
    ]
    
    # Optional configs that users can enable
    OPTIONAL_CONFIGS: Dict[str, str] = {
        "var_lib_containers": "98-var-lib-containers",
        "ringsize": "ringsize"
    }
    
    # Default DNS domain
    DEFAULT_DNS_DOMAIN: str = "example.company.com"
    
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
            version: OpenShift version (e.g., "4.15", "4.16")
            
        Returns:
            List of image content source configurations.
            
        Raises:
            ValueError: If version is not supported.
            FileNotFoundError: If version configuration file doesn't exist.
        """
        if version not in self.SUPPORTED_VERSIONS:
            raise ValueError(
                f"Unsupported version '{version}'. "
                f"Supported versions: {', '.join(self.SUPPORTED_VERSIONS)}"
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
    
    def get_supported_versions(self) -> List[str]:
        """Get list of supported OpenShift versions.
        
        Returns:
            List of supported version strings.
        """
        return self.SUPPORTED_VERSIONS.copy()
    
    def get_supported_vendors(self) -> List[str]:
        """Get list of supported hardware vendors.
        
        Returns:
            List of supported vendor strings.
        """
        return self.SUPPORTED_VENDORS.copy()
    
    def get_default_configs(self) -> List[str]:
        """Get list of default configs that are always included.
        
        Returns:
            List of default config names.
        """
        return self.DEFAULT_CONFIGS.copy()
    
    def get_optional_configs(self) -> Dict[str, str]:
        """Get dictionary of optional configs.
        
        Returns:
            Dictionary mapping config keys to config names.
        """
        return self.OPTIONAL_CONFIGS.copy()
    
    def get_default_dns_domain(self) -> str:
        """Get the default DNS domain.
        
        Returns:
            Default DNS domain string.
        """
        return self.DEFAULT_DNS_DOMAIN
    
    def build_config_list(
        self,
        cluster_name: str,
        vendor: str,
        include_var_lib_containers: bool = False,
        include_ringsize: bool = False,
        custom_configs: Optional[List[str]] = None
    ) -> List[Dict[str, str]]:
        """Build the complete config list for a nodepool.
        
        Args:
            cluster_name: Name of the cluster.
            vendor: Vendor name for nm-conf.
            include_var_lib_containers: Whether to include var-lib-containers config.
            include_ringsize: Whether to include ringsize config.
            custom_configs: Additional custom config names to include.
            
        Returns:
            List of config dictionaries with 'name' key.
        """
        configs = []
        
        # Add nm-conf specific to cluster and vendor
        configs.append({"name": f"nm-conf-{cluster_name}-{vendor}"})
        
        # Add default configs
        for config in self.DEFAULT_CONFIGS:
            configs.append({"name": config})
        
        # Add optional configs if enabled
        if include_var_lib_containers:
            configs.append({"name": self.OPTIONAL_CONFIGS["var_lib_containers"]})
        
        if include_ringsize:
            configs.append({"name": self.OPTIONAL_CONFIGS["ringsize"]})
        
        # Add custom configs
        if custom_configs:
            for config in custom_configs:
                if config.strip():  # Skip empty strings
                    configs.append({"name": config.strip()})
        
        return configs
    
    def build_mc_files_list(
        self,
        cluster_name: str,
        vendors: List[str],
        include_var_lib_containers: bool = False,
        include_ringsize: bool = False,
        custom_configs: Optional[List[str]] = None
    ) -> List[str]:
        """Build the mcFiles list for cluster configuration.
        
        Args:
            cluster_name: Name of the cluster.
            vendors: List of vendors.
            include_var_lib_containers: Whether to include var-lib-containers config.
            include_ringsize: Whether to include ringsize config.
            custom_configs: Additional custom config names to include.
            
        Returns:
            List of mcFiles names.
        """
        mc_files = []
        
        # Add nm-conf for each vendor
        for vendor in vendors:
            mc_files.append(f"nm-conf-{cluster_name}-{vendor}")
        
        # Add default configs
        mc_files.extend(self.DEFAULT_CONFIGS)
        
        # Add optional configs if enabled
        if include_var_lib_containers:
            mc_files.append(self.OPTIONAL_CONFIGS["var_lib_containers"])
        
        if include_ringsize:
            mc_files.append(self.OPTIONAL_CONFIGS["ringsize"])
        
        # Add custom configs
        if custom_configs:
            for config in custom_configs:
                if config.strip():
                    mc_files.append(config.strip())
        
        return mc_files


# Global defaults manager instance
defaults_manager = DefaultsManager()

