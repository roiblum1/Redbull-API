"""GitOps repository management."""

import logging
from pathlib import Path
from typing import Optional
import git
from git import Repo, GitCommandError

from git_ops.path_validator import PathValidator

logger = logging.getLogger(__name__)


class GitRepository:
    """Manages GitOps repository operations."""
    
    def __init__(self, repo_path: Path, remote_url: Optional[str] = None):
        """Initialize Git repository manager.
        
        Args:
            repo_path: Path to the local Git repository.
            remote_url: URL of the remote repository (for cloning).
        """
        self.repo_path = Path(repo_path)
        self.remote_url = remote_url
        self.repo: Optional[Repo] = None
        self.path_validator = PathValidator(self.repo_path)
        
        self._initialize_repository()
        logger.info(f"Git repository manager initialized for: {self.repo_path}")
    
    def _initialize_repository(self) -> None:
        """Initialize or open the Git repository."""
        try:
            if self.repo_path.exists() and (self.repo_path / ".git").exists():
                # Repository already exists
                self.repo = Repo(self.repo_path)
                logger.info(f"Opened existing repository: {self.repo_path}")
            elif self.remote_url:
                # Clone repository with authentication support
                logger.info(f"Cloning repository from {self.remote_url} to {self.repo_path}")
                
                # Set up authentication environment if needed
                env = {}
                if self.remote_url.startswith('https://') and hasattr(self, '_username') and hasattr(self, '_password'):
                    # For HTTPS with username/password
                    auth_url = self.remote_url.replace('https://', f'https://{self._username}:{self._password}@')
                    self.repo = Repo.clone_from(auth_url, self.repo_path)
                else:
                    # For SSH or public repositories
                    self.repo = Repo.clone_from(self.remote_url, self.repo_path)
                    
                logger.info(f"Successfully cloned repository")
            else:
                # Initialize new repository
                self.repo_path.mkdir(parents=True, exist_ok=True)
                self.repo = Repo.init(self.repo_path)
                logger.info(f"Initialized new repository: {self.repo_path}")
                
        except Exception as e:
            logger.error(f"Failed to initialize repository: {e}")
            raise RuntimeError(f"Repository initialization failed: {e}")
    
    def set_credentials(self, username: str = None, password: str = None):
        """Set Git credentials for HTTPS authentication.
        
        Args:
            username: Git username
            password: Git password or token
        """
        if username:
            self._username = username
        if password:
            self._password = password
    
    def create_branch(self, branch_name: str, base_branch: str = "main") -> bool:
        """Create a new branch for the cluster configuration.
        
        Args:
            branch_name: Name of the new branch.
            base_branch: Base branch to create from.
            
        Returns:
            True if branch was created successfully, False otherwise.
        """
        try:
            if not self.repo:
                raise RuntimeError("Repository not initialized")
            
            # Check if branch already exists
            existing_branches = [branch.name for branch in self.repo.branches]
            if branch_name in existing_branches:
                logger.warning(f"Branch '{branch_name}' already exists")
                self.repo.git.checkout(branch_name)
                return True
            
            # Create and checkout new branch
            if base_branch in existing_branches:
                self.repo.git.checkout(base_branch)
            else:
                # Try to checkout main/master
                try:
                    self.repo.git.checkout("main")
                except GitCommandError:
                    try:
                        self.repo.git.checkout("master")
                    except GitCommandError:
                        logger.warning("Could not find main or master branch, staying on current branch")
            
            new_branch = self.repo.create_head(branch_name)
            new_branch.checkout()
            
            logger.info(f"Created and checked out branch: {branch_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create branch '{branch_name}': {e}")
            return False
    
    def add_file(self, file_path: Path, content: str) -> bool:
        """Add a file to the repository.
        
        Args:
            file_path: Path relative to repository root.
            content: File content.
            
        Returns:
            True if file was added successfully, False otherwise.
        """
        try:
            if not self.repo:
                raise RuntimeError("Repository not initialized")
            
            full_path = self.repo_path / file_path
            
            # Create directory structure if needed
            self.path_validator.create_directory_structure(file_path)
            
            # Write file content
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Add to git index
            self.repo.index.add([str(file_path)])
            
            logger.info(f"Added file to repository: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add file '{file_path}': {e}")
            return False
    
    def commit_changes(self, commit_message: str, author_name: str = "MCE Cluster Generator", author_email: str = "mce-gen@company.com") -> bool:
        """Commit changes to the repository.
        
        Args:
            commit_message: Commit message.
            author_name: Author name for the commit.
            author_email: Author email for the commit.
            
        Returns:
            True if commit was successful, False otherwise.
        """
        try:
            if not self.repo:
                raise RuntimeError("Repository not initialized")
            
            # Check if there are changes to commit
            if not self.repo.is_dirty():
                logger.warning("No changes to commit")
                return True
            
            # Create commit
            actor = git.Actor(author_name, author_email)
            self.repo.index.commit(commit_message, author=actor, committer=actor)
            
            logger.info(f"Committed changes with message: {commit_message}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to commit changes: {e}")
            return False
    
    def push_branch(self, branch_name: str, remote: str = "origin") -> bool:
        """Push branch to remote repository.
        
        Args:
            branch_name: Name of the branch to push.
            remote: Remote name.
            
        Returns:
            True if push was successful, False otherwise.
        """
        try:
            if not self.repo:
                raise RuntimeError("Repository not initialized")
            
            # Push branch
            origin = self.repo.remote(remote)
            origin.push(branch_name)
            
            logger.info(f"Pushed branch '{branch_name}' to remote '{remote}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to push branch '{branch_name}': {e}")
            return False
    
    def get_current_branch(self) -> Optional[str]:
        """Get the name of the current branch.
        
        Returns:
            Name of current branch or None if unable to determine.
        """
        try:
            if not self.repo:
                return None
            
            return self.repo.active_branch.name
            
        except Exception as e:
            logger.error(f"Failed to get current branch: {e}")
            return None
    
    def generate_branch_name(self, cluster_name: str, site: str) -> str:
        """Generate a branch name for the cluster configuration.
        
        Args:
            cluster_name: Name of the cluster.
            site: Site name.
            
        Returns:
            Generated branch name.
        """
        branch_name = f"add-cluster-{cluster_name}-{site}"
        logger.debug(f"Generated branch name: {branch_name}")
        return branch_name