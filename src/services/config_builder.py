"""Configuration builder service for cluster machine configs.

This module implements the Strategy pattern to build configuration lists,
eliminating duplication between nodepool configs and mcFiles lists.
"""

from typing import List, Optional
from dataclasses import dataclass

from config.constants import ConfigNames, MaxPods


@dataclass
class ConfigBuildParams:
    """Parameters for building configuration lists."""
    cluster_name: str
    vendors: List[str]
    max_pods: int = MaxPods.STANDARD.value
    include_var_lib_containers: bool = False
    include_ringsize: bool = False
    custom_configs: Optional[List[str]] = None


class ConfigListBuilder:
    """Builds configuration lists for cluster generation.

    This class consolidates the config building logic that was previously
    duplicated across build_config_list() and build_mc_files_list().
    """

    @staticmethod
    def _should_include_var_lib(include_var_lib: bool, max_pods: int) -> bool:
        """Determine if var_lib_containers should be included.

        Args:
            include_var_lib: User-requested flag.
            max_pods: Maximum pods per node.

        Returns:
            True if var_lib_containers config is required.
        """
        return include_var_lib or max_pods == MaxPods.HIGH_DENSITY.value

    @staticmethod
    def _build_nm_conf_names(cluster_name: str, vendors: List[str]) -> List[str]:
        """Build network manager config names for all vendors.

        Args:
            cluster_name: Name of the cluster.
            vendors: List of vendor names.

        Returns:
            List of nm-conf names.
        """
        return [ConfigNames.get_nm_conf_name(cluster_name, vendor) for vendor in vendors]

    @staticmethod
    def _build_base_configs(max_pods: int) -> List[str]:
        """Build base configuration list.

        Args:
            max_pods: Maximum pods per node.

        Returns:
            List of base config names.
        """
        configs = [ConfigNames.WORKERS_CHRONY]
        configs.append(ConfigNames.get_kubelet_config_name(max_pods))
        return configs

    @staticmethod
    def _add_optional_configs(
        configs: List[str],
        include_var_lib: bool,
        max_pods: int,
        include_ringsize: bool
    ) -> None:
        """Add optional configurations to the config list (in-place).

        Args:
            configs: Configuration list to modify.
            include_var_lib: Whether to include var_lib_containers.
            max_pods: Maximum pods per node.
            include_ringsize: Whether to include ringsize.
        """
        if ConfigListBuilder._should_include_var_lib(include_var_lib, max_pods):
            configs.append(ConfigNames.VAR_LIB_CONTAINERS)

        if include_ringsize:
            configs.append(ConfigNames.RINGSIZE)

    @staticmethod
    def _add_custom_configs(configs: List[str], custom_configs: Optional[List[str]]) -> None:
        """Add custom configurations to the config list (in-place).

        Args:
            configs: Configuration list to modify.
            custom_configs: Additional custom config names.
        """
        if custom_configs:
            for config in custom_configs:
                if config.strip():
                    configs.append(config.strip())

    @staticmethod
    def build_for_nodepool(
        cluster_name: str,
        vendor: str,
        max_pods: int = MaxPods.STANDARD.value,
        include_var_lib_containers: bool = False,
        include_ringsize: bool = False,
        custom_configs: Optional[List[str]] = None
    ) -> List[str]:
        """Build configuration list for a single nodepool.

        Args:
            cluster_name: Name of the cluster.
            vendor: Vendor name for nm-conf.
            max_pods: Maximum pods per node.
            include_var_lib_containers: Whether to include var-lib-containers config.
            include_ringsize: Whether to include ringsize config.
            custom_configs: Additional custom config names.

        Returns:
            List of configuration names for the nodepool.
        """
        configs = []

        # Add vendor-specific nm-conf
        configs.append(ConfigNames.get_nm_conf_name(cluster_name, vendor))

        # Add base configs
        configs.extend(ConfigListBuilder._build_base_configs(max_pods))

        # Add optional configs
        ConfigListBuilder._add_optional_configs(
            configs,
            include_var_lib_containers,
            max_pods,
            include_ringsize
        )

        # Add custom configs
        ConfigListBuilder._add_custom_configs(configs, custom_configs)

        return configs

    @staticmethod
    def build_mc_files(
        cluster_name: str,
        vendors: List[str],
        max_pods: int = MaxPods.STANDARD.value,
        include_var_lib_containers: bool = False,
        include_ringsize: bool = False,
        custom_configs: Optional[List[str]] = None
    ) -> List[str]:
        """Build mcFiles list for cluster configuration.

        Args:
            cluster_name: Name of the cluster.
            vendors: List of all vendors in the cluster.
            max_pods: Maximum pods per node.
            include_var_lib_containers: Whether to include var-lib-containers config.
            include_ringsize: Whether to include ringsize config.
            custom_configs: Additional custom config names.

        Returns:
            List of mcFiles names.
        """
        mc_files = []

        # Add nm-conf for all vendors
        mc_files.extend(ConfigListBuilder._build_nm_conf_names(cluster_name, vendors))

        # Add base configs
        mc_files.extend(ConfigListBuilder._build_base_configs(max_pods))

        # Add optional configs
        ConfigListBuilder._add_optional_configs(
            mc_files,
            include_var_lib_containers,
            max_pods,
            include_ringsize
        )

        # Add custom configs
        ConfigListBuilder._add_custom_configs(mc_files, custom_configs)

        return mc_files
