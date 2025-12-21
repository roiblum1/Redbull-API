# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MCE Cluster Generator API - A FastAPI-based REST API for generating OpenShift cluster configurations with multi-vendor support. The API generates YAML cluster configuration files following MCE (Multi-Cluster Engine) standards, supporting multiple hardware vendors (Cisco, Dell, NVIDIA GPU nodes) with per-vendor node pools and infrastructure environments.

## Development Commands

### Starting the API Server
```bash
# Activate virtual environment
source .venv/bin/activate

# Start the API server (development mode with auto-reload)
python start.py

# Access points:
# - API: http://localhost:8000
# - Swagger UI: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

### Docker Commands
```bash
# Build the Docker image
docker build -t mce-cluster-generator .

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Dependencies
```bash
# Install dependencies
pip install -r requirements.txt

# Core dependencies: FastAPI, Uvicorn, Pydantic, PyYAML, GitPython, Jinja2
```

## Architecture Overview

### Request Flow
1. **API Layer** ([src/api/routers/clusters.py](src/api/routers/clusters.py)) - Receives HTTP requests, validates vendor configs
2. **Model Layer** ([src/models/input.py](src/models/input.py)) - Pydantic models validate cluster parameters
3. **Generator Layer** ([src/generators/cluster_builder.py](src/generators/cluster_builder.py)) - Builder pattern constructs cluster configs
4. **Defaults Layer** ([src/defaults/defaults_manager.py](src/defaults/defaults_manager.py)) - Provides version-specific defaults and machine configs
5. **Output** - Returns YAML cluster configuration

### Key Design Patterns

**Builder Pattern** ([src/generators/cluster_builder.py](src/generators/cluster_builder.py))
- `ClusterBuilder` - Fluent interface for constructing cluster configs step-by-step
- `ClusterConfigGenerator` - High-level facade that orchestrates the builder
- Separates construction logic from representation

**Multi-Vendor Architecture**
- Each vendor gets its own nodepool with distinct configuration
- Vendor configs include: vendor name, node count, and infrastructure environment name
- Network manager configs are vendor-specific: `nm-conf-{cluster_name}-{vendor}`
- mcFiles list aggregates configs from all vendors to avoid duplication

**Version-Specific Defaults** ([src/defaults/defaults_manager.py](src/defaults/defaults_manager.py))
- Image content sources are loaded from YAML files per OCP version ([src/defaults/image_content_sources/](src/defaults/image_content_sources/))
- Supports OpenShift 4.15 and 4.16 (stored in `SUPPORTED_VERSIONS`)
- Uses `@lru_cache` for performance when loading version files

**Pod Density Configuration**
- Supports 250 pods/node (default) or 500 pods/node (high-density)
- `max_pods=500` automatically includes `98-var-lib-containers` config (enforced in validation)
- Different kubeletconfig used: `worker-kubeletconfig` (250) vs `worker-kubeletconfig-500` (500)

## Important Implementation Details

### Machine Config Building Logic

The config list for each nodepool and the mcFiles list follow this structure:

**Per-Nodepool Configs** (in `config` field):
1. `nm-conf-{cluster_name}-{vendor}` - Vendor-specific network manager config
2. `workers-chrony-configuration` - Always included
3. `worker-kubeletconfig` or `worker-kubeletconfig-500` - Based on max_pods
4. `98-var-lib-containers` - Optional (250 pods) or required (500 pods)
5. `ringsize` - Optional network tuning
6. Custom configs - User-provided additional configs

**mcFiles List** (cluster-level, aggregates all vendors):
- Contains nm-conf entries for ALL vendors
- Contains shared configs only once (no duplication)
- Built by `build_mc_files_list()` in defaults_manager

### Validation Chain

1. **API Request Models** ([src/api/models/requests.py](src/api/models/requests.py)) - FastAPI validation
2. **Input Models** ([src/models/input.py](src/models/input.py)) - Pydantic validation with:
   - Vendor validation against `SUPPORTED_VENDORS`
   - Cluster name: lowercase, DNS-compliant, 1-63 chars
   - `max_pods=500` forces `include_var_lib_containers=True` via `@model_validator`
3. **API Router** ([src/api/routers/clusters.py](src/api/routers/clusters.py)) - Additional vendor checks against defaults manager

### Configuration System

**Settings** ([src/config.py](src/config.py)):
- Singleton `Settings` class loads from environment variables
- Key settings: `HOST`, `PORT`, `DEBUG`, `LOG_LEVEL`, `PRIVATE_REGISTRY`, `DEFAULT_OCP_VERSION`, `DEFAULT_DNS_DOMAIN`
- `SUPPORTED_VENDORS` and `SUPPORTED_VERSIONS` can be overridden via env vars (comma-separated)
- CORS origins configurable via `CORS_ORIGINS` env var

**Defaults Manager** ([src/defaults/defaults_manager.py](src/defaults/defaults_manager.py)):
- Centralized source of truth for supported vendors, versions, and configs
- Loads image content sources from YAML files based on OCP version
- Provides methods to build config lists with proper ordering and dependencies

### API Endpoints

- `GET /health` - Health check
- `GET /api/v1/clusters/defaults` - Get all defaults (vendors, versions, configs)
- `GET /api/v1/clusters/vendors` - List available vendors with display names
- `GET /api/v1/clusters/versions` - List supported OpenShift versions
- `POST /api/v1/clusters/generate` - Generate cluster YAML (returns YAML content)
- `POST /api/v1/clusters/preview` - Preview cluster YAML (identical to generate but clearer intent)

### Error Handling

- Custom `MCEGeneratorError` exception ([src/utils/exceptions.py](src/utils/exceptions.py))
- Exception handler in [src/main.py](src/main.py) converts to 400 responses
- Comprehensive logging via `logging_config.py` with Rich console output

## Common Modifications

### Adding a New Vendor
1. Add vendor to `SUPPORTED_VENDORS` in [src/defaults/defaults_manager.py](src/defaults/defaults_manager.py)
2. Add display name to `VENDOR_DISPLAY_NAMES` in [src/api/routers/clusters.py](src/api/routers/clusters.py)
3. Update validator in [src/models/input.py](src/models/input.py) `VendorConfig.validate_vendor()`

### Adding a New OpenShift Version
1. Create new YAML file in [src/defaults/image_content_sources/](src/defaults/image_content_sources/) (e.g., `4.17.yaml`)
2. Add version to `SUPPORTED_VERSIONS` in [src/defaults/defaults_manager.py](src/defaults/defaults_manager.py)
3. Update `Literal` type in [src/models/input.py](src/models/input.py) `ClusterGenerationInput.ocp_version`

### Adding Optional Configs
1. Add config key and name to `OPTIONAL_CONFIGS` dict in [src/defaults/defaults_manager.py](src/defaults/defaults_manager.py)
2. Add boolean field to [src/models/input.py](src/models/input.py) `ClusterGenerationInput`
3. Add to `ConfigInfo` list in [src/api/routers/clusters.py](src/api/routers/clusters.py) `get_defaults()`
4. Handle in `build_config_list()` and `build_mc_files_list()` methods

## Testing the API

```bash
# List available vendors
curl http://localhost:8000/api/v1/clusters/vendors

# Get all defaults
curl http://localhost:8000/api/v1/clusters/defaults

# Generate cluster config
curl -X POST http://localhost:8000/api/v1/clusters/generate \
  -H "Content-Type: application/json" \
  -d '{
    "cluster_name": "test-cluster",
    "site": "datacenter-1",
    "vendor_configs": [
      {"vendor": "dell", "number_of_nodes": 3, "infra_env_name": "dell-prod"},
      {"vendor": "cisco", "number_of_nodes": 2, "infra_env_name": "cisco-prod"}
    ],
    "ocp_version": "4.16",
    "max_pods": 250
  }'
```

## Project Structure Notes

- **No GitOps Integration Active**: README mentions GitOps features, but current codebase focuses on YAML generation only
- **Static UI Files**: [src/static/](src/static/) directory for UI, but fallback HTML served if missing
- **Sites Directory**: [sites/](sites/) contains example/test cluster configurations
- **No Tests**: No test suite present in the repository
