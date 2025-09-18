#!/usr/bin/env python3
"""Example API client for MCE Cluster Generator."""

import requests
import json
from typing import Dict, Any


class MCEClusterAPIClient:
    """Simple client for MCE Cluster Generator API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health."""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def list_flavors(self) -> Dict[str, Any]:
        """List available cluster flavors."""
        response = self.session.get(f"{self.base_url}/api/v1/clusters/flavors")
        response.raise_for_status()
        return response.json()
    
    def validate_flavor(self, flavor_name: str) -> Dict[str, Any]:
        """Validate a specific flavor."""
        response = self.session.get(f"{self.base_url}/api/v1/clusters/flavors/{flavor_name}/validate")
        response.raise_for_status()
        return response.json()
    
    def get_flavor_template(self, flavor_name: str) -> str:
        """Get raw template content for a flavor."""
        response = self.session.get(f"{self.base_url}/api/v1/clusters/flavors/{flavor_name}/template")
        response.raise_for_status()
        return response.text
    
    def preview_cluster(self, cluster_config: Dict[str, Any]) -> Dict[str, Any]:
        """Preview cluster configuration."""
        response = self.session.post(
            f"{self.base_url}/api/v1/clusters/preview",
            json=cluster_config
        )
        response.raise_for_status()
        return response.json()
    
    def generate_cluster(self, cluster_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate cluster configuration."""
        response = self.session.post(
            f"{self.base_url}/api/v1/clusters/generate",
            json=cluster_config
        )
        response.raise_for_status()
        return response.json()


def main():
    """Example usage of the API client."""
    client = MCEClusterAPIClient()
    
    print("🚀 MCE Cluster Generator API Client Example")
    print("=" * 50)
    
    # Health check
    print("\n1. Health Check:")
    health = client.health_check()
    print(f"   Status: {health['status']}")
    print(f"   Version: {health['version']}")
    
    # List flavors
    print("\n2. Available Flavors:")
    flavors = client.list_flavors()
    for flavor in flavors['flavors']:
        status = "✅" if flavor['valid'] else "❌"
        print(f"   {status} {flavor['name']}")
    
    # Validate a specific flavor
    print("\n3. Flavor Validation:")
    validation = client.validate_flavor("default")
    print(f"   {validation['message']}")
    
    # Preview cluster configuration
    print("\n4. Preview Cluster Configuration:")
    preview_config = {
        "cluster_name": "api-example",
        "site": "datacenter-1",
        "number_of_nodes": 3,
        "mce_name": "mce-prod",
        "environment": "prod",
        "flavor": "default"
    }
    
    preview = client.preview_cluster(preview_config)
    print(f"   Cluster: {preview['cluster_name']}")
    print(f"   Output Path: {preview['output_path']}")
    print(f"   Flavor Used: {preview['flavor_used']}")
    print(f"   Generated At: {preview['generated_at']}")
    
    # Generate cluster (dry-run)
    print("\n5. Generate Cluster (Dry-Run):")
    generate_config = {
        "cluster_name": "api-test-cluster",
        "site": "datacenter-2",
        "number_of_nodes": 5,
        "mce_name": "mce-prod",
        "environment": "prod",
        "flavor": "portworks",
        "author_name": "API Client",
        "author_email": "api-client@company.com"
    }
    
    result = client.generate_cluster(generate_config)
    print(f"   Cluster: {result['cluster_name']}")
    print(f"   Dry Run: {result['dry_run']}")
    print(f"   Message: {result['message']}")
    
    print("\n✅ API Client Example Complete!")


if __name__ == "__main__":
    main()