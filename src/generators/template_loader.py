"""Template loader for flavor-based cluster generation."""

import os
import yaml
import re
from pathlib import Path
from typing import Dict, Any, Optional, Set
from jinja2 import Template, Environment, FileSystemLoader, meta
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
    
    def get_template_variables(self, flavor: str) -> Set[str]:
        """Extract all variables used in a template.
        
        Args:
            flavor: Name of the flavor template.
            
        Returns:
            Set of variable names found in the template.
        """
        template_path = self.templates_dir / f"{flavor}.yaml"
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template '{flavor}' not found")
        
        # Read template content
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Parse template to find undeclared variables
        template_ast = self.env.parse(template_content)
        variables = meta.find_undeclared_variables(template_ast)
        
        logger.debug(f"Found variables in template '{flavor}': {variables}")
        return variables
    
    def render_template(self, flavor: str, variables: Dict[str, Any]) -> str:
        """Render a template with the provided variables.
        
        Args:
            flavor: Name of the flavor template to use.
            variables: Variables to substitute in the template.
            
        Returns:
            Rendered YAML content as string.
            
        Raises:
            FileNotFoundError: If the template file doesn't exist.
            ValueError: If required variables are missing.
        """
        template = self.load_template(flavor)
        
        # Get all variables used in template
        template_vars = self.get_template_variables(flavor)
        
        # Add default variables
        default_vars = {
            "private_registry": "registry.internal.company.com"
        }
        
        # Merge with provided variables (provided variables take precedence)
        render_vars = {**default_vars, **variables}
        
        # Check for missing variables and auto-generate defaults
        missing_vars = template_vars - set(render_vars.keys())
        if missing_vars:
            logger.warning(f"Missing variables in template '{flavor}': {missing_vars}")
            
            # Auto-generate default values for common patterns
            for var in missing_vars:
                default_value = self._generate_default_value(var, variables)
                render_vars[var] = default_value
                logger.info(f"Auto-generated variable '{var}': {default_value}")
        
        logger.debug(f"Rendering template '{flavor}' with variables: {list(render_vars.keys())}")
        rendered = template.render(**render_vars)
        
        # Validate that the rendered content is valid YAML
        try:
            yaml.safe_load(rendered)
        except yaml.YAMLError as e:
            logger.error(f"Rendered template produced invalid YAML: {e}")
            raise ValueError(f"Template rendering produced invalid YAML: {e}")
        
        return rendered
    
    def _generate_default_value(self, var_name: str, existing_vars: Dict[str, Any]) -> str:
        """Generate a default value for a missing variable.
        
        Args:
            var_name: Name of the variable to generate a default for.
            existing_vars: Already provided variables for context.
            
        Returns:
            Generated default value.
        """
        # Pattern-based default generation
        if 'registry' in var_name.lower():
            return "registry.internal.company.com"
        elif 'url' in var_name.lower():
            return f"https://example.com/{var_name.lower()}"
        elif 'version' in var_name.lower():
            return "latest"
        elif 'port' in var_name.lower():
            return "8080"
        elif 'namespace' in var_name.lower():
            return "default"
        elif 'image' in var_name.lower():
            return f"registry.internal.company.com/{var_name.lower()}:latest"
        elif var_name.endswith('_count') or var_name.endswith('_size'):
            return str(existing_vars.get('number_of_nodes', 3))
        elif var_name.startswith('enable_') or var_name.startswith('is_'):
            return "true"
        else:
            # Generic default - try to infer from cluster name if available
            cluster_name = existing_vars.get('cluster_name', 'default')
            return f"{cluster_name}-{var_name.replace('_', '-')}"
    
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