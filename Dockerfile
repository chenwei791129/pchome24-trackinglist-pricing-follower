# Use official Python 3.13 slim image as base
FROM python:3.13-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock* ./

# Install dependencies (production only, no dev dependencies)
RUN uv sync --no-dev --frozen

# Copy source code
COPY src/ ./src/

# Production image
FROM python:3.13-slim

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
