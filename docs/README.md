# MCE Cluster Generator - Documentation

Complete documentation for the MCE Cluster Generator API.

---

## Quick Links

- [Quick Start Guide](QUICK_START.md)
- [Development Guide](CLAUDE.md)
- [Docker Deployment](DOCKER_DEPLOYMENT_COMPLETE.md)
- [Helm Chart Guide](HELM_CHART_COMPLETE.md)
- [Architecture Overview](ARCHITECTURE_UPDATE.md)

---

## All Documentation

### Getting Started
- **[QUICK_START.md](QUICK_START.md)** - Quick start guide for common tasks
- **[CLAUDE.md](CLAUDE.md)** - Development guide and project overview

### Deployment
- **[DOCKER_DEPLOYMENT_COMPLETE.md](DOCKER_DEPLOYMENT_COMPLETE.md)** - Docker/Podman deployment guide
- **[HELM_CHART_COMPLETE.md](HELM_CHART_COMPLETE.md)** - Kubernetes Helm chart documentation
- **[../deploy/README.md](../deploy/README.md)** - Helm chart detailed reference
- **[../deploy/QUICKSTART.md](../deploy/QUICKSTART.md)** - Helm quick start

### Architecture & Code
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - ⭐ Clean Architecture, SOLID principles, design patterns
- **[REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)** - ⭐ Complete refactoring summary
- **[ARCHITECTURE_UPDATE.md](ARCHITECTURE_UPDATE.md)** - Application architecture and routing
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Project directory structure
- **[CODE_QUALITY.md](CODE_QUALITY.md)** - Code quality, refactoring, and SOLID principles

### Operations
- **[LOGGING.md](LOGGING.md)** - Logging configuration and usage

---

## Scripts

- **[../scripts/build-and-push.sh](../scripts/build-and-push.sh)** - Build and push Docker image
- **[../scripts/save-for-offline.sh](../scripts/save-for-offline.sh)** - Create offline deployment package

---

## Documentation by Topic

### 🚀 Getting Started

**New to the project?**
1. Start with [QUICK_START.md](QUICK_START.md) for immediate setup
2. Read [CLAUDE.md](CLAUDE.md) for development guidelines
3. Review [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) to understand the layout

### 🐳 Deployment

**Docker/Podman:**
- [DOCKER_DEPLOYMENT_COMPLETE.md](DOCKER_DEPLOYMENT_COMPLETE.md) - Complete Docker guide

**Kubernetes:**
- [HELM_CHART_COMPLETE.md](HELM_CHART_COMPLETE.md) - Complete Helm guide
- [../deploy/QUICKSTART.md](../deploy/QUICKSTART.md) - Quick start for Helm

### 🏗️ Architecture

**System Design:**
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - ⭐ Clean Architecture, SOLID principles, design patterns
- [ARCHITECTURE_UPDATE.md](ARCHITECTURE_UPDATE.md) - Entry point, routing, reverse proxy config
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Directory organization

**Code Quality:**
- **[REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)** - ⭐ Complete refactoring summary
- [CODE_QUALITY.md](CODE_QUALITY.md) - SOLID principles, refactoring, best practices

### 🔧 Operations

**Logging:**
- [LOGGING.md](LOGGING.md) - Complete logging guide (setup, usage, debugging)

---

## Quick Reference

### Starting the Application

```bash
# Local development
source .venv/bin/activate
python src/main.py
```

### API Endpoints

```
UI:             http://localhost:8000/
API Docs:       http://localhost:8000/docs
Health:         http://localhost:8000/health
Vendors:        http://localhost:8000/api/v1/clusters/vendors
Generate:       POST http://localhost:8000/api/v1/clusters/generate
```

### Docker Commands

```bash
# Build
podman build -t mce-cluster-generator:2.0.0 .

# Run
podman run -d -p 8000:8000 mce-cluster-generator:2.0.0

# Build and push to registry
../scripts/build-and-push.sh 2.0.0

# Create offline package
../scripts/save-for-offline.sh 2.0.0
```

### Helm Commands

```bash
# Install
helm install mce-api ../deploy

# Install with production values
helm install mce-api ../deploy -f ../deploy/values-prod.yaml

# Upgrade
helm upgrade mce-api ../deploy --reuse-values

# Uninstall
helm uninstall mce-api
```

---

## Configuration

### Environment Variables

See [CLAUDE.md#configuration-system](CLAUDE.md) for complete list.

Common variables:
```bash
DEFAULT_OCP_VERSION=4.16
DEFAULT_DNS_DOMAIN=cluster.company.com
PRIVATE_REGISTRY=registry.company.com
SUPPORTED_VENDORS=cisco,dell,dell-data,h100-gpu,h200-gpu
LOG_LEVEL=INFO
```

### Helm Values

See [../deploy/values.yaml](../deploy/values.yaml) for all configuration options.

---

## Contributing

For development guidelines, see [CLAUDE.md](CLAUDE.md).

For code quality standards, see [CODE_QUALITY.md](CODE_QUALITY.md).

---

## Need Help?

1. Check the [Quick Start Guide](QUICK_START.md)
2. Review [CLAUDE.md](CLAUDE.md) for development guidance
3. See [API Documentation](http://localhost:8000/docs) for endpoint details
4. Check deployment guides for your environment:
   - [Docker Guide](DOCKER_DEPLOYMENT_COMPLETE.md)
   - [Helm Guide](HELM_CHART_COMPLETE.md)
