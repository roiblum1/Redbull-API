"""Defaults manager for cluster configuration.

This module provides a centralized way to manage default values
for cluster generation, including version-specific image content sources.
"""

import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional
from functools import lru_cache

from config.constants import Vendor, OCPVersion, MaxPods, ConfigNames, ClusterDefaults
from utils.logging import get_logger

logger = get_logger(__name__)


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
