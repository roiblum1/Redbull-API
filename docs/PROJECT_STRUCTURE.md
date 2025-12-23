# Project Structure

Clean and organized project structure for the MCE Cluster Generator API.

---

## Directory Layout

```
Redbull-API/
├── README.md                      # Main project README
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Container image definition
├── docker-compose.yml             # Docker Compose configuration
│
├── src/                           # Application source code
│   ├── main.py                    # Application entry point
│   ├── api/                       # API routers and middleware
│   │   ├── routers/              # API endpoint routers
│   │   └── middleware/           # Request/response middleware
│   ├── config/                    # Configuration
│   │   ├── settings.py           # Application settings
│   │   └── constants.py          # Constants and enums
│   ├── defaults/                  # Default values and templates
│   │   └── image_content_sources/ # OCP version-specific configs
│   ├── generators/                # YAML generators
│   │   └── cluster_builder.py    # Cluster configuration builder
│   ├── models/                    # Pydantic models
│   │   ├── input.py              # Input models
│   │   ├── requests.py           # API request models
│   │   └── responses.py          # API response models
│   ├── services/                  # Business logic
│   │   ├── validators.py         # Validation services
│   │   ├── converters.py         # Data conversion services
│   │   └── config_builder.py    # Configuration building
│   ├── static/                    # Web UI
│   │   ├── index.html            # Main UI page
│   │   ├── css/                  # Stylesheets
│   │   └── js/                   # JavaScript
│   └── utils/                     # Utilities
│       ├── logging_config.py     # Logging setup
│       └── exceptions.py         # Custom exceptions
│
├── deploy/                        # Kubernetes/Helm deployment
│   ├── Chart.yaml                # Helm chart definition
│   ├── values.yaml               # Default values
│   ├── values-dev.yaml           # Development values
│   ├── values-prod.yaml          # Production values
│   ├── values-disconnected.yaml  # Air-gapped values
│   ├── templates/                # Helm templates
│   ├── README.md                 # Helm chart documentation
│   └── QUICKSTART.md             # Helm quick start
│
├── docs/                          # Documentation
│   ├── README.md                 # Documentation index
│   ├── QUICK_START.md            # Quick start guide
│   ├── CLAUDE.md                 # Development guide
│   ├── ARCHITECTURE_UPDATE.md    # Architecture details
│   ├── DOCKER_DEPLOYMENT_COMPLETE.md  # Docker deployment
│   ├── HELM_CHART_COMPLETE.md    # Helm deployment
│   ├── REFACTORING_SUMMARY.md    # Code refactoring
│   ├── IMPROVEMENTS_COMPLETED.md # Code improvements
│   ├── LOGGING_IMPROVEMENTS.md   # Logging overview
│   ├── LOGGING_QUICK_WINS_COMPLETED.md  # Logging setup
│   └── PROJECT_STRUCTURE.md      # This file
│
├── scripts/                       # Utility scripts
│   ├── build-and-push.sh         # Build and push Docker image
│   └── save-for-offline.sh       # Create offline package
│
├── sites/                         # Example cluster configurations
│   ├── datacenter-1/
│   ├── datacenter-east/
│   ├── datacenter-north/
│   └── datacenter-west/
│
└── offline-deployment/            # Generated offline package
    ├── mce-cluster-generator-*.tar.gz
    ├── DEPLOYMENT-INSTRUCTIONS.txt
    ├── docker-compose.offline.yml
    └── checksums.txt
```

---

## Key Directories

### `src/` - Application Code

The main application source code, organized by functional areas:

- **`main.py`** - Single entry point for the application
- **`api/`** - FastAPI routers and HTTP middleware
- **`config/`** - Settings and configuration constants
- **`models/`** - Pydantic data models (input validation, API contracts)
- **`services/`** - Business logic layer (validators, converters, builders)
- **`generators/`** - YAML generation logic
- **`defaults/`** - Default configurations and templates
- **`static/`** - Web UI files (HTML, CSS, JavaScript)
- **`utils/`** - Utility functions (logging, exceptions)

### `deploy/` - Kubernetes Deployment

Helm chart for deploying to Kubernetes:

- **`Chart.yaml`** - Helm chart metadata
- **`values.yaml`** - Default configuration values
- **`values-*.yaml`** - Environment-specific configurations
- **`templates/`** - Kubernetes resource templates
- **Documentation** - Deployment guides

### `docs/` - Documentation

All project documentation in one place:

- **User guides** - Quick start, deployment guides
- **Developer guides** - Architecture, code quality
- **Operations** - Logging, monitoring
- **Reference** - API documentation, configuration

### `scripts/` - Utility Scripts

Helper scripts for common tasks:

- **`build-and-push.sh`** - Build Docker image and push to registry
- **`save-for-offline.sh`** - Create offline deployment package

---

## File Organization Principles

### 1. Separation of Concerns

- **Source code** in `src/`
- **Documentation** in `docs/`
- **Deployment configs** in `deploy/`
- **Utility scripts** in `scripts/`

### 2. Single Entry Point

- Application runs from `src/main.py`
- No wrapper scripts needed
- Clear, simple startup

### 3. Clear Dependencies

```
main.py
  ↓
api/ (routers + middleware)
  ↓
services/ (business logic)
  ↓
generators/ + defaults/ (YAML generation)
  ↓
models/ (data validation)
  ↓
config/ + utils/ (foundation)
```

### 4. Self-Documenting Structure

- Directory names describe contents
- README files in key directories
- Consistent naming conventions

---

## Configuration Files

### Root Level
- **`README.md`** - Project overview
- **`requirements.txt`** - Python dependencies
- **`Dockerfile`** - Container build instructions
- **`docker-compose.yml`** - Local Docker deployment

### Hidden/Config Files
- **`.dockerignore`** - Files to exclude from Docker builds
- **`.gitignore`** - Files to exclude from git
- **`.env.example`** - Example environment variables

---

## Source Code Organization

### API Layer (`src/api/`)

```
api/
├── routers/
│   └── clusters.py          # Cluster management endpoints
└── middleware/
    └── logging_middleware.py  # Request/response logging
```

### Business Logic (`src/services/`)

```
services/
├── validators.py            # Input validation
├── converters.py            # Data transformation
└── config_builder.py        # Config list building
```

### Models (`src/models/`)

```
models/
├── input.py                 # Domain models
├── requests.py              # API request models
└── responses.py             # API response models
```

### Configuration (`src/config/`)

```
config/
├── settings.py              # Application settings (env vars)
└── constants.py             # Enums and constants
```

---

## Routes Structure

### UI Routes
- `GET /` → Web interface
- `GET /static/*` → Static files (CSS, JS, images)

### API Routes
- `GET /api/health` → API health check
- `GET /api/v1/clusters/*` → Cluster operations

### Documentation Routes
- `GET /docs` → Swagger UI
- `GET /redoc` → ReDoc documentation

### Health Routes
- `GET /health` → Health check (backward compatible)

---

## Deployment Artifacts

### Docker
- **`Dockerfile`** - Multi-stage build for optimal image size
- **Image**: `docker.io/roi12345/mce-cluster-generator:2.0.0`
- **Size**: 304 MB (uncompressed), 106 MB (offline package)

### Kubernetes
- **Helm Chart**: `deploy/` directory
- **Deployments**: Development, Production, Air-gapped
- **Resources**: Deployment, Service, Ingress, PVC, HPA

### Offline Deployment
- **Package**: `offline-deployment/` directory
- **Contents**: Compressed image, instructions, compose file, checksums
- **Size**: ~106 MB

---

## Adding New Components

### New API Endpoint

1. Add route to `src/api/routers/clusters.py` (or create new router)
2. Add request/response models to `src/models/`
3. Add business logic to `src/services/`
4. Update API documentation

### New Vendor

1. Add to `SUPPORTED_VENDORS` in `src/config/constants.py`
2. Optionally add display name in `Vendor.display_names()`
3. Done! (Auto-validated everywhere)

### New Configuration Option

1. Add to `src/config/settings.py`
2. Add to Helm `values.yaml` if applicable
3. Update documentation

---

## Best Practices

### Code Organization
- Keep files focused (Single Responsibility)
- Use services for business logic
- Use models for data validation
- Keep routers thin (delegate to services)

### Documentation
- README in each major directory
- Code comments for complex logic
- API documentation via OpenAPI
- Keep docs in `docs/` directory

### Configuration
- Environment variables for runtime config
- Constants file for application constants
- Helm values for Kubernetes deployment
- Clear separation of concerns

---

## Clean Up

### Files Removed
- ✅ `start.py` - Merged into main.py
- ✅ `fix_imports.py` - No longer needed
- ✅ Root-level `*.md` files - Moved to `docs/`
- ✅ Root-level `*.sh` files - Moved to `scripts/`

### Files Kept (Backward Compatibility)
- `docker-compose.yml` - For local development
- `sites/` - Example configurations
- `.env.example` - Environment template

---

## Maintenance

### Regular Tasks
1. Update dependencies in `requirements.txt`
2. Keep documentation in sync with code
3. Update Helm chart version when releasing
4. Rebuild Docker images for new versions

### Version Updates
1. Update version in `src/config/settings.py`
2. Update version in `deploy/Chart.yaml`
3. Update CHANGELOG in README
4. Tag release in git

---

## Summary

The project is now organized into clear, functional areas:

- ✅ **Clean structure** - Everything in its place
- ✅ **Easy to navigate** - Logical organization
- ✅ **Well documented** - Docs in `docs/`
- ✅ **Production ready** - Complete deployment configs
- ✅ **Maintainable** - Clear separation of concerns
- ✅ **Scalable** - Easy to extend

This structure supports both development and deployment workflows efficiently.
