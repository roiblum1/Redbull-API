# MCE Cluster Generator API

A FastAPI-based REST API for generating OpenShift cluster configurations with multi-vendor support.

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/roi/mce-cluster-generator)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.127+-green.svg)](https://fastapi.tiangolo.com/)

---

## Features

- 🎯 **Multi-Vendor Support** - Cisco, Dell, NVIDIA GPU nodes
- 📦 **YAML Generation** - MCE-compliant cluster configurations
- 🔧 **Configurable** - Environment-based configuration
- 🌐 **Web UI** - Interactive cluster configuration interface
- 📚 **OpenAPI Docs** - Auto-generated API documentation
- 🐳 **Container Ready** - Docker/Podman support
- ⎈ **Kubernetes Ready** - Helm chart included
- 🔒 **Air-gapped Support** - Disconnected deployment ready

---

## Quick Start

### Local Development

```bash
# Clone repository
git clone <repository-url>
cd Redbull-API

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py
```

**Access:**
- **UI**: http://localhost:8000/
- **API Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

### Docker/Podman

```bash
# Build image
podman build -t mce-cluster-generator:2.0.0 .

# Run container
podman run -d -p 8000:8000 \
  -e DEFAULT_DNS_DOMAIN=cluster.company.com \
  -e PRIVATE_REGISTRY=registry.company.com \
  mce-cluster-generator:2.0.0
```

### Kubernetes (Helm)

```bash
# Install with default values
helm install mce-api ./deploy

# Install with custom values
helm install mce-api ./deploy -f ./deploy/values-prod.yaml
```

---

## Project Structure

```
.
├── src/                          # Application source code
│   ├── api/                      # API routers and middleware
│   ├── config/                   # Configuration and constants
│   ├── defaults/                 # Default values and templates
│   ├── generators/               # Cluster YAML generators
│   ├── models/                   # Pydantic models
│   ├── services/                 # Business logic services
│   ├── static/                   # Web UI files
│   ├── utils/                    # Utility functions
│   └── main.py                   # Application entry point
├── deploy/                       # Helm chart for Kubernetes
├── docs/                         # Documentation
├── scripts/                      # Utility scripts
├── offline-deployment/           # Offline deployment package
├── requirements.txt              # Python dependencies
└── Dockerfile                    # Container image definition
```

---

## Configuration

All configuration via environment variables:

```bash
# Server
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# Application
DEFAULT_OCP_VERSION=4.16
DEFAULT_DNS_DOMAIN=cluster.company.com
PRIVATE_REGISTRY=registry.company.com
SUPPORTED_VENDORS=cisco,dell,dell-data,h100-gpu,h200-gpu

# Security
CORS_ORIGINS=*
```

See [docs/CLAUDE.md](docs/CLAUDE.md) for complete configuration options.

---

## API Endpoints

### UI
- `GET /` - Web interface

### Health
- `GET /health` - Health check
- `GET /api/health` - API health check

### Clusters (API v1)
- `GET /api/v1/clusters/defaults` - Get default values
- `GET /api/v1/clusters/vendors` - List supported vendors
- `GET /api/v1/clusters/versions` - List supported OCP versions
- `POST /api/v1/clusters/generate` - Generate cluster YAML
- `POST /api/v1/clusters/preview` - Preview cluster YAML

### Documentation
- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc documentation

---

## Documentation

### Getting Started
- [Quick Start](docs/QUICK_START.md) - Quick start guide
- [Architecture](docs/ARCHITECTURE_UPDATE.md) - System architecture
- [Development Guide](docs/CLAUDE.md) - Development guidelines

### Deployment
- [Docker Deployment](docs/DOCKER_DEPLOYMENT_COMPLETE.md) - Docker/Podman deployment
- [Helm Chart](docs/HELM_CHART_COMPLETE.md) - Kubernetes deployment
- [Helm Quick Start](deploy/QUICKSTART.md) - Helm quick start

### Technical Details
- [Code Improvements](docs/IMPROVEMENTS_COMPLETED.md) - Code quality improvements
- [Logging Setup](docs/LOGGING_QUICK_WINS_COMPLETED.md) - Logging configuration
- [Refactoring Summary](docs/REFACTORING_SUMMARY.md) - Refactoring details

---

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src
```

### Building Docker Image

```bash
# Build and optionally push to registry
./scripts/build-and-push.sh 2.0.0
```

### Creating Offline Package

```bash
# Create offline deployment package
./scripts/save-for-offline.sh 2.0.0
```

---

## Deployment Scenarios

### Connected Environment (Production)

```bash
# Using Helm
helm install mce-api ./deploy -f ./deploy/values-prod.yaml \
  --set config.defaultDnsDomain=cluster.company.com \
  --set config.privateRegistry=registry.company.com
```

### Disconnected/Air-gapped Environment

```bash
# 1. Build and save offline package
./scripts/save-for-offline.sh 2.0.0

# 2. Transfer offline-deployment/ directory to disconnected system

# 3. Load and deploy
cd offline-deployment/
gunzip mce-cluster-generator-*.tar.gz
podman load -i mce-cluster-generator-*.tar
helm install mce-api ../deploy -f ../deploy/values-disconnected.yaml
```

---

## Supported Vendors

- **Cisco UCS** - `cisco`
- **Dell PowerEdge** - `dell`
- **Dell Data Services** - `dell-data`
- **NVIDIA H100 GPU** - `h100-gpu`
- **NVIDIA H200 GPU** - `h200-gpu`

To add a new vendor, see [docs/CLAUDE.md#adding-a-new-vendor](docs/CLAUDE.md).

---

## Supported OpenShift Versions

- OpenShift 4.15
- OpenShift 4.16

---

## Example Usage

### Generate Cluster Configuration

```bash
curl -X POST http://localhost:8000/api/v1/clusters/generate \
  -H "Content-Type: application/json" \
  -d '{
    "cluster_name": "prod-cluster",
    "site": "datacenter-1",
    "vendor_configs": [
      {
        "vendor": "dell",
        "number_of_nodes": 3,
        "infra_env_name": "dell-prod"
      },
      {
        "vendor": "cisco",
        "number_of_nodes": 2,
        "infra_env_name": "cisco-prod"
      }
    ],
    "ocp_version": "4.16",
    "dns_domain": "cluster.company.com"
  }'
```

---

## Requirements

- Python 3.11+
- FastAPI 0.127+
- Pydantic 2.12+
- Docker/Podman (for containerized deployment)
- Kubernetes/Helm (for k8s deployment)

---

## Security

- Non-root user in containers (UID 1000)
- Configurable CORS origins
- Health checks enabled
- No hardcoded secrets
- Environment-based configuration

---

## Contributing

See [docs/CLAUDE.md](docs/CLAUDE.md) for development guidelines.

---

## License

[Add your license here]

---

## Support

- **Documentation**: See [docs/](docs/) directory
- **API Docs**: http://localhost:8000/docs
- **Issues**: [GitHub Issues](https://github.com/roi/mce-cluster-generator/issues)

---

## Changelog

### v2.0.0
- ✅ Unified entry point (merged start.py into main.py)
- ✅ Helm chart for Kubernetes deployment
- ✅ Offline deployment support
- ✅ Improved logging with correlation IDs
- ✅ SOLID principles refactoring
- ✅ Web UI for cluster configuration
- ✅ Multi-vendor support
- ✅ Production-ready Docker image
