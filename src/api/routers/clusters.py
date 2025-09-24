"""Cluster management API endpoints."""

import logging
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from fastapi.responses import PlainTextResponse

from models.input import ClusterInput
from generators.cluster_generator import ClusterGenerator
from git_ops.repository import GitRepository
from utils.exceptions import MCEGeneratorError
from config import settings
from api.models.requests import GenerateClusterRequest, PreviewClusterRequest
from api.models.responses import (
    GenerateClusterResponse, 
    PreviewClusterResponse, 
    FlavorListResponse,
    ValidateFlavorResponse,
    FlavorInfo,
    GitInfo,
    ErrorResponse
)

router = APIRouter(prefix="/clusters", tags=["clusters"])
logger = logging.getLogger(__name__)


@router.post(
    "/generate",
    response_model=GenerateClusterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate cluster configuration",
    description="Generate a cluster configuration and optionally commit to GitOps repository"
)
async def generate_cluster(request: GenerateClusterRequest):
    """Generate cluster configuration with optional GitOps integration."""
    try:
        logger.info(f"Generating cluster configuration for: {request.cluster_name}")
        
        # Convert request to ClusterInput
        cluster_input = ClusterInput(
            cluster_name=request.cluster_name,
            site=request.site,
            number_of_nodes=request.number_of_nodes,
            mce_name=request.mce_name,
            environment=request.environment,
            flavor=request.flavor
        )
        
        # Initialize generator
        generator = ClusterGenerator()
        
        # Validate flavor
        if not generator.validate_flavor(request.flavor):
            available_flavors = generator.list_available_flavors()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid flavor '{request.flavor}'. Available flavors: {', '.join(available_flavors)}"
            )
        
        # Generate configuration
        yaml_content = generator.generate_yaml_content(cluster_input)
        output_path = generator.get_output_path(cluster_input)
        
        # Use configured repository or request override
        repo_path = request.repo_path or settings.GITOPS_REPO_PATH
        remote_url = request.remote_url or settings.GITOPS_REPO_URL
        
        # Determine if this is a dry run (no repo configured)
        is_dry_run = not repo_path or not remote_url
        
        if is_dry_run:
            # Dry run mode - just return the configuration
            return GenerateClusterResponse(
                cluster_name=request.cluster_name,
                output_path=str(output_path),
                flavor_used=request.flavor,
                dry_run=True,
                yaml_content=yaml_content,
                message="Cluster configuration generated successfully (dry-run mode)"
            )
        
        # GitOps integration
        try:
            git_repo = GitRepository(Path(repo_path), remote_url)
            
            # Generate branch name and create branch
            branch_name = git_repo.generate_branch_name(request.cluster_name, request.site)
            
            if not git_repo.create_branch(branch_name):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create Git branch"
                )
            
            # Add file to repository
            if not git_repo.add_file(output_path, yaml_content):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to add file to repository"
                )
            
            # Commit changes
            commit_message = f"Add cluster configuration for {request.cluster_name} in {request.site}\n\nCluster: {request.cluster_name}\nSite: {request.site}\nEnvironment: {request.environment}\nNodes: {request.number_of_nodes}\nFlavor: {request.flavor}"
            
            if not git_repo.commit_changes(commit_message, request.author_name, request.author_email):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to commit changes"
                )
            
            # Try to push branch
            pushed = git_repo.push_branch(branch_name)
            
            git_info = GitInfo(
                branch_name=branch_name,
                commit_message=commit_message,
                file_path=str(output_path),
                pushed=pushed
            )
            
            return GenerateClusterResponse(
                cluster_name=request.cluster_name,
                output_path=str(output_path),
                flavor_used=request.flavor,
                dry_run=False,
                git_info=git_info,
                message=f"Cluster configuration generated and committed to branch '{branch_name}'"
            )
            
        except Exception as e:
            logger.error(f"GitOps operation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"GitOps operation failed: {str(e)}"
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
    description="Generate and preview cluster configuration without creating files"
)
async def preview_cluster(request: PreviewClusterRequest):
    """Preview cluster configuration without creating files."""
    try:
        logger.info(f"Previewing cluster configuration for: {request.cluster_name}")
        
        # Convert request to ClusterInput
        cluster_input = ClusterInput(
            cluster_name=request.cluster_name,
            site=request.site,
            number_of_nodes=request.number_of_nodes,
            mce_name=request.mce_name,
            environment=request.environment,
            flavor=request.flavor
        )
        
        # Initialize generator
        generator = ClusterGenerator()
        
        # Validate flavor
        if not generator.validate_flavor(request.flavor):
            available_flavors = generator.list_available_flavors()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid flavor '{request.flavor}'. Available flavors: {', '.join(available_flavors)}"
            )
        
        # Generate configuration
        yaml_content = generator.generate_yaml_content(cluster_input)
        output_path = generator.get_output_path(cluster_input)
        
        return PreviewClusterResponse(
            cluster_name=request.cluster_name,
            output_path=str(output_path),
            yaml_content=yaml_content,
            flavor_used=request.flavor
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


@router.get(
    "/flavors",
    response_model=FlavorListResponse,
    summary="List available flavors",
    description="Get a list of all available cluster flavors"
)
async def list_flavors():
    """List all available cluster flavors."""
    try:
        generator = ClusterGenerator()
        flavors = generator.list_available_flavors()
        
        flavor_info_list = []
        for flavor in flavors:
            is_valid = generator.validate_flavor(flavor)
            flavor_info_list.append(FlavorInfo(
                name=flavor,
                valid=is_valid,
                description=f"Cluster flavor template: {flavor}"
            ))
        
        return FlavorListResponse(
            flavors=flavor_info_list,
            total=len(flavor_info_list)
        )
    
    except Exception as e:
        logger.error(f"Error listing flavors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list flavors: {str(e)}"
        )


@router.get(
    "/flavors/{flavor_name}/validate",
    response_model=ValidateFlavorResponse,
    summary="Validate flavor",
    description="Validate a specific cluster flavor template"
)
async def validate_flavor(flavor_name: str):
    """Validate a specific cluster flavor."""
    try:
        generator = ClusterGenerator()
        is_valid = generator.validate_flavor(flavor_name)
        
        if is_valid:
            message = f"Flavor '{flavor_name}' is valid and ready to use"
        else:
            available_flavors = generator.list_available_flavors()
            message = f"Flavor '{flavor_name}' is invalid or not found. Available flavors: {', '.join(available_flavors)}"
        
        return ValidateFlavorResponse(
            flavor=flavor_name,
            valid=is_valid,
            message=message
        )
    
    except Exception as e:
        logger.error(f"Error validating flavor: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate flavor: {str(e)}"
        )


@router.get(
    "/flavors/{flavor_name}/template",
    response_class=PlainTextResponse,
    summary="Get flavor template",
    description="Get the raw template content for a specific flavor"
)
async def get_flavor_template(flavor_name: str):
    """Get the raw template content for a specific flavor."""
    try:
        generator = ClusterGenerator()
        
        if not generator.validate_flavor(flavor_name):
            available_flavors = generator.list_available_flavors()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flavor '{flavor_name}' not found. Available flavors: {', '.join(available_flavors)}"
            )
        
        # Load the template file directly
        template_path = Path(__file__).parent.parent.parent / "templates" / f"{flavor_name}.yaml"
        
        if not template_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template file for flavor '{flavor_name}' not found"
            )
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        return PlainTextResponse(
            content=template_content,
            media_type="text/yaml"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get template: {str(e)}"
        )


@router.get(
    "/flavors/{flavor_name}/variables",
    summary="Get template variables",
    description="Get all variables used in a specific flavor template"
)
async def get_template_variables(flavor_name: str):
    """Get all variables used in a template."""
    try:
        generator = ClusterGenerator()
        
        if not generator.validate_flavor(flavor_name):
            available_flavors = generator.list_available_flavors()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flavor '{flavor_name}' not found. Available flavors: {', '.join(available_flavors)}"
            )
        
        # Get template variables
        template_vars = generator.template_loader.get_template_variables(flavor_name)
        
        return {
            "flavor": flavor_name,
            "variables": sorted(list(template_vars)),
            "total": len(template_vars),
            "message": f"Found {len(template_vars)} variables in template '{flavor_name}'"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template variables: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get template variables: {str(e)}"
        )