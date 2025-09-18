# Use Python 3.11 slim base image for optimal size and security
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r mceapi && useradd -r -g mceapi mceapi

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY start.py .

# Create directories for GitOps operations and SSH keys
RUN mkdir -p /app/gitops-repos /app/.ssh && \
    chown -R mceapi:mceapi /app

# Create volume mount points
VOLUME ["/app/gitops-repos", "/app/.ssh", "/app/logs"]

# Switch to non-root user
USER mceapi

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["python", "start.py"]