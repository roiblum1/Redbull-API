# MCE Cluster Generator

A comprehensive REST API for generating cluster configurations for MCE (Multi-Cluster Engine) environments with GitOps integration.

## Features

- **📋 Flexible Template System**: YAML-based templates for different cluster flavors
- **✅ Comprehensive Validation**: Pydantic-based validation for all input parameters
- **🔄 GitOps Integration**: Automatic branch creation, file generation, and commit/push workflows
- **📁 Path Management**: Ensures correct repository structure exists or creates it
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

### GitOps Repository Authentication

#### Password/Token Authentication (HTTPS)

For repositories that require username/password or token authentication:

1. **Set environment variables**:
```bash
# Use HTTPS authentication
REPO_ACCESS_MODE=https
GITOPS_REPO_URL=https://gitlab.company.com/infrastructure/gitops-clusters.git

# For username/password authentication
GIT_USERNAME=your-username
GIT_PASSWORD=your-password

# For token authentication (recommended)
GIT_USERNAME=your-username
GIT_PASSWORD=your-personal-access-token
```

2. **GitHub Personal Access Token**:
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Generate new token with `repo` permissions
   - Use token as `GIT_PASSWORD`

3. **GitLab Personal Access Token**:
   - Go to GitLab User Settings → Access Tokens
   - Create token with `write_repository` scope
   - Use token as `GIT_PASSWORD`

4. **Azure DevOps Personal Access Token**:
   - Go to User Settings → Personal Access Tokens
   - Create token with `Code (read & write)` permissions
   - Use token as `GIT_PASSWORD`

#### Example configurations:

**GitHub with Token**:
```bash
REPO_ACCESS_MODE=https
GITOPS_REPO_URL=https://github.com/your-org/gitops-clusters.git
GIT_USERNAME=your-github-username
GIT_PASSWORD=ghp_your_personal_access_token
```

**GitLab with Token**:
```bash
REPO_ACCESS_MODE=https
GITOPS_REPO_URL=https://gitlab.company.com/infrastructure/gitops-clusters.git
GIT_USERNAME=your-gitlab-username
GIT_PASSWORD=glpat-your_personal_access_token
```

**Corporate Git with Username/Password**:
```bash
REPO_ACCESS_MODE=https
GITOPS_REPO_URL=https://git.company.com/infrastructure/gitops-clusters.git
GIT_USERNAME=your-domain-username
GIT_PASSWORD=your-domain-password
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

#### Quick Start with Docker

1. **Build and run with Docker**:
```bash
# Build the image
docker build -t mce-cluster-generator .

# Run with environment variables
docker run -d \
  -p 8000:8000 \
  -e GITOPS_REPO_URL="https://github.com/your-org/gitops-clusters.git" \
  -e GIT_USERNAME="your-username" \
  -e GIT_PASSWORD="your-token" \
  -e REPO_ACCESS_MODE="https" \
  --name mce-api \
  mce-cluster-generator
```

2. **Using Docker Compose** (recommended):
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env

# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

#### Environment Configuration for Docker

Create a `.env` file for Docker Compose:

```bash
# GitOps Repository (required for full functionality)
GITOPS_REPO_URL=https://github.com/your-org/gitops-clusters.git

# For HTTPS authentication
REPO_ACCESS_MODE=https
GIT_USERNAME=your-username
GIT_PASSWORD=your-personal-access-token

# For SSH authentication (advanced)
REPO_ACCESS_MODE=ssh
SSH_KEY_PATH=./ssh-keys

# Optional settings
DEFAULT_AUTHOR_NAME=MCE API Docker
DEFAULT_AUTHOR_EMAIL=mce-api@company.com
PRIVATE_REGISTRY=registry.internal.company.com
CORS_ORIGINS=*
```

#### SSH Key Setup for Docker

If using SSH authentication:

1. **Create SSH key directory**:
```bash
mkdir -p ssh-keys
chmod 700 ssh-keys
```

2. **Copy your SSH private key**:
```bash
cp ~/.ssh/id_rsa ssh-keys/id_rsa
chmod 600 ssh-keys/id_rsa
```

3. **Update docker-compose.yml SSH_KEY_PATH**:
```bash
SSH_KEY_PATH=./ssh-keys
```

#### Production Docker Setup

For production deployment with security best practices:

```bash
# Create dedicated network
docker network create mce-network

# Run with production settings
docker run -d \
  --name mce-api-prod \
  --network mce-network \
  -p 8000:8000 \
  -e DEBUG=false \
  -e LOG_LEVEL=WARNING \
  -e GITOPS_REPO_URL="your-repo-url" \
  -e GIT_USERNAME="production-user" \
  -e GIT_PASSWORD="production-token" \
  -e CORS_ORIGINS="https://your-production-frontend.com" \
  -v /secure/path/to/logs:/app/logs \
  -v /secure/path/to/gitops:/app/gitops-repos \
  --restart unless-stopped \
  mce-cluster-generator
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
│   └── main.py               # FastAPI app
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