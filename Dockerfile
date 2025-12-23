# Multi-stage build for optimal image size
# Stage 1: Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /build/wheels -r requirements.txt

# Stage 2: Runtime stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    HOST=0.0.0.0 \
    PORT=8000 \
    LOG_LEVEL=INFO

# Set work directory
WORKDIR /app

# Install runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    openssh-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security (UID 1000 to match Helm chart)
RUN groupadd -g 1000 mceapi && useradd -u 1000 -g mceapi -m -s /bin/bash mceapi

# Copy pre-built wheels from builder stage
COPY --from=builder /build/wheels /wheels
COPY requirements.txt .

# Install Python dependencies from wheels (faster, no compilation needed)
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

# Copy application code
COPY src/ ./src/

# Create necessary directories
RUN mkdir -p /app/gitops-repos /app/.ssh /app/logs && \
    chown -R mceapi:mceapi /app

# Create volume mount points
VOLUME ["/app/gitops-repos", "/app/.ssh", "/app/logs"]

# Switch to non-root user
USER mceapi

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set labels for metadata
LABEL maintainer="roi" \
      version="2.0.0" \
      description="MCE Cluster Generator API - Production Ready" \
      org.opencontainers.image.source="https://github.com/roi/mce-cluster-generator" \
      org.opencontainers.image.vendor="MCE Team"

# Run the application directly from main.py
CMD ["python", "-m", "main"]
