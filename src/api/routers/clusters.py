"""Cluster management API endpoints."""

import logging
from typing import Dict
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import PlainTextResponse

from models.input import ClusterGenerationInput, VendorConfig
from generators.cluster_builder import ClusterConfigGenerator
from defaults.defaults_manager import DefaultsManager
from utils.exceptions import MCEGeneratorError
from config import settings
from api.models.requests import (
    GenerateClusterRequest,
    PreviewClusterRequest
)
from api.models.responses import (
    GenerateClusterResponse,
    PreviewClusterResponse,
    DefaultsResponse,
    VendorInfo,
    VersionInfo,
    ConfigInfo
)

router = APIRouter(prefix="/clusters", tags=["clusters"])
logger = logging.getLogger(__name__)

# Initialize generator and defaults manager
generator = ClusterConfigGenerator()
defaults_manager = DefaultsManager()


# Vendor display names mapping
VENDOR_DISPLAY_NAMES: Dict[str, str] = {
    "cisco": "Cisco UCS",
    "dell": "Dell PowerEdge",
    "dell-data": "Dell Data Services",
    "h100-gpu": "NVIDIA H100 GPU",
    "h200-gpu": "NVIDIA H200 GPU"
}


@router.get(
    "/defaults",
    response_model=DefaultsResponse,
    summary="Get default values",
    description="Get all default values for cluster generation"
)
async def get_defaults():
    """Get all default values for cluster configuration."""
    try:
        vendors = [
            VendorInfo(
                name=v,
                display_name=VENDOR_DISPLAY_NAMES.get(v, v.title())
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
                name="98-var-lib-containers",
                description="Configure /var/lib/containers storage",
                is_optional=True
            ),
            ConfigInfo(
                key="ringsize",
                name="ringsize",
                description="Network ring buffer size configuration",
                is_optional=True
            )
        ]
        
        return DefaultsResponse(
            vendors=vendors,
            versions=versions,
            default_configs=defaults_manager.get_default_configs(),
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
    return {
        "vendors": [
            {
                "name": v,
                "display_name": VENDOR_DISPLAY_NAMES.get(v, v.title())
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
        
        # Validate vendors
        valid_vendors = set(defaults_manager.get_supported_vendors())
        for vc in request.vendor_configs:
            if vc.vendor not in valid_vendors:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid vendor: {vc.vendor}. Valid vendors: {', '.join(sorted(valid_vendors))}"
                )
        
        # Convert request to ClusterGenerationInput
        vendor_configs = [
            VendorConfig(
                vendor=vc.vendor,
                number_of_nodes=vc.number_of_nodes,
                infra_env_name=vc.infra_env_name
            )
            for vc in request.vendor_configs
        ]
        
        cluster_input = ClusterGenerationInput(
            cluster_name=request.cluster_name,
            site=request.site,
            vendor_configs=vendor_configs,
            ocp_version=request.ocp_version,
            dns_domain=request.dns_domain,
            include_var_lib_containers=request.include_var_lib_containers,
            include_ringsize=request.include_ringsize,
            custom_configs=request.custom_configs
        )
        
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
        logger.error(f"Unexpected error: {e}")
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
        
        # Validate vendors
        valid_vendors = set(defaults_manager.get_supported_vendors())
        for vc in request.vendor_configs:
            if vc.vendor not in valid_vendors:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid vendor: {vc.vendor}. Valid vendors: {', '.join(sorted(valid_vendors))}"
                )
        
        # Convert request to ClusterGenerationInput
        vendor_configs = [
            VendorConfig(
                vendor=vc.vendor,
                number_of_nodes=vc.number_of_nodes,
                infra_env_name=vc.infra_env_name
            )
            for vc in request.vendor_configs
        ]
        
        cluster_input = ClusterGenerationInput(
            cluster_name=request.cluster_name,
            site=request.site,
            vendor_configs=vendor_configs,
            ocp_version=request.ocp_version,
            dns_domain=request.dns_domain,
            include_var_lib_containers=request.include_var_lib_containers,
            include_ringsize=request.include_ringsize,
            custom_configs=request.custom_configs
        )
        
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
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )
