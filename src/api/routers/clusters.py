"""Cluster management API endpoints.

This module follows the Thin Controller pattern:
- Controllers handle HTTP concerns (request/response, status codes)
- Business logic is delegated to the service layer
- No direct access to repositories or generators
"""

from typing import Dict
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import PlainTextResponse

from services.cluster_service import ClusterService, create_cluster_service
from utils.exceptions import handle_api_exceptions
from utils.logging import get_logger
from models.requests import (
    GenerateClusterRequest,
    PreviewClusterRequest
)
from models.responses import (
    GenerateClusterResponse,
    PreviewClusterResponse,
    DefaultsResponse
)

router = APIRouter(prefix="/clusters", tags=["clusters"])
logger = get_logger(__name__)


# Dependency injection for service layer
def get_cluster_service() -> ClusterService:
    """Get cluster service instance (dependency injection).

    This function can be overridden in tests to inject mock services.

    Returns:
        ClusterService instance
    """
    return create_cluster_service()


@router.get(
    "/defaults",
    response_model=DefaultsResponse,
    summary="Get default values",
    description="Get all default values for cluster generation"
)
@handle_api_exceptions
async def get_defaults(service: ClusterService = Depends(get_cluster_service)):
    """Get all default values for cluster configuration.

    Args:
        service: Injected cluster service

    Returns:
        Default values for cluster generation

    Raises:
        HTTPException: If defaults cannot be retrieved
    """
    return service.get_defaults()


@router.get(
    "/vendors",
    summary="List available vendors",
    description="Get a list of all available hardware vendors"
)
async def list_vendors(service: ClusterService = Depends(get_cluster_service)):
    """List all available hardware vendors.

    Args:
        service: Injected cluster service

    Returns:
        List of available vendors with display names
    """
    return service.list_vendors()


@router.get(
    "/versions",
    summary="List available OpenShift versions",
    description="Get a list of all supported OpenShift versions"
)
async def list_versions(service: ClusterService = Depends(get_cluster_service)):
    """List all supported OpenShift versions.

    Args:
        service: Injected cluster service

    Returns:
        List of OpenShift versions with default
    """
    return service.list_versions()


@router.get(
    "/sites",
    summary="List available sites",
    description="Get a list of all available deployment sites"
)
async def list_sites(service: ClusterService = Depends(get_cluster_service)):
    """List all available deployment sites.

    Args:
        service: Injected cluster service

    Returns:
        List of available deployment sites
    """
    return service.list_sites()


@router.get(
    "/flavors",
    summary="List cluster flavors",
    description="Get a list of all predefined cluster configuration flavors"
)
async def list_cluster_flavors(service: ClusterService = Depends(get_cluster_service)):
    """List all available cluster flavors.

    Args:
        service: Injected cluster service

    Returns:
        List of available cluster flavors
    """
    return service.list_flavors()


@router.post(
    "/flavors/reload",
    summary="Reload flavors from disk",
    description="Reload all flavor YAML files without restarting the server"
)
@handle_api_exceptions
async def reload_cluster_flavors(service: ClusterService = Depends(get_cluster_service)):
    """Reload flavors from YAML files.

    Use this after adding new flavor YAML files to pick them up
    without restarting the server.

    Args:
        service: Injected cluster service

    Returns:
        Reload status with available flavors

    Raises:
        HTTPException: If reload fails
    """
    return service.reload_flavors()


@router.get(
    "/flavors/{flavor_name}",
    summary="Get flavor details",
    description="Get detailed information about a specific cluster flavor"
)
@handle_api_exceptions
async def get_cluster_flavor(
    flavor_name: str,
    service: ClusterService = Depends(get_cluster_service)
):
    """Get details of a specific cluster flavor.

    Args:
        flavor_name: Name of the flavor
        service: Injected cluster service

    Returns:
        Flavor details

    Raises:
        HTTPException: If flavor not found
    """
    return service.get_flavor_details(flavor_name)


@router.post(
    "/generate/flavor/{flavor_name}",
    response_model=GenerateClusterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate cluster from flavor",
    description="Generate a cluster configuration using a predefined flavor. Only cluster_name, site, and dns_domain are required."
)
@handle_api_exceptions
async def generate_cluster_from_flavor(
    flavor_name: str,
    cluster_name: str,
    site: str,
    dns_domain: str = None,
    service: ClusterService = Depends(get_cluster_service)
):
    """Generate cluster configuration from a flavor.

    Args:
        flavor_name: Name of the flavor to use
        cluster_name: Name for the cluster
        site: Deployment site
        dns_domain: Optional DNS domain
        service: Injected cluster service

    Returns:
        Generated cluster configuration

    Raises:
        HTTPException: If flavor not found or generation fails
    """
    return service.generate_from_flavor(
        flavor_name=flavor_name,
        cluster_name=cluster_name,
        site=site,
        dns_domain=dns_domain
    )


@router.post(
    "/generate",
    response_model=GenerateClusterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate cluster configuration",
    description="Generate a cluster configuration YAML with per-vendor node counts and infra environments"
)
@handle_api_exceptions
async def generate_cluster(
    request: GenerateClusterRequest,
    service: ClusterService = Depends(get_cluster_service)
):
    """Generate cluster configuration.

    Args:
        request: Cluster generation request
        service: Injected cluster service

    Returns:
        Generated cluster configuration

    Raises:
        HTTPException: If validation or generation fails
    """
    return service.generate_cluster(request)


@router.post(
    "/preview",
    response_model=PreviewClusterResponse,
    summary="Preview cluster configuration",
    description="Generate and preview cluster configuration without any side effects"
)
@handle_api_exceptions
async def preview_cluster(
    request: PreviewClusterRequest,
    service: ClusterService = Depends(get_cluster_service)
):
    """Preview cluster configuration.

    Args:
        request: Cluster preview request
        service: Injected cluster service

    Returns:
        Preview of cluster configuration

    Raises:
        HTTPException: If validation or generation fails
    """
    return service.preview_cluster(request)
