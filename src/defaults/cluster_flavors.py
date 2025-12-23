"""Cluster flavor loader - loads cluster flavors from YAML files.

Flavors are predefined cluster configurations that simplify cluster generation.
To add a new flavor: Simply create a new YAML file in the flavors/ directory.
No code changes required!

YAML format:
```yaml
name: My Flavor Name
description: Description of what this cluster flavor provides

vendors:
  - vendor: dell
    nodes: 3
    infra_env: dell-infra
  - vendor: cisco    # (optional) add more vendors
    nodes: 2
    infra_env: cisco-infra

ocp_version: "4.16"  # or "4.15"
max_pods: 250        # or 500
include_var_lib_containers: false
include_ringsize: false
custom_configs: []   # optional list of custom config names
```
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from functools import lru_cache

from utils.logging import get_logger

logger = get_logger(__name__)

# Directory containing flavor YAML files
FLAVORS_DIR = Path(__file__).parent / "flavors"


@dataclass
class ClusterFlavor:
    """A cluster configuration flavor loaded from YAML."""
    
    name: str
    description: str
    vendors: List[Dict[str, Any]]
    ocp_version: str = "4.16"
    max_pods: int = 250
    include_var_lib_containers: bool = False
    include_ringsize: bool = False
    custom_configs: List[str] = field(default_factory=list)
    
    # Internal: the filename this was loaded from
    _filename: str = ""
    
    def to_dict(self) -> Dict:
        """Convert flavor to dictionary for API request."""
        return {
            "vendor_configs": [
                {
                    "vendor": v["vendor"],
                    "number_of_nodes": v["nodes"],
                    "infra_env_name": v.get("infra_env", f"{v['vendor']}-infra")
                }
                for v in self.vendors
            ],
            "ocp_version": self.ocp_version,
            "max_pods": self.max_pods,
            "include_var_lib_containers": self.include_var_lib_containers,
            "include_ringsize": self.include_ringsize,
            "custom_configs": self.custom_configs or []
        }


def _load_flavor_from_file(filepath: Path) -> Optional[ClusterFlavor]:
    """Load a single flavor from a YAML file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data:
            logger.warning(f"Empty flavor file: {filepath}")
            return None
        
        # Validate required fields
        if not data.get('name') or not data.get('vendors'):
            logger.warning(f"Invalid flavor file (missing name or vendors): {filepath}")
            return None
        
        flavor = ClusterFlavor(
            name=data['name'],
            description=data.get('description', ''),
            vendors=data['vendors'],
            ocp_version=str(data.get('ocp_version', '4.16')),
            max_pods=int(data.get('max_pods', 250)),
            include_var_lib_containers=bool(data.get('include_var_lib_containers', False)),
            include_ringsize=bool(data.get('include_ringsize', False)),
            custom_configs=data.get('custom_configs', []) or [],
            _filename=filepath.stem
        )
        
        return flavor
        
    except yaml.YAMLError as e:
        logger.error(f"YAML parsing error in {filepath}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error loading flavor from {filepath}: {e}")
        return None


def _load_all_flavors() -> Dict[str, ClusterFlavor]:
    """Load all flavors from the flavors directory."""
    flavors = {}
    
    if not FLAVORS_DIR.exists():
        logger.warning(f"Flavors directory not found: {FLAVORS_DIR}")
        return flavors
    
    for filepath in sorted(FLAVORS_DIR.glob("*.yaml")):
        flavor = _load_flavor_from_file(filepath)
        if flavor:
            # Use filename (without .yaml) as the flavor key
            flavor_key = filepath.stem
            flavors[flavor_key] = flavor
            logger.debug(f"Loaded flavor: {flavor_key} ({flavor.name})")
    
    logger.info(f"Loaded {len(flavors)} flavors from {FLAVORS_DIR}")
    return flavors


# Cache the loaded flavors
@lru_cache(maxsize=1)
def _get_flavors_cache() -> Dict[str, ClusterFlavor]:
    """Get cached flavors (reload by clearing cache)."""
    return _load_all_flavors()


def reload_flavors() -> None:
    """Force reload of all flavors from disk."""
    _get_flavors_cache.cache_clear()
    _get_flavors_cache()
    logger.info("Flavors reloaded from disk")


def get_flavor(flavor_name: str) -> ClusterFlavor:
    """Get a cluster flavor by name.
    
    Args:
        flavor_name: Name of the flavor (filename without .yaml)
        
    Returns:
        ClusterFlavor object
        
    Raises:
        KeyError: If flavor not found
    """
    flavors = _get_flavors_cache()
    
    if flavor_name not in flavors:
        available = list(flavors.keys())
        raise KeyError(
            f"Flavor '{flavor_name}' not found. "
            f"Available flavors: {', '.join(available)}"
        )
    
    return flavors[flavor_name]


def list_flavors() -> Dict[str, str]:
    """List all available flavors with descriptions.
    
    Returns:
        Dictionary of flavor name to description
    """
    flavors = _get_flavors_cache()
    return {
        name: flavor.description
        for name, flavor in flavors.items()
    }


def get_flavor_details(flavor_name: str) -> Dict:
    """Get detailed information about a flavor.
    
    Args:
        flavor_name: Name of the flavor
        
    Returns:
        Dictionary with flavor details
    """
    flavor = get_flavor(flavor_name)
    
    # Calculate total nodes
    total_nodes = sum(v.get("nodes", 0) for v in flavor.vendors)
    
    # Get vendor breakdown
    vendors = [
        {
            "vendor": v["vendor"],
            "nodes": v.get("nodes", 0)
        }
        for v in flavor.vendors
    ]
    
    return {
        "name": flavor.name,
        "description": flavor.description,
        "total_nodes": total_nodes,
        "vendors": vendors,
        "ocp_version": flavor.ocp_version,
        "max_pods": flavor.max_pods,
        "high_density": flavor.max_pods == 500,
        "includes_var_lib_containers": flavor.include_var_lib_containers,
        "includes_ringsize": flavor.include_ringsize,
        "custom_configs": flavor.custom_configs
    }


def get_all_flavors() -> Dict[str, ClusterFlavor]:
    """Get all loaded flavors."""
    return _get_flavors_cache().copy()
