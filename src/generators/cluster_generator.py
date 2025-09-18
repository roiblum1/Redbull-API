"""Core cluster configuration generator."""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from models.input import ClusterInput
from models.cluster import ClusterConfig
from generators.template_loader import TemplateLoader

logger = logging.getLogger(__name__)


class ClusterGenerator:
    """Generates cluster configuration from input parameters and templates."""
    
    def __init__(self, templates_dir: Optional[Path] = None):
        """Initialize cluster generator.
        
        Args:
            templates_dir: Directory containing template files.
        """
        self.template_loader = TemplateLoader(templates_dir)
        logger.info("Cluster generator initialized")
    
    def generate_cluster_config(self, input_params: ClusterInput) -> ClusterConfig:
        """Generate cluster configuration from input parameters.
        
        Args:
            input_params: Validated input parameters.
            
        Returns:
            Generated cluster configuration.
            
        Raises:
            ValueError: If template rendering fails or produces invalid config.
        """
        logger.info(f"Generating cluster config for: {input_params.cluster_name}")
        
        # Prepare template variables
        template_vars = {
            "cluster_name": input_params.cluster_name,
            "number_of_nodes": input_params.number_of_nodes,
            "site": input_params.site,
            "mce_name": input_params.mce_name,
            "environment": input_params.environment
        }
        
        # Render template
        try:
            rendered_yaml = self.template_loader.render_template(
                input_params.flavor, 
                template_vars
            )
            logger.debug(f"Template rendered successfully for flavor: {input_params.flavor}")
        except Exception as e:
            logger.error(f"Failed to render template: {e}")
            raise ValueError(f"Template rendering failed: {e}")
        
        # Parse rendered YAML into configuration object
        try:
            config_dict = yaml.safe_load(rendered_yaml)
            cluster_config = ClusterConfig(**config_dict)
            logger.info(f"Cluster configuration generated successfully")
            return cluster_config
        except Exception as e:
            logger.error(f"Failed to parse rendered configuration: {e}")
            raise ValueError(f"Configuration parsing failed: {e}")
    
    def generate_yaml_content(self, input_params: ClusterInput) -> str:
        """Generate YAML content for cluster configuration.
        
        Args:
            input_params: Validated input parameters.
            
        Returns:
            YAML content as string.
        """
        cluster_config = self.generate_cluster_config(input_params)
        return yaml.dump(
            cluster_config.model_dump(), 
            default_flow_style=False, 
            sort_keys=False,
            indent=2
        )
    
    def get_output_path(self, input_params: ClusterInput) -> Path:
        """Generate the output file path for the cluster configuration.
        
        Args:
            input_params: Validated input parameters.
            
        Returns:
            Path where the configuration should be saved.
        """
        # Path format: sites/<site>/mce-tenant-cluster/mce-<prod/prep>/<mce-name>/ocp4-<cluster-name>.yaml
        path = Path("sites") / input_params.site / "mce-tenant-cluster" / f"mce-{input_params.environment}" / input_params.mce_name / f"ocp4-{input_params.cluster_name}.yaml"
        
        logger.debug(f"Generated output path: {path}")
        return path
    
    def list_available_flavors(self) -> list[str]:
        """List all available cluster flavors.
        
        Returns:
            List of available flavor names.
        """
        return self.template_loader.list_available_flavors()
    
    def validate_flavor(self, flavor: str) -> bool:
        """Validate that a flavor template exists and is valid.
        
        Args:
            flavor: Name of the flavor to validate.
            
        Returns:
            True if flavor is valid, False otherwise.
        """
        return self.template_loader.validate_template(flavor)