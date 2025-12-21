"""Application-wide constants and enumerations.

This module centralizes all magic strings, vendor lists, and configuration
constants to ensure a single source of truth across the application.
"""

from enum import Enum
from typing import Final


class Vendor(str, Enum):
    """Supported hardware vendors.

    To add a new vendor, just add ONE line:
        NEW_VENDOR = "technical-name"

    Display name is auto-generated from the enum name (e.g., H100_GPU -> "H100 Gpu").
    Override display_name property if custom formatting needed.
    """

    CISCO = "cisco"
    DELL = "dell"
    DELL_DATA = "dell-data"
    H100_GPU = "h100-gpu"
    H200_GPU = "h200-gpu"

    @property
    def display_name(self) -> str:
        """Get human-readable display name for this vendor.

        Auto-generates from enum name but can be overridden with custom mapping.
        """
        # Custom display names for better formatting
        custom_names = {
            "CISCO": "Cisco UCS",
            "DELL": "Dell PowerEdge",
            "DELL_DATA": "Dell Data Services",
            "H100_GPU": "NVIDIA H100 GPU",
            "H200_GPU": "NVIDIA H200 GPU",
        }
        return custom_names.get(self.name, self.name.replace("_", " ").title())

    @classmethod
    def values(cls) -> list[str]:
        """Get list of all vendor values."""
        return [v.value for v in cls]

    @classmethod
    def display_names(cls) -> dict[str, str]:
        """Get mapping of vendor values to display names."""
        return {v.value: v.display_name for v in cls}


class OCPVersion(str, Enum):
    """Supported OpenShift Container Platform versions."""
    V4_15 = "4.15"
    V4_16 = "4.16"

    @classmethod
    def values(cls) -> list[str]:
        """Get list of all version values."""
        return [v.value for v in cls]


class MaxPods(int, Enum):
    """Supported maximum pods per node configurations."""
    STANDARD = 250
    HIGH_DENSITY = 500


class ConfigNames:
    """Machine configuration names used in cluster generation."""

    # Network manager config template
    NM_CONF_TEMPLATE: Final[str] = "nm-conf-{cluster_name}-{vendor}"

    # Base configs
    WORKERS_CHRONY: Final[str] = "workers-chrony-configuration"
    KUBELET_CONFIG_250: Final[str] = "worker-kubeletconfig"
    KUBELET_CONFIG_500: Final[str] = "worker-kubeletconfig-500"

    # Optional configs
    VAR_LIB_CONTAINERS: Final[str] = "98-var-lib-containers"
    RINGSIZE: Final[str] = "ringsize"

    @staticmethod
    def get_nm_conf_name(cluster_name: str, vendor: str) -> str:
        """Generate network manager config name for a cluster and vendor."""
        return f"nm-conf-{cluster_name}-{vendor}"

    @staticmethod
    def get_kubelet_config_name(max_pods: int) -> str:
        """Get kubeletconfig name based on max pods configuration."""
        if max_pods == MaxPods.HIGH_DENSITY.value:
            return ConfigNames.KUBELET_CONFIG_500
        return ConfigNames.KUBELET_CONFIG_250


class ClusterDefaults:
    """Default values for cluster configuration."""

    DNS_DOMAIN: Final[str] = "example.company.com"
    MAX_PODS: Final[int] = MaxPods.STANDARD.value
    OCP_VERSION: Final[str] = OCPVersion.V4_16.value
    PLATFORM: Final[str] = "agent"
    HOST_INVENTORY: Final[str] = "inventory"
    AGENT_LABEL_KEY: Final[str] = "infraenv"


class APIConfig:
    """API configuration constants."""

    API_VERSION: Final[str] = "v1"
    APP_NAME: Final[str] = "MCE Cluster Generator API"
    APP_VERSION: Final[str] = "2.0.0"
    APP_DESCRIPTION: Final[str] = "API for generating MCE cluster configurations with UI"
