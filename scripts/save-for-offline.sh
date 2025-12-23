#!/bin/bash
# Save image for offline/disconnected deployment (Podman/Docker compatible)
# Usage: ./save-for-offline.sh [version]

set -e

# Configuration
DOCKER_REGISTRY="docker.io/roi12345"
IMAGE_NAME="mce-cluster-generator"
VERSION="${1:-2.0.0}"
OUTPUT_DIR="./offline-deployment"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Detect container runtime (podman preferred, fallback to docker)
if command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
elif command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
else
    echo "❌ Error: Neither podman nor docker found"
    exit 1
fi

# Image names
IMAGE_TAG="${DOCKER_REGISTRY}/${IMAGE_NAME}:${VERSION}"
TAR_FILE="${OUTPUT_DIR}/${IMAGE_NAME}-${VERSION}-${TIMESTAMP}.tar"
COMPRESSED_FILE="${TAR_FILE}.gz"

echo "=========================================="
echo "Save Image for Disconnected Deployment"
echo "=========================================="
echo "Container Runtime: ${CONTAINER_CMD}"
echo "Image: ${IMAGE_TAG}"
echo "Output: ${COMPRESSED_FILE}"
echo "=========================================="
echo ""

# Create output directory
mkdir -p "${OUTPUT_DIR}"

# Check if image exists locally
if ! ${CONTAINER_CMD} image inspect "${IMAGE_TAG}" > /dev/null 2>&1; then
    echo "⚠️  Image not found locally"
    read -p "Pull from registry? (y/n) " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "⬇️  Pulling ${IMAGE_TAG}..."
        ${CONTAINER_CMD} pull "${IMAGE_TAG}"
    else
        echo "❌ Image not available. Build it first with:"
        echo "   ./build-and-push.sh ${VERSION}"
        exit 1
    fi
fi

# Save image to tar
echo "💾 Saving image to tar file..."
${CONTAINER_CMD} save "${IMAGE_TAG}" -o "${TAR_FILE}"

if [ $? -ne 0 ]; then
    echo "❌ Failed to save image"
    exit 1
fi

echo "✅ Image saved to ${TAR_FILE}"

# Compress the tar file
echo "🗜️  Compressing..."
gzip -f "${TAR_FILE}"

if [ $? -ne 0 ]; then
    echo "❌ Failed to compress"
    exit 1
fi

echo "✅ Compressed to ${COMPRESSED_FILE}"
echo ""

# Show file info
FILE_SIZE=$(du -h "${COMPRESSED_FILE}" | cut -f1)
echo "📦 Package Information:"
echo "   File: ${COMPRESSED_FILE}"
echo "   Size: ${FILE_SIZE}"
echo ""

# Create deployment instructions
INSTRUCTIONS_FILE="${OUTPUT_DIR}/DEPLOYMENT-INSTRUCTIONS.txt"
cat > "${INSTRUCTIONS_FILE}" << EOF
========================================
MCE Cluster Generator - Offline Deployment
========================================

Version: ${VERSION}
Package: ${IMAGE_NAME}-${VERSION}-${TIMESTAMP}.tar.gz
Created: $(date)

DEPLOYMENT INSTRUCTIONS
========================================

1. Transfer Files to Disconnected Environment
   - Copy ${IMAGE_NAME}-${VERSION}-${TIMESTAMP}.tar.gz to target system
   - Copy docker-compose.offline.yml (if using compose)
   - Copy .env.example and configure as .env

2. Load Image
   # Extract and load the image (use 'podman' or 'docker')
   gunzip ${IMAGE_NAME}-${VERSION}-${TIMESTAMP}.tar.gz
   podman load -i ${IMAGE_NAME}-${VERSION}-${TIMESTAMP}.tar
   # OR: docker load -i ${IMAGE_NAME}-${VERSION}-${TIMESTAMP}.tar

   # Verify image loaded
   podman images | grep ${IMAGE_NAME}
   # OR: docker images | grep ${IMAGE_NAME}

3. Run the Container

   Option A: Using Podman/Docker Run
   ----------------------------------
   podman run -d \\
     --name mce-api \\
     -p 8000:8000 \\
     -e LOG_LEVEL=INFO \\
     -e DEFAULT_OCP_VERSION=4.16 \\
     -e PRIVATE_REGISTRY=your-registry.com \\
     ${IMAGE_TAG}
   # OR: Replace 'podman' with 'docker' in the command above

   Option B: Using Docker Compose
   -------------------------------
   # Configure .env file first
   docker-compose -f docker-compose.offline.yml up -d
   # OR: podman-compose -f docker-compose.offline.yml up -d

4. Verify Deployment
   # Check health
   curl http://localhost:8000/health

   # Check logs
   podman logs mce-api
   # OR: docker logs mce-api

   # Access API docs
   http://localhost:8000/docs

5. Configuration
   Environment variables can be set via:
   - Podman/Docker run -e flags
   - docker-compose.yml environment section
   - .env file (with compose)

   Required for disconnected:
   - PRIVATE_REGISTRY: Your internal registry
   - DEFAULT_DNS_DOMAIN: Your DNS domain
   - SUPPORTED_VENDORS: Vendor list
   - DEFAULT_OCP_VERSION: OpenShift version

========================================
TROUBLESHOOTING
========================================

Image won't start:
  podman logs mce-api
  # OR: docker logs mce-api

Check configuration:
  podman exec mce-api env | grep -E 'HOST|PORT|LOG_LEVEL'
  # OR: docker exec mce-api env | grep -E 'HOST|PORT|LOG_LEVEL'

Interactive shell:
  podman exec -it mce-api /bin/bash
  # OR: docker exec -it mce-api /bin/bash

========================================
For support, see README.md
========================================
EOF

echo "📝 Deployment instructions created: ${INSTRUCTIONS_FILE}"
echo ""

# Create offline docker-compose file
COMPOSE_FILE="${OUTPUT_DIR}/docker-compose.offline.yml"
cat > "${COMPOSE_FILE}" << 'EOF'
version: '3.8'

services:
  mce-api:
    image: docker.io/roi12345/mce-cluster-generator:VERSION_PLACEHOLDER
    container_name: mce-api
    ports:
      - "8000:8000"
    environment:
      # Server settings
      - HOST=0.0.0.0
      - PORT=8000
      - DEBUG=false
      - LOG_LEVEL=INFO

      # Cluster defaults (configure for your environment)
      - DEFAULT_OCP_VERSION=4.16
      - DEFAULT_DNS_DOMAIN=example.company.com
      - PRIVATE_REGISTRY=registry.internal.company.com
      - SUPPORTED_VENDORS=cisco,dell,dell-data,h100-gpu,h200-gpu

      # Security
      - CORS_ORIGINS=*

      # Operational
      - MAX_NODES=100

    volumes:
      # Mount logs directory
      - ./logs:/app/logs

    restart: unless-stopped

    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  logs:
EOF

# Replace version placeholder
sed -i "s/VERSION_PLACEHOLDER/${VERSION}/g" "${COMPOSE_FILE}"

echo "🐳 Docker Compose file created: ${COMPOSE_FILE}"
echo ""

# Create checksums
echo "🔐 Creating checksums..."
cd "${OUTPUT_DIR}"
sha256sum "${IMAGE_NAME}-${VERSION}-${TIMESTAMP}.tar.gz" > checksums.txt
sha256sum "DEPLOYMENT-INSTRUCTIONS.txt" >> checksums.txt
sha256sum "docker-compose.offline.yml" >> checksums.txt
cd - > /dev/null

echo "✅ Checksums created: ${OUTPUT_DIR}/checksums.txt"
echo ""

echo "=========================================="
echo "✨ Package Ready for Offline Deployment!"
echo "=========================================="
echo ""
echo "📁 Files created in ${OUTPUT_DIR}:"
echo "   - ${IMAGE_NAME}-${VERSION}-${TIMESTAMP}.tar.gz (${FILE_SIZE})"
echo "   - DEPLOYMENT-INSTRUCTIONS.txt"
echo "   - docker-compose.offline.yml"
echo "   - checksums.txt"
echo ""
echo "📋 Next steps:"
echo "   1. Transfer entire ${OUTPUT_DIR}/ to disconnected environment"
echo "   2. Follow instructions in DEPLOYMENT-INSTRUCTIONS.txt"
echo "   3. Verify checksums before deployment"
echo ""
