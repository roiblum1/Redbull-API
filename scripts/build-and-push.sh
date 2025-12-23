#!/bin/bash
# Build and push MCE Cluster Generator image (Podman/Docker compatible)
# Usage: ./build-and-push.sh [version]

set -e

# Configuration
DOCKER_REGISTRY="docker.io/roi12345"
IMAGE_NAME="mce-cluster-generator"
VERSION="${1:-2.0.0}"
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# Detect container runtime (podman preferred, fallback to docker)
if command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
elif command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
else
    echo "❌ Error: Neither podman nor docker found"
    exit 1
fi

# Full image names
IMAGE_TAG="${DOCKER_REGISTRY}/${IMAGE_NAME}:${VERSION}"
IMAGE_LATEST="${DOCKER_REGISTRY}/${IMAGE_NAME}:latest"

echo "======================================"
echo "MCE Cluster Generator - Build & Push"
echo "======================================"
echo "Container Runtime: ${CONTAINER_CMD}"
echo "Image: ${IMAGE_TAG}"
echo "Latest: ${IMAGE_LATEST}"
echo "Build Date: ${BUILD_DATE}"
echo "Git Commit: ${GIT_COMMIT}"
echo "======================================"
echo ""

# Check if container runtime is accessible
if ! ${CONTAINER_CMD} info > /dev/null 2>&1; then
    echo "❌ Error: ${CONTAINER_CMD} is not running or accessible"
    exit 1
fi

# Build the image
echo "🔨 Building image with ${CONTAINER_CMD}..."
${CONTAINER_CMD} build \
    --build-arg BUILD_DATE="${BUILD_DATE}" \
    --build-arg GIT_COMMIT="${GIT_COMMIT}" \
    --build-arg VERSION="${VERSION}" \
    -t "${IMAGE_TAG}" \
    -t "${IMAGE_LATEST}" \
    .

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "✅ Build successful!"
echo ""

# Show image info
echo "📦 Image Information:"
${CONTAINER_CMD} images | grep "${IMAGE_NAME}" | head -2
echo ""

# Ask for push confirmation
read -p "🚀 Push to registry ${DOCKER_REGISTRY}? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔐 Logging in to registry..."
    ${CONTAINER_CMD} login docker.io

    echo "⬆️  Pushing ${IMAGE_TAG}..."
    ${CONTAINER_CMD} push "${IMAGE_TAG}"

    echo "⬆️  Pushing ${IMAGE_LATEST}..."
    ${CONTAINER_CMD} push "${IMAGE_LATEST}"

    echo ""
    echo "✅ Push complete!"
    echo ""
    echo "📍 Image available at:"
    echo "   ${IMAGE_TAG}"
    echo "   ${IMAGE_LATEST}"
else
    echo "⏭️  Skipping push"
fi

echo ""
echo "======================================"
echo "✨ Done!"
echo "======================================"
echo ""
echo "To run the image:"
echo "  ${CONTAINER_CMD} run -p 8000:8000 ${IMAGE_TAG}"
echo ""
echo "To test:"
echo "  curl http://localhost:8000/health"
echo ""
