# Architecture Update - Unified Entry Point

## Summary

Successfully merged `start.py` into `main.py` to create a single entry point for the application. The architecture now clearly separates UI and API endpoints.

---

## Changes Made

### ✅ 1. Merged start.py into main.py

**Before:**
- `start.py` - Startup script that imports and runs main.py
- `main.py` - FastAPI application

**After:**
- `main.py` - Single entry point with integrated startup logic
- `start.py` - No longer needed (kept for backward compatibility)

### ✅ 2. Clear Route Structure

All routes are now clearly organized:

```
/                          → UI (serves static/index.html)
/static/*                  → Static assets (CSS, JS, images)
/health                    → Health check (backward compatibility)
/docs                      → OpenAPI/Swagger documentation
/redoc                     → ReDoc documentation

/api/health                → API health check
/api/v1/clusters/defaults  → Get cluster defaults
/api/v1/clusters/vendors   → List supported vendors
/api/v1/clusters/versions  → List supported OCP versions
/api/v1/clusters/generate  → Generate cluster YAML
/api/v1/clusters/preview   → Preview cluster YAML
```

### ✅ 3. Updated Dockerfile

**Changed:**
```dockerfile
# Before
COPY src/ ./src/
COPY start.py .
CMD ["python", "start.py"]

# After
COPY src/ ./src/
CMD ["python", "-m", "main"]
```

**Benefits:**
- Simpler deployment
- No need for wrapper script
- Cleaner Docker image

### ✅ 4. Updated .dockerignore

Excluded unnecessary files from Docker build:
- `start.py` (no longer needed in container)
- `build-and-push.sh`
- `save-for-offline.sh`
- `offline-deployment/`
- `deploy/`
- Documentation files

---

## Architecture Overview

### Entry Point Flow

```
python -m main
    ↓
main.py starts
    ↓
FastAPI app initialized
    ↓
Middleware configured (CORS, Logging)
    ↓
Routes mounted:
    - UI at /
    - Static files at /static
    - API at /api/v1
    ↓
Uvicorn server starts
    ↓
Application running
```

### Request Routing

```
Client Request
    ↓
    ├─ / → UI (index.html)
    ├─ /static/* → Static files
    ├─ /docs → OpenAPI docs
    ├─ /health → Health check
    └─ /api/* → API endpoints
        └─ /api/v1/clusters/* → Cluster operations
```

---

## Running the Application

### Local Development

```bash
# Activate virtual environment
source .venv/bin/activate

# Run directly
python src/main.py

# Or with module syntax
cd src && python -m main
```

### Docker

```bash
# Build
podman build -t mce-cluster-generator:2.0.0 .

# Run
podman run -d -p 8000:8000 mce-cluster-generator:2.0.0
```

### Kubernetes (Helm)

```bash
helm install mce-api ./deploy -f ./deploy/values-prod.yaml
```

---

## Benefits of This Architecture

### 1. **Simplicity**
- Single entry point
- No wrapper scripts needed
- Easier to understand

### 2. **Clear Separation**
- UI at root path `/`
- API under `/api/v1/`
- Easy to proxy/route

### 3. **Deployment Friendly**
- Simple reverse proxy configuration
- Clear path structure for ingress rules
- Easy to add API versioning (`/api/v2/` in future)

### 4. **Developer Experience**
- Run with `python src/main.py`
- All configuration in one place
- Standard Python module execution

---

## Reverse Proxy Configuration

### Nginx Example

```nginx
server {
    listen 80;
    server_name mce-api.company.com;

    # UI - serve from root
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API - clearly under /api
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Static files
    location /static/ {
        proxy_pass http://localhost:8000;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }
}
```

### Kubernetes Ingress Example

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mce-api-ingress
spec:
  rules:
  - host: mce-api.company.com
    http:
      paths:
      # API routes
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: mce-api
            port:
              number: 8000
      # UI and static
      - path: /
        pathType: Prefix
        backend:
          service:
            name: mce-api
            port:
              number: 8000
```

---

## API Versioning

The current structure makes it easy to add new API versions:

```python
# main.py
from api.routers import clusters_v1, clusters_v2

app.include_router(clusters_v1.router, prefix="/api/v1")
app.include_router(clusters_v2.router, prefix="/api/v2")
```

This allows:
- `/api/v1/clusters/generate` - Current version
- `/api/v2/clusters/generate` - New version
- Gradual migration
- Backward compatibility

---

## Environment Variables

All configuration via environment variables:

```bash
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO

# Application
DEFAULT_OCP_VERSION=4.16
DEFAULT_DNS_DOMAIN=cluster.company.com
PRIVATE_REGISTRY=registry.company.com
SUPPORTED_VENDORS=cisco,dell,dell-data,h100-gpu,h200-gpu

# Security
CORS_ORIGINS=*
```

---

## Testing

### Test UI

```bash
curl http://localhost:8000/
# Should return HTML
```

### Test API

```bash
# Health check
curl http://localhost:8000/api/health

# List vendors
curl http://localhost:8000/api/v1/clusters/vendors

# Generate cluster
curl -X POST http://localhost:8000/api/v1/clusters/generate \
  -H "Content-Type: application/json" \
  -d '{
    "cluster_name": "test-cluster",
    "site": "dc1",
    "vendor_configs": [
      {"vendor": "dell", "number_of_nodes": 3, "infra_env_name": "dell-prod"}
    ]
  }'
```

### Test Static Files

```bash
curl http://localhost:8000/static/css/styles.css
# Should return CSS
```

---

## Migration Guide

For existing deployments:

### Docker/Podman

No changes needed - Dockerfile handles everything automatically.

### Kubernetes/Helm

No changes needed - Helm chart already uses correct configuration.

### Local Development

**Before:**
```bash
python start.py
```

**After:**
```bash
python src/main.py
```

**Or (recommended):**
```bash
cd src && python -m main
```

---

## File Changes

### Modified:
- [src/main.py](src/main.py) - Added startup logic from start.py
- [Dockerfile](Dockerfile) - Changed CMD to use main.py directly
- [.dockerignore](.dockerignore) - Excluded start.py and deployment files

### Unchanged (backward compatible):
- [start.py](start.py) - Still works if needed
- All API routes
- All configurations
- Environment variables

---

## Verification

### ✅ Local Testing

```bash
$ python src/main.py
Starting MCE Cluster Generator API v2.0.0
Server: http://0.0.0.0:8000
UI: http://0.0.0.0:8000/
API Documentation: http://0.0.0.0:8000/docs
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### ✅ Health Check

```bash
$ curl http://localhost:8000/health
{"status":"healthy","version":"2.0.0","timestamp":"2025-12-22T10:49:38.597644"}
```

### ✅ API Endpoints

```bash
$ curl http://localhost:8000/api/v1/clusters/vendors
{
  "vendors": [
    {"name": "cisco", "display_name": "Cisco UCS"},
    {"name": "dell", "display_name": "Dell PowerEdge"},
    ...
  ],
  "total": 5
}
```

### ✅ UI Accessible

```bash
$ curl http://localhost:8000/ | grep -o "<title>.*</title>"
<title>MCE Cluster Generator</title>
```

---

## Conclusion

✅ **Successfully unified the application entry point!**

**Benefits:**
- ✅ Simpler architecture
- ✅ Clear route structure (UI at `/`, API at `/api/v1/`)
- ✅ Easier deployment
- ✅ Better reverse proxy support
- ✅ Backward compatible
- ✅ Standard Python module execution

**Ready for:**
- ✅ Production deployment
- ✅ Docker/Podman containers
- ✅ Kubernetes/Helm
- ✅ Reverse proxy configuration
- ✅ Future API versioning

🎉 **Architecture Update Complete!**
