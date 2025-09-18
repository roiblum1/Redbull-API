"""Path validation for GitOps repository structure."""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class PathValidator:
    """Validates and manages repository path structure."""
    
    def __init__(self, repo_path: Path):
        """Initialize path validator.
        
        Args:
            repo_path: Path to the GitOps repository.
        """
        self.repo_path = Path(repo_path)
        logger.info(f"Path validator initialized for repository: {self.repo_path}")
    
    def validate_path_exists(self, relative_path: Path) -> bool:
        """Check if a path exists in the repository.
        
        Args:
            relative_path: Path relative to repository root.
            
        Returns:
            True if path exists, False otherwise.
        """
        full_path = self.repo_path / relative_path
        exists = full_path.exists()
        logger.debug(f"Path validation for {relative_path}: {exists}")
        return exists
    
    def create_directory_structure(self, relative_path: Path) -> bool:
        """Create directory structure for a given path.
        
        Args:
            relative_path: Path relative to repository root.
            
        Returns:
            True if directories were created successfully, False otherwise.
        """
        try:
            full_path = self.repo_path / relative_path
            directory_path = full_path.parent
            
            if not directory_path.exists():
                directory_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory structure: {directory_path}")
                return True
            else:
                logger.debug(f"Directory structure already exists: {directory_path}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create directory structure for {relative_path}: {e}")
            return False
    
    def validate_cluster_path(self, site: str, environment: str, mce_name: str, cluster_name: str) -> tuple[Path, bool]:
        """Validate and prepare the full cluster configuration path.
        
        Args:
            site: Site name.
            environment: Environment (prod/prep).
            mce_name: MCE instance name.
            cluster_name: Cluster name.
            
        Returns:
            Tuple of (full_path, path_exists).
        """
        relative_path = Path("sites") / site / "mce-tenant-cluster" / f"mce-{environment}" / mce_name / f"ocp4-{cluster_name}.yaml"
        full_path = self.repo_path / relative_path
        
        path_exists = self.validate_path_exists(relative_path.parent)
        
        logger.info(f"Cluster path validation - Path: {relative_path}, Exists: {path_exists}")
        
        return full_path, path_exists
    
    def get_required_directories(self, site: str, environment: str, mce_name: str) -> list[Path]:
        """Get list of directories that should exist for the cluster configuration.
        
        Args:
            site: Site name.
            environment: Environment (prod/prep).
            mce_name: MCE instance name.
            
        Returns:
            List of directory paths that should exist.
        """
        base_path = Path("sites") / site / "mce-tenant-cluster" / f"mce-{environment}" / mce_name
        
        directories = [
            Path("sites"),
            Path("sites") / site,
            Path("sites") / site / "mce-tenant-cluster",
            Path("sites") / site / "mce-tenant-cluster" / f"mce-{environment}",
            base_path
        ]
        
        return directories
    
    def validate_all_required_paths(self, site: str, environment: str, mce_name: str) -> dict[str, bool]:
        """Validate all required paths for a cluster configuration.
        
        Args:
            site: Site name.
            environment: Environment (prod/prep).
            mce_name: MCE instance name.
            
        Returns:
            Dictionary mapping path to existence status.
        """
        required_dirs = self.get_required_directories(site, environment, mce_name)
        validation_results = {}
        
        for directory in required_dirs:
            exists = self.validate_path_exists(directory)
            validation_results[str(directory)] = exists
            
        logger.debug(f"Path validation results: {validation_results}")
        return validation_results