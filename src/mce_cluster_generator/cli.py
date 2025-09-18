"""CLI interface for MCE cluster generator."""

import sys
import click
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .models.input import ClusterInput
from .generators.cluster_generator import ClusterGenerator
from .git_ops.repository import GitRepository
from .utils.logging_config import setup_logging
from .utils.exceptions import MCEGeneratorError

console = Console()


@click.group()
@click.option(
    '--log-level',
    default='INFO',
    type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']),
    help='Set the logging level'
)
@click.option(
    '--log-file',
    type=click.Path(path_type=Path),
    help='Log file path'
)
@click.pass_context
def cli(ctx, log_level: str, log_file: Optional[Path]):
    """MCE Cluster Generator - Generate cluster configurations with GitOps integration."""
    ctx.ensure_object(dict)
    ctx.obj['log_level'] = log_level
    ctx.obj['log_file'] = log_file
    
    # Setup logging
    setup_logging(level=log_level, log_file=log_file, console=console)


@cli.command()
@click.option('--cluster-name', required=True, help='Name of the cluster')
@click.option('--site', required=True, help='Site where the cluster will be deployed')
@click.option('--nodes', 'number_of_nodes', required=True, type=int, help='Number of worker nodes')
@click.option('--mce-name', required=True, help='MCE instance name')
@click.option('--environment', required=True, type=click.Choice(['prod', 'prep']), help='Environment type')
@click.option('--flavor', default='default', help='Cluster flavor template to use')
@click.option('--repo-path', type=click.Path(path_type=Path), help='Path to GitOps repository')
@click.option('--remote-url', help='Remote repository URL (for cloning)')
@click.option('--dry-run', is_flag=True, help='Generate configuration without committing to Git')
@click.option('--output-file', type=click.Path(path_type=Path), help='Output file path (for dry-run)')
@click.pass_context
def generate(
    ctx,
    cluster_name: str,
    site: str,
    number_of_nodes: int,
    mce_name: str,
    environment: str,
    flavor: str,
    repo_path: Optional[Path],
    remote_url: Optional[str],
    dry_run: bool,
    output_file: Optional[Path]
):
    """Generate cluster configuration and optionally commit to GitOps repository."""
    try:
        # Validate input parameters
        cluster_input = ClusterInput(
            cluster_name=cluster_name,
            site=site,
            number_of_nodes=number_of_nodes,
            mce_name=mce_name,
            environment=environment,
            flavor=flavor
        )
        
        console.print(f"[bold green]✓[/bold green] Input validation passed")
        
        # Initialize generator
        generator = ClusterGenerator()
        
        # Check if flavor exists
        if not generator.validate_flavor(flavor):
            available_flavors = generator.list_available_flavors()
            console.print(f"[bold red]✗[/bold red] Flavor '{flavor}' not found")
            console.print(f"Available flavors: {', '.join(available_flavors)}")
            sys.exit(1)
        
        # Generate configuration
        console.print(f"[bold blue]→[/bold blue] Generating configuration...")
        yaml_content = generator.generate_yaml_content(cluster_input)
        
        if dry_run:
            # Dry run mode - just output the configuration
            console.print(f"[bold green]✓[/bold green] Configuration generated successfully")
            
            if output_file:
                output_file.parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, 'w') as f:
                    f.write(yaml_content)
                console.print(f"[bold green]✓[/bold green] Configuration saved to: {output_file}")
            else:
                console.print("\n[bold]Generated Configuration:[/bold]")
                console.print(yaml_content)
            
            return
        
        # GitOps integration
        if not repo_path:
            console.print(f"[bold red]✗[/bold red] Repository path required for GitOps integration")
            console.print("Use --repo-path to specify the repository path, or --dry-run for testing")
            sys.exit(1)
        
        console.print(f"[bold blue]→[/bold blue] Initializing GitOps repository...")
        git_repo = GitRepository(repo_path, remote_url)
        
        # Generate branch name and create branch
        branch_name = git_repo.generate_branch_name(cluster_name, site)
        console.print(f"[bold blue]→[/bold blue] Creating branch: {branch_name}")
        
        if not git_repo.create_branch(branch_name):
            console.print(f"[bold red]✗[/bold red] Failed to create branch")
            sys.exit(1)
        
        # Get output path and add file
        output_path = generator.get_output_path(cluster_input)
        console.print(f"[bold blue]→[/bold blue] Adding file: {output_path}")
        
        if not git_repo.add_file(output_path, yaml_content):
            console.print(f"[bold red]✗[/bold red] Failed to add file to repository")
            sys.exit(1)
        
        # Commit changes
        commit_message = f"Add cluster configuration for {cluster_name} in {site}\n\nCluster: {cluster_name}\nSite: {site}\nEnvironment: {environment}\nNodes: {number_of_nodes}\nFlavor: {flavor}"
        
        console.print(f"[bold blue]→[/bold blue] Committing changes...")
        if not git_repo.commit_changes(commit_message):
            console.print(f"[bold red]✗[/bold red] Failed to commit changes")
            sys.exit(1)
        
        # Push branch
        console.print(f"[bold blue]→[/bold blue] Pushing branch to remote...")
        if not git_repo.push_branch(branch_name):
            console.print(f"[bold yellow]⚠[/bold yellow] Failed to push branch (you may need to push manually)")
        
        console.print(f"[bold green]✓[/bold green] Cluster configuration generated and committed successfully!")
        console.print(f"[bold]Branch:[/bold] {branch_name}")
        console.print(f"[bold]File:[/bold] {output_path}")
        console.print(f"[bold]Next step:[/bold] Create a merge request for branch '{branch_name}'")
        
    except MCEGeneratorError as e:
        console.print(f"[bold red]✗[/bold red] Generator error: {e.message}")
        if e.details:
            console.print(f"Details: {e.details}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Unexpected error: {e}")
        sys.exit(1)


@cli.command()
def list_flavors():
    """List available cluster flavors."""
    generator = ClusterGenerator()
    flavors = generator.list_available_flavors()
    
    console.print(f"[bold]Available Cluster Flavors:[/bold]")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Flavor", style="cyan")
    table.add_column("Status", style="green")
    
    for flavor in flavors:
        status = "✓ Valid" if generator.validate_flavor(flavor) else "✗ Invalid"
        table.add_row(flavor, status)
    
    console.print(table)


@cli.command()
@click.argument('flavor')
def validate_flavor(flavor: str):
    """Validate a specific cluster flavor template."""
    generator = ClusterGenerator()
    
    console.print(f"[bold blue]→[/bold blue] Validating flavor: {flavor}")
    
    if generator.validate_flavor(flavor):
        console.print(f"[bold green]✓[/bold green] Flavor '{flavor}' is valid")
    else:
        console.print(f"[bold red]✗[/bold red] Flavor '{flavor}' is invalid or not found")
        available = generator.list_available_flavors()
        console.print(f"Available flavors: {', '.join(available)}")
        sys.exit(1)


@cli.command()
@click.option('--cluster-name', required=True, help='Name of the cluster')
@click.option('--site', required=True, help='Site where the cluster will be deployed')
@click.option('--nodes', 'number_of_nodes', required=True, type=int, help='Number of worker nodes')
@click.option('--mce-name', required=True, help='MCE instance name')
@click.option('--environment', required=True, type=click.Choice(['prod', 'prep']), help='Environment type')
@click.option('--flavor', default='default', help='Cluster flavor template to use')
def preview(
    cluster_name: str,
    site: str,
    number_of_nodes: int,
    mce_name: str,
    environment: str,
    flavor: str
):
    """Preview the generated cluster configuration without creating files."""
    try:
        # Validate input parameters
        cluster_input = ClusterInput(
            cluster_name=cluster_name,
            site=site,
            number_of_nodes=number_of_nodes,
            mce_name=mce_name,
            environment=environment,
            flavor=flavor
        )
        
        # Generate configuration
        generator = ClusterGenerator()
        yaml_content = generator.generate_yaml_content(cluster_input)
        output_path = generator.get_output_path(cluster_input)
        
        console.print(f"[bold]Preview for cluster: {cluster_name}[/bold]")
        console.print(f"[bold]Output path:[/bold] {output_path}")
        console.print(f"[bold]Configuration:[/bold]")
        console.print(yaml_content)
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error: {e}")
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()