"""Cluster management API endpoints."""

import logging
from typing import Dict
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import PlainTextResponse

from config.constants import Vendor, ConfigNames
from generators.cluster_builder import ClusterConfigGenerator
from defaults.defaults_manager import DefaultsManager
from utils.exceptions import MCEGeneratorError
from config.settings import settings
from models.requests import (
    GenerateClusterRequest,
    PreviewClusterRequest
)
from models.responses import (
    GenerateClusterResponse,
    PreviewClusterResponse,
    DefaultsResponse,
    VendorInfo,
    VersionInfo,
    ConfigInfo
)
from services.validators import ClusterValidator
from services.converters import RequestConverter

router = APIRouter(prefix="/clusters", tags=["clusters"])
logger = logging.getLogger(__name__)

# Initialize generator and defaults manager
generator = ClusterConfigGenerator()
defaults_manager = DefaultsManager()


@router.get(
    "/defaults",
    response_model=DefaultsResponse,
    summary="Get default values",
    description="Get all default values for cluster generation"
)
async def get_defaults():
    """Get all default values for cluster configuration."""
    try:
        vendor_display_names = Vendor.display_names()

        vendors = [
            VendorInfo(
                name=v,
                display_name=vendor_display_names.get(v, v.title())
            )
            for v in defaults_manager.get_supported_vendors()
        ]

        versions = [
            VersionInfo(
                version=v,
                is_default=(v == settings.DEFAULT_OCP_VERSION)
            )
            for v in defaults_manager.get_supported_versions()
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
        from services.config_builder import ConfigListBuilder
        base_configs = ConfigListBuilder._build_base_configs(250)

        return DefaultsResponse(
            vendors=vendors,
            versions=versions,
            default_configs=base_configs,
            optional_configs=optional_configs,
            default_dns_domain=defaults_manager.get_default_dns_domain()
        )

    except Exception as e:
        logger.error(f"Error getting defaults: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get defaults: {str(e)}"
        )


@router.get(
    "/vendors",
    summary="List available vendors",
    description="Get a list of all available hardware vendors"
)
async def list_vendors():
    """List all available hardware vendors."""
    vendors = defaults_manager.get_supported_vendors()
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


@router.get(
    "/versions",
    summary="List available OpenShift versions",
    description="Get a list of all supported OpenShift versions"
)
async def list_versions():
    """List all supported OpenShift versions."""
    versions = defaults_manager.get_supported_versions()
    return {
        "versions": versions,
        "default": settings.DEFAULT_OCP_VERSION,
        "total": len(versions)
    }


@router.post(
    "/generate",
    response_model=GenerateClusterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate cluster configuration",
    description="Generate a cluster configuration YAML with per-vendor node counts and infra environments"
)
async def generate_cluster(request: GenerateClusterRequest):
    """Generate cluster configuration."""
    try:
        logger.info(f"Generating cluster configuration for: {request.cluster_name}")

        # Validate vendors using centralized validator
        ClusterValidator.validate_vendors(request.vendor_configs)

        # Convert request to internal model using converter service
        cluster_input = RequestConverter.from_generate_request(request)

        # Generate YAML
        yaml_content = generator.generate_yaml(cluster_input)

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

    except MCEGeneratorError as e:
        logger.error(f"Generator error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.post(
    "/preview",
    response_model=PreviewClusterResponse,
    summary="Preview cluster configuration",
    description="Generate and preview cluster configuration without any side effects"
)
async def preview_cluster(request: PreviewClusterRequest):
    """Preview cluster configuration."""
    try:
        logger.info(f"Previewing cluster configuration for: {request.cluster_name}")

        # Validate vendors using centralized validator
        ClusterValidator.validate_vendors(request.vendor_configs)

        # Convert request to internal model using converter service
        cluster_input = RequestConverter.from_preview_request(request)

        # Generate YAML
        yaml_content = generator.generate_yaml(cluster_input)

        vendors_used = [vc.vendor for vc in request.vendor_configs]

        return PreviewClusterResponse(
            cluster_name=request.cluster_name,
            yaml_content=yaml_content,
            vendors_used=vendors_used,
            ocp_version=request.ocp_version,
            nodepool_count=len(request.vendor_configs)
        )

    except MCEGeneratorError as e:
        logger.error(f"Generator error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )
