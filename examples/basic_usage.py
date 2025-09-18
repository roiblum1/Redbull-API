#!/usr/bin/env python3
"""Basic usage example for MCE Cluster Generator."""

from pathlib import Path
from mce_cluster_generator.models.input import ClusterInput
from mce_cluster_generator.generators.cluster_generator import ClusterGenerator
from mce_cluster_generator.utils.logging_config import setup_logging

def main():
    """Demonstrate basic usage of the MCE Cluster Generator."""
    # Setup logging
    setup_logging(level="INFO")
    
    # Create input parameters
    cluster_input = ClusterInput(
        cluster_name="example-cluster",
        site="datacenter-east",
        number_of_nodes=3,
        mce_name="mce-production",
        environment="prod",
        flavor="default"
    )
    
    print(f"Generating configuration for cluster: {cluster_input.cluster_name}")
    
    # Initialize generator
    generator = ClusterGenerator()
    
    # List available flavors
    print(f"Available flavors: {generator.list_available_flavors()}")
    
    # Generate configuration
    yaml_content = generator.generate_yaml_content(cluster_input)
    output_path = generator.get_output_path(cluster_input)
    
    print(f"Output path: {output_path}")
    print("Generated configuration:")
    print("-" * 50)
    print(yaml_content)

if __name__ == "__main__":
    main()