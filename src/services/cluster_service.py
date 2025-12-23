"""Cluster service - orchestrates all cluster generation business logic.

This service follows SOLID principles:
- Single Responsibility: Handles cluster generation orchestration
- Open/Closed: Extensible through dependency injection
- Liskov Substitution: N/A (no inheritance)
- Interface Segregation: Focused interface
- Dependency Inversion: Depends on abstractions (injected dependencies)
"""

from typing import List, Dict, Optional

from models.requests import GenerateClusterRequest, PreviewClusterRequest
from models.responses import (
    GenerateClusterResponse,
    PreviewClusterResponse,
    DefaultsResponse,
    VendorInfo,
    VersionInfo,
    ConfigInfo
)
from models.input import ClusterGenerationInput
from generators.cluster_builder import ClusterConfigGenerator
from defaults.defaults_manager import DefaultsManager
from defaults.cluster_flavors import get_flavor, get_flavor_details, list_flavors, reload_flavors
from services.validators import ClusterValidator
from services.converters import RequestConverter
from services.config_builder import ConfigListBuilder
from config.constants import ConfigNames, Vendor
from config.settings import settings
from utils.logging import get_logger, log_execution
from utils.exceptions import MCEGeneratorError

logger = get_logger(__name__)


class ClusterService:
    """Service layer for cluster operations.

    This class orchestrates all cluster-related business logic,
    separating it from the API routing layer. It follows the
    Service pattern and uses dependency injection for testability.

    Attributes:
        generator: Cluster configuration generator
        defaults_manager: Manager for default values
        validator: Cluster validation service
        converter: Request-to-domain model converter
    """

    def __init__(
        self,
        generator: Optional[ClusterConfigGenerator] = None,
        defaults_manager: Optional[DefaultsManager] = None
    ):
        """Initialize the cluster service.

        Args:
            generator: Cluster generator instance (injected for testability)
            defaults_manager: Defaults manager instance (injected for testability)
        """
        self.generator = generator or ClusterConfigGenerator()
        self.defaults_manager = defaults_manager or DefaultsManager()
        self.validator = ClusterValidator
        self.converter = RequestConverter

        logger.info("ClusterService initialized")

    def get_defaults(self) -> DefaultsResponse:
        """Get all default values for cluster configuration.

        Returns:
            DefaultsResponse with vendors, versions, and configs

        Raises:
            Exception: If defaults cannot be loaded
        """
        logger.debug("Getting cluster defaults")

        vendor_display_names = Vendor.display_names()

        vendors = [
            VendorInfo(
                name=v,
                display_name=vendor_display_names.get(v, v.title())
            )
            for v in self.defaults_manager.get_supported_vendors()
        ]

        versions = [
            VersionInfo(
                version=v,
                is_default=(v == settings.DEFAULT_OCP_VERSION)
            )
            for v in self.defaults_manager.get_supported_versions()
        ]

        optional_configs = [
            ConfigInfo(
                key="var_lib_containers",
                name=ConfigNames.VAR_LIB_CONTAINERS,
                description="Configure /var/lib/containers storage (required for 500 pods)",
                is_optional=True
            ),
            ConfigInfo(
                key="ringsize",
                name=ConfigNames.RINGSIZE,
                description="Network ring buffer size configuration",
                is_optional=True
            )
        ]

        # Get default configs for standard pods (250)
        # This is where we properly delegate to ConfigListBuilder
        base_configs = ConfigListBuilder.build_base_configs(max_pods=250)

        return DefaultsResponse(
            vendors=vendors,
            versions=versions,
            default_configs=base_configs,
            optional_configs=optional_configs,
            default_dns_domain=self.defaults_manager.get_default_dns_domain()
        )

    def list_vendors(self) -> Dict:
        """List all available hardware vendors.

        Returns:
            Dictionary with vendors list and total count
        """
        logger.debug("Listing available vendors")

        vendors = self.defaults_manager.get_supported_vendors()
        vendor_display_names = Vendor.display_names()

        return {
            "vendors": [
                {
                    "name": v,
                    "display_name": vendor_display_names.get(v, v.title())
                }
                for v in vendors
            ],
            "total": len(vendors)
        }

    def list_versions(self) -> Dict:
        """List all supported OpenShift versions.

        Returns:
            Dictionary with versions list, default, and total count
        """
        logger.debug("Listing available versions")

        versions = self.defaults_manager.get_supported_versions()
        return {
            "versions": versions,
            "default": settings.DEFAULT_OCP_VERSION,
            "total": len(versions)
        }

    def list_sites(self) -> Dict:
        """List all available deployment sites.

        Returns:
            Dictionary with sites list and total count
        """
        logger.debug("Listing available sites")

        sites = [site.strip() for site in settings.AVAILABLE_SITES if site.strip()]
        return {
            "sites": sites,
            "total": len(sites)
        }

    def list_flavors(self) -> Dict:
        """List all available cluster flavors.

        Returns:
            Dictionary with flavors list and total count
        """
        logger.debug("Listing available flavors")

        flavors = list_flavors()
        return {
            "flavors": [
                {"name": name, "description": desc}
                for name, desc in flavors.items()
            ],
            "total": len(flavors)
        }

    def get_flavor_details(self, flavor_name: str) -> Dict:
        """Get details of a specific cluster flavor.

        Args:
            flavor_name: Name of the flavor

        Returns:
            Dictionary with flavor details

        Raises:
            KeyError: If flavor not found
        """
        logger.debug(f"Getting flavor details for: {flavor_name}")
        return get_flavor_details(flavor_name)

    def reload_flavors(self) -> Dict:
        """Reload flavors from disk without restarting the server.

        Returns:
            Dictionary with reload status and available flavors
        """
        logger.info("Reloading cluster flavors from disk")

        reload_flavors()
        flavors = list_flavors()

        return {
            "message": "Flavors reloaded successfully",
            "flavors_loaded": len(flavors),
            "available_flavors": list(flavors.keys())
        }

    @log_execution(level="INFO", include_args=False)
    def generate_cluster(self, request: GenerateClusterRequest) -> GenerateClusterResponse:
        """Generate cluster configuration from request.

        Args:
            request: Cluster generation request

        Returns:
            GenerateClusterResponse with YAML content

        Raises:
            MCEGeneratorError: If generation fails
        """
        # Validate vendors using centralized validator
        self.validator.validate_vendors(request.vendor_configs)

        # Convert request to internal model using converter service
        cluster_input = self.converter.from_generate_request(request)

        # Generate YAML
        yaml_content = self.generator.generate_yaml(cluster_input)

        # Get vendor names for response
        vendors_used = [vc.vendor for vc in request.vendor_configs]

        return GenerateClusterResponse(
            cluster_name=request.cluster_name,
            yaml_content=yaml_content,
            vendors_used=vendors_used,
            ocp_version=request.ocp_version,
            nodepool_count=len(request.vendor_configs),
            message=f"Cluster configuration generated successfully with {len(request.vendor_configs)} nodepool(s)"
        )

    @log_execution(level="INFO", include_args=False)
    def preview_cluster(self, request: PreviewClusterRequest) -> PreviewClusterResponse:
        """Preview cluster configuration without side effects.

        Args:
            request: Cluster preview request

        Returns:
            PreviewClusterResponse with YAML content

        Raises:
            MCEGeneratorError: If preview generation fails
        """
        # Validate vendors using centralized validator
        self.validator.validate_vendors(request.vendor_configs)

        # Convert request to internal model using converter service
        cluster_input = self.converter.from_preview_request(request)

        # Generate YAML
        yaml_content = self.generator.generate_yaml(cluster_input)

        vendors_used = [vc.vendor for vc in request.vendor_configs]

        return PreviewClusterResponse(
            cluster_name=request.cluster_name,
            yaml_content=yaml_content,
            vendors_used=vendors_used,
            ocp_version=request.ocp_version,
            nodepool_count=len(request.vendor_configs)
        )

    @log_execution(level="INFO", include_args=True)
    def generate_from_flavor(
        self,
        flavor_name: str,
        cluster_name: str,
        site: str,
        dns_domain: Optional[str] = None
    ) -> GenerateClusterResponse:
        """Generate cluster configuration from a flavor.

        Args:
            flavor_name: Name of the flavor to use
            cluster_name: Name for the cluster
            site: Deployment site
            dns_domain: Optional DNS domain (uses default if not provided)

        Returns:
            GenerateClusterResponse with YAML content

        Raises:
            KeyError: If flavor not found
            MCEGeneratorError: If generation fails
        """
        # Get the flavor
        flavor = get_flavor(flavor_name)

        # Build request from flavor
        request_data = {
            "cluster_name": cluster_name,
            "site": site,
            "dns_domain": dns_domain or settings.DEFAULT_DNS_DOMAIN,
            **flavor.to_dict()
        }

        # Convert to GenerateClusterRequest
        request = GenerateClusterRequest(**request_data)

        # Validate vendors
        self.validator.validate_vendors(request.vendor_configs)

        # Convert to internal model
        cluster_input = self.converter.from_generate_request(request)

        # Generate YAML
        yaml_content = self.generator.generate_yaml(cluster_input)

        # Get vendor names for response
        vendors_used = [vc.vendor for vc in request.vendor_configs]

        return GenerateClusterResponse(
            cluster_name=cluster_name,
            yaml_content=yaml_content,
            vendors_used=vendors_used,
            ocp_version=request.ocp_version,
            nodepool_count=len(request.vendor_configs),
            message=f"Cluster configuration generated successfully from flavor '{flavor_name}'"
        )


# Service factory for dependency injection
def create_cluster_service(
    generator: Optional[ClusterConfigGenerator] = None,
    defaults_manager: Optional[DefaultsManager] = None
) -> ClusterService:
    """Factory function to create a ClusterService instance.

    This factory enables dependency injection and makes testing easier.

    Args:
        generator: Optional generator instance
        defaults_manager: Optional defaults manager instance

    Returns:
        Configured ClusterService instance
    """
    return ClusterService(
        generator=generator,
        defaults_manager=defaults_manager
    )
