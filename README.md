# MCE Cluster Generator

A comprehensive tool for generating cluster configurations for MCE (Multi-Cluster Engine) environments with GitOps integration. Available as both **CLI tool** and **REST API**.

## Features

- **🎯 Dual Interface**: Both CLI and REST API for maximum flexibility
- **📋 Flexible Template System**: YAML-based templates for different cluster flavors
- **✅ Comprehensive Validation**: Pydantic-based validation for all input parameters
- **🔄 GitOps Integration**: Automatic branch creation, file generation, and commit/push workflows
- **📁 Path Management**: Ensures correct repository structure exists or creates it
- **🎨 Rich CLI Interface**: User-friendly command-line interface with colored output
- **📡 REST API**: Full-featured API with automatic documentation
- **📊 Extensive Logging**: Configurable logging with file and console output
- **🛡️ Error Handling**: Comprehensive error handling with custom exceptions

## Quick Start

### 🚀 Start the API Server

```bash
# Clone and setup
git clone <repository-url>
cd mce-cluster-generator
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Start the API server
python start.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Interactive API**: http://localhost:8000/redoc

### 📋 API Usage Examples

#### List Available Flavors
```bash
curl -X GET "http://localhost:8000/api/v1/clusters/flavors"
```

#### Preview Cluster Configuration
```bash
curl -X POST "http://localhost:8000/api/v1/clusters/preview" \
  -H "Content-Type: application/json" \
  -d '{
    "cluster_name": "my-cluster",
    "site": "datacenter-1",
    "number_of_nodes": 3,
    "mce_name": "mce-prod",
    "environment": "prod",
    "flavor": "default"
  }'
```

#### Generate Cluster (Dry Run)
```bash
curl -X POST "http://localhost:8000/api/v1/clusters/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "cluster_name": "api-cluster",
    "site": "datacenter-1",
    "number_of_nodes": 5,
    "mce_name": "mce-prod",
    "environment": "prod",
    "flavor": "default",
    "author_name": "API User",
    "author_email": "user@company.com"
  }'
```

#### Generate with GitOps Integration
```bash
curl -X POST "http://localhost:8000/api/v1/clusters/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "cluster_name": "production-cluster",
    "site": "datacenter-1",
    "number_of_nodes": 5,
    "mce_name": "mce-prod",
    "environment": "prod",
    "flavor": "default",
    "repo_path": "/path/to/gitops/repo",
    "remote_url": "git@gitlab.company.com:infrastructure/gitops-clusters.git",
    "author_name": "Production Deploy",
    "author_email": "deploy@company.com"
  }'
```

### 🖥️ CLI Usage

```bash
# List available flavors
python -m src.cli list-flavors

# Preview configuration
python -m src.cli preview \
  --cluster-name "my-cluster" \
  --site "datacenter-1" \
  --nodes 3 \
  --mce-name "mce-prod" \
  --environment "prod" \
  --flavor "default"

# Generate with GitOps integration
python -m src.cli generate \
  --cluster-name "my-cluster" \
  --site "datacenter-1" \
  --nodes 3 \
  --mce-name "mce-prod" \
  --environment "prod" \
  --flavor "default" \
  --repo-path "/path/to/gitops/repo"
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Server Settings
HOST=0.0.0.0
PORT=8000
DEBUG=false

# GitOps Repository Configuration
GITOPS_REPO_URL=git@gitlab.company.com:infrastructure/gitops-clusters.git
GITOPS_REPO_PATH=/tmp/gitops-repo
GITOPS_BRANCH_BASE=main

# Git Authentication
REPO_ACCESS_MODE=ssh
GIT_SSH_KEY_PATH=/etc/mce-api/ssh_key
DEFAULT_AUTHOR_NAME=MCE API
DEFAULT_AUTHOR_EMAIL=mce-api@company.com

# Registry Settings
PRIVATE_REGISTRY=registry.internal.company.com

# Security
CORS_ORIGINS=https://your-frontend.com,http://localhost:3000
```

### Repository Structure

Generated files follow this structure:
```
sites/<site>/mce-tenant-cluster/mce-<environment>/<mce-name>/ocp4-<cluster-name>.yaml
```

Example:
```
sites/datacenter-1/mce-tenant-cluster/mce-prod/mce-main/ocp4-my-cluster.yaml
```

## Available Flavors

### Built-in Flavors

1. **default**: Standard cluster configuration
   - Agent-based platform
   - Classic bare-metal infrastructure
   - Standard network and machine configs

2. **portworks**: PortWorks storage integration
   - PortWorks-specific bare-metal configuration
   - Additional storage configuration
   - PortWorks registry mirrors

3. **powerflex**: PowerFlex storage integration
   - PowerFlex-specific bare-metal configuration
   - Dell storage configuration
   - Dell registry mirrors

### Adding New Flavors

1. Create a new YAML template in `src/templates/`:

```yaml
# src/templates/my-custom-flavor.yaml
clusterName: "{{ cluster_name }}"
platform: agent
nodePool:
  - name: "{{ cluster_name }}-nodepool"
    replicas: {{ number_of_nodes }}
    labels:
      allowDeletion: false
      minReplicas: "{{ number_of_nodes - 1 }}"
      maxReplicas: "{{ number_of_nodes + 1 }}"
    agentLabelSelector:
      nodeLabelKey: infraenv
      nodeLabelValue: my-custom-baremetal
    configs:
      - "nm-conf-{{ cluster_name }}"
      - worker-kubeconfig
      - my-custom-config
mcConfig:
  - "nm-conf-{{ cluster_name }}"
  - worker-kubeconfig
  - my-custom-config
idms:
  mirrors:
    - source: registry.redhat.io
      mirrors:
        - "{{ private_registry }}/redhat"
    - source: my-custom-registry.com
      mirrors:
        - "{{ private_registry }}/my-custom"
```

2. Available template variables:
   - `{{ cluster_name }}`: Cluster name
   - `{{ number_of_nodes }}`: Number of worker nodes
   - `{{ site }}`: Deployment site
   - `{{ mce_name }}`: MCE instance name
   - `{{ environment }}`: Environment (prod/prep)
   - `{{ private_registry }}`: Private registry URL

3. Restart the API server to pick up the new flavor

### Modifying Existing Flavors

1. Edit the template file in `src/templates/`
2. Validate the template:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/clusters/flavors/my-flavor/validate"
   ```
3. Test with preview:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/clusters/preview" \
     -H "Content-Type: application/json" \
     -d '{"cluster_name": "test", "site": "test", "number_of_nodes": 1, "mce_name": "test", "environment": "prep", "flavor": "my-flavor"}'
   ```

## API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/clusters/flavors` | List available flavors |
| GET | `/api/v1/clusters/flavors/{flavor}/validate` | Validate specific flavor |
| GET | `/api/v1/clusters/flavors/{flavor}/template` | Get raw template content |
| POST | `/api/v1/clusters/preview` | Preview cluster configuration |
| POST | `/api/v1/clusters/generate` | Generate cluster configuration |

### Request Models

#### Generate/Preview Request
```json
{
  "cluster_name": "string",
  "site": "string", 
  "number_of_nodes": 1,
  "mce_name": "string",
  "environment": "prod" | "prep",
  "flavor": "string",
  "repo_path": "string (optional)",
  "remote_url": "string (optional)",
  "author_name": "string (optional)",
  "author_email": "string (optional)"
}
```

### Response Models

#### Generate Response
```json
{
  "cluster_name": "string",
  "output_path": "string",
  "flavor_used": "string",
  "dry_run": boolean,
  "git_info": {
    "branch_name": "string",
    "commit_message": "string", 
    "file_path": "string",
    "pushed": boolean
  },
  "yaml_content": "string (dry-run only)",
  "generated_at": "datetime",
  "message": "string"
}
```

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY start.py .

EXPOSE 8000
CMD ["python", "start.py"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mce-cluster-generator
spec:
  replicas: 2
  selector:
    matchLabels:
      app: mce-cluster-generator
  template:
    metadata:
      labels:
        app: mce-cluster-generator
    spec:
      containers:
      - name: api
        image: mce-cluster-generator:latest
        ports:
        - containerPort: 8000
        env:
        - name: GITOPS_REPO_URL
          value: "git@gitlab.company.com:infrastructure/gitops-clusters.git"
        - name: PRIVATE_REGISTRY
          value: "registry.internal.company.com"
---
apiVersion: v1
kind: Service
metadata:
  name: mce-cluster-generator
spec:
  selector:
    app: mce-cluster-generator
  ports:
  - port: 80
    targetPort: 8000
```

## Development

### Project Structure

```
├── src/
│   ├── api/                    # FastAPI application
│   │   ├── models/            # Request/response models
│   │   └── routers/           # API endpoints
│   ├── models/                # Core data models
│   ├── generators/            # Template processing
│   ├── git_ops/              # GitOps integration
│   ├── templates/            # Flavor templates
│   ├── utils/                # Utilities
│   ├── config.py             # Configuration
│   ├── main.py               # FastAPI app
│   └── cli.py                # CLI interface
├── examples/                 # Usage examples
├── requirements.txt          # Dependencies
├── start.py                  # Server startup
└── .env.example             # Environment template
```

### Adding Features

1. **New API endpoints**: Add to `src/api/routers/`
2. **New validation**: Extend `src/models/`
3. **New flavors**: Add templates to `src/templates/`
4. **New utilities**: Add to `src/utils/`

### Testing

```bash
# Test CLI
python -m src.cli list-flavors

# Test API
python start.py &
curl -X GET "http://localhost:8000/health"

# Run example client
python examples/api_client_example.py
```

## Security Considerations

- 🔐 Configure proper SSH keys for GitOps access
- 🛡️ Use HTTPS in production
- 🔒 Secure private registry credentials
- 📝 Validate all input parameters
- 🚫 No secrets in logs or responses

## License

[Your License Here]

## Support

- **Documentation**: http://localhost:8000/docs
- **Issues**: GitHub Issues
- **API Reference**: http://localhost:8000/redoc