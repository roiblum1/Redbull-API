# Quick Start Guide - MCE Cluster Generator API

## Build & Push (Connected Environment)

```bash
# Build and optionally push to docker.io/roi12345
./build-and-push.sh 2.0.0

# The script will:
# 1. Auto-detect podman/docker
# 2. Build the image
# 3. Ask if you want to push to registry
```

---

## Create Offline Package (For Disconnected Networks)

```bash
# Create offline deployment package
./save-for-offline.sh 2.0.0

# Output: offline-deployment/ directory with:
# - mce-cluster-generator-VERSION-TIMESTAMP.tar.gz (106 MB)
# - DEPLOYMENT-INSTRUCTIONS.txt
# - docker-compose.offline.yml
# - checksums.txt
```

---

## Run Locally (Quick Test)

```bash
# Using Podman
podman run -d --name mce-api -p 8000:8000 docker.io/roi12345/mce-cluster-generator:2.0.0

# Using Docker
docker run -d --name mce-api -p 8000:8000 docker.io/roi12345/mce-cluster-generator:2.0.0

# Test it
curl http://localhost:8000/health

# View logs
podman logs mce-api

# Stop and remove
podman stop mce-api && podman rm mce-api
```

---

## Deploy in Disconnected Environment

```bash
# 1. Transfer offline-deployment/ directory to disconnected system

# 2. Extract and load image
cd offline-deployment/
gunzip mce-cluster-generator-2.0.0-*.tar.gz
podman load -i mce-cluster-generator-2.0.0-*.tar

# 3. Run container
podman run -d \
  --name mce-api \
  -p 8000:8000 \
  -e PRIVATE_REGISTRY=your-registry.com \
  -e DEFAULT_DNS_DOMAIN=your-domain.com \
  docker.io/roi12345/mce-cluster-generator:2.0.0

# 4. Verify
curl http://localhost:8000/health
```

---

## Useful Commands

```bash
# List images
podman images | grep mce-cluster-generator

# Check running containers
podman ps | grep mce-api

# View logs
podman logs -f mce-api

# Interactive shell
podman exec -it mce-api /bin/bash

# Check health
curl http://localhost:8000/health

# API Documentation
# Browser: http://localhost:8000/docs
```

---

## Configuration

Edit environment variables:

**Using podman/docker run:**
```bash
podman run -d \
  --name mce-api \
  -p 8000:8000 \
  -e LOG_LEVEL=DEBUG \
  -e DEFAULT_OCP_VERSION=4.16 \
  -e PRIVATE_REGISTRY=registry.example.com \
  -e DEFAULT_DNS_DOMAIN=company.com \
  docker.io/roi12345/mce-cluster-generator:2.0.0
```

**Using docker-compose:**
```bash
# Edit docker-compose.offline.yml
# Then:
docker-compose -f docker-compose.offline.yml up -d
```

---

## See Also

- [DOCKER_DEPLOYMENT_COMPLETE.md](DOCKER_DEPLOYMENT_COMPLETE.md) - Complete deployment documentation
- [offline-deployment/DEPLOYMENT-INSTRUCTIONS.txt](offline-deployment/DEPLOYMENT-INSTRUCTIONS.txt) - Offline deployment guide
- [LOGGING_QUICK_WINS_COMPLETED.md](LOGGING_QUICK_WINS_COMPLETED.md) - Logging improvements
- [CLAUDE.md](CLAUDE.md) - Project documentation
