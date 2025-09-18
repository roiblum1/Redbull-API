"""Template loader for flavor-based cluster generation."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Template, Environment, FileSystemLoader
import logging

logger = logging.getLogger(__name__)


class TemplateLoader:
    """Loads and processes cluster flavor templates."""
    
    def __init__(self, templates_dir: Optional[Path] = None):
        """Initialize template loader.
        
        Args:
            templates_dir: Directory containing template files. Defaults to package templates.
        """
        if templates_dir is None:
            self.templates_dir = Path(__file__).parent.parent / "templates"
        else:
            self.templates_dir = Path(templates_dir)
            
        self.env = Environment(loader=FileSystemLoader(str(self.templates_dir)))
        logger.info(f"Template loader initialized with directory: {self.templates_dir}")
    
    def list_available_flavors(self) -> list[str]:
        """List all available flavor templates.
        
        Returns:
            List of available flavor names.
        """
        flavors = []
        if self.templates_dir.exists():
            for file in self.templates_dir.glob("*.yaml"):
                if file.is_file():
                    flavors.append(file.stem)
        
        logger.debug(f"Available flavors: {flavors}")
        return flavors
    
    def load_template(self, flavor: str) -> Template:
        """Load a specific flavor template.
        
        Args:
            flavor: Name of the flavor template to load.
            
        Returns:
            Jinja2 template object.
            
        Raises:
            FileNotFoundError: If the template file doesn't exist.
        """
        template_file = f"{flavor}.yaml"
        template_path = self.templates_dir / template_file
        
        if not template_path.exists():
            available = self.list_available_flavors()
            raise FileNotFoundError(
                f"Template '{flavor}' not found. Available flavors: {available}"
            )
        
        logger.info(f"Loading template: {template_file}")
        return self.env.get_template(template_file)
    
    def render_template(self, flavor: str, variables: Dict[str, Any]) -> str:
        """Render a template with the provided variables.
        
        Args:
            flavor: Name of the flavor template to use.
            variables: Variables to substitute in the template.
            
        Returns:
            Rendered YAML content as string.
            
        Raises:
            FileNotFoundError: If the template file doesn't exist.
        """
        template = self.load_template(flavor)
        
        # Add default variables
        default_vars = {
            "private_registry": "registry.internal.company.com"
        }
        
        # Merge with provided variables (provided variables take precedence)
        render_vars = {**default_vars, **variables}
        
        logger.debug(f"Rendering template '{flavor}' with variables: {list(render_vars.keys())}")
        rendered = template.render(**render_vars)
        
        # Validate that the rendered content is valid YAML
        try:
            yaml.safe_load(rendered)
        except yaml.YAMLError as e:
            logger.error(f"Rendered template produced invalid YAML: {e}")
            raise ValueError(f"Template rendering produced invalid YAML: {e}")
        
        return rendered
    
    def validate_template(self, flavor: str) -> bool:
        """Validate that a template can be loaded and has required structure.
        
        Args:
            flavor: Name of the flavor template to validate.
            
        Returns:
            True if template is valid, False otherwise.
        """
        try:
            template = self.load_template(flavor)
            
            # Try rendering with minimal test variables
            test_vars = {
                "cluster_name": "test-cluster",
                "number_of_nodes": 3,
                "private_registry": "test.registry.com"
            }
            
            rendered = template.render(**test_vars)
            config = yaml.safe_load(rendered)
            
            # Check for required top-level keys
            required_keys = ["clusterName", "platform", "nodePool", "mcConfig"]
            for key in required_keys:
                if key not in config:
                    logger.error(f"Template '{flavor}' missing required key: {key}")
                    return False
            
            logger.info(f"Template '{flavor}' validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Template '{flavor}' validation failed: {e}")
            return False