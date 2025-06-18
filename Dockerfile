# syntax=docker/dockerfile:1

# Multi-stage build for Python FastAPI application
# Based on Docker best practices for Python applications

ARG PYTHON_VERSION=3.11.4
FROM python:${PYTHON_VERSION}-slim AS base

# Prevents Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Create a non-privileged user that the app will run under
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip to latest version to fix warning
RUN python -m pip install --upgrade pip

# Create necessary directories with proper permissions
RUN mkdir -p /app/data /app/logs /app/ssl /app/.cache && \
    chown -R appuser:appuser /app

# Switch to the non-privileged user before installing Python packages
USER appuser

# Set pip cache directory for the appuser
ENV PIP_CACHE_DIR=/app/.cache/pip

# Copy requirements file
COPY --chown=appuser:appuser requirements.txt .

# Download dependencies as a separate step to take advantage of Docker's caching
# Install packages as appuser to avoid permission warnings
RUN python -m pip install --user --no-cache-dir -r requirements.txt

# Add user-installed packages to PATH
ENV PATH="/app/.local/bin:${PATH}"

# Copy the source code into the container
COPY --chown=appuser:appuser . .

# Expose the port that the application listens on
EXPOSE 8001

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run the application
CMD ["python3", "-m", "uvicorn", "src.web_api:app", "--host", "0.0.0.0", "--port", "8001"] 