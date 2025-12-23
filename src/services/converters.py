"""Conversion services for transforming between API and domain models.

This module implements the Adapter pattern to convert between API request models
and internal domain models, eliminating duplicate transformation logic.
"""

from typing import List

from models.requests import GenerateClusterRequest, PreviewClusterRequest, VendorConfigRequest
from models.input import ClusterGenerationInput, VendorConfig
from config.constants import MaxPods
from utils.logging import LoggingMixin, get_logger

logger = get_logger(__name__)


class RequestConverter(LoggingMixin):
    """Converts API request models to internal domain models."""

    @staticmethod
    def _convert_vendor_configs(vendor_configs: List[VendorConfigRequest]) -> List[VendorConfig]:
        """Convert API vendor config requests to domain vendor configs.

        Args:
            vendor_configs: List of API vendor config requests.

        Returns:
            List of domain vendor config objects.
        """
        return [
            VendorConfig(
                vendor=vc.vendor,
                number_of_nodes=vc.number_of_nodes,
                infra_env_name=vc.infra_env_name
            )
            for vc in vendor_configs
        ]

    @staticmethod
    def _should_include_var_lib_containers(include_var_lib: bool, max_pods: int) -> bool:
        """Determine if var_lib_containers config should be included.

        Args:
            include_var_lib: User-requested flag.
            max_pods: Maximum pods per node.

        Returns:
            True if var_lib_containers should be included.
        """
        return include_var_lib or max_pods == MaxPods.HIGH_DENSITY.value

    @staticmethod
    def from_generate_request(request: GenerateClusterRequest) -> ClusterGenerationInput:
        """Convert GenerateClusterRequest to ClusterGenerationInput.

        Args:
            request: API request object.

        Returns:
            Internal domain model.
        """
        vendor_configs = RequestConverter._convert_vendor_configs(request.vendor_configs)

        include_var_lib = RequestConverter._should_include_var_lib_containers(
            request.include_var_lib_containers,
            request.max_pods
        )

        return ClusterGenerationInput(
            cluster_name=request.cluster_name,
            site=request.site,
            vendor_configs=vendor_configs,
            ocp_version=request.ocp_version,
            dns_domain=request.dns_domain,
            max_pods=request.max_pods,
            include_var_lib_containers=include_var_lib,
            include_ringsize=request.include_ringsize,
            custom_configs=request.custom_configs
        )

    @staticmethod
    def from_preview_request(request: PreviewClusterRequest) -> ClusterGenerationInput:
        """Convert PreviewClusterRequest to ClusterGenerationInput.

        Args:
            request: API request object.

        Returns:
            Internal domain model.
        """
        vendor_configs = RequestConverter._convert_vendor_configs(request.vendor_configs)

        include_var_lib = RequestConverter._should_include_var_lib_containers(
            request.include_var_lib_containers,
            request.max_pods
        )

        return ClusterGenerationInput(
            cluster_name=request.cluster_name,
            site=request.site,
            vendor_configs=vendor_configs,
            ocp_version=request.ocp_version,
            dns_domain=request.dns_domain,
            max_pods=request.max_pods,
            include_var_lib_containers=include_var_lib,
            include_ringsize=request.include_ringsize,
            custom_configs=request.custom_configs
        )
