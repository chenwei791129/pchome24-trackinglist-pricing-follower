# Builder: official Python 3.15 Alpine image with uv preinstalled
FROM ghcr.io/astral-sh/uv:python3.15-alpine AS builder

# Build the venv on the image's own interpreter so its python symlink matches
# the runtime image (same /usr/local/bin/python3.15) instead of a uv download.
ENV UV_PYTHON_DOWNLOADS=never

# Set working directory
WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock* ./

# Install dependencies (production only, no dev dependencies)
RUN uv sync --no-dev --frozen

# Copy source code
COPY src/ ./src/

# Production image
FROM python:3.15-alpine

# Apply pending Alpine package updates not yet in the base image; they are only
# picked up when this layer is rebuilt rather than served from the build cache.
# Also remove pip: the app runs from /app/.venv and never invokes it, while its
# vendored urllib3, msgpack and setuptools' pkg_resources carry known CVEs.
RUN apk upgrade --no-cache \
    && python -m pip uninstall -y pip

WORKDIR /app

# Copy virtual environment and source from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Create directory for database
RUN mkdir -p /app/db

# Run the application
CMD ["python", "src/main.py"]
