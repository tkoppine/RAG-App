# =============================================================================
# ArXiv Research Assistant - Production Docker Image
# =============================================================================

# Use Python 3.10 with CUDA support for optimal performance
FROM pytorch/pytorch:1.13.1-cpu AS base

# Set metadata
LABEL maintainer="ArXiv Research Assistant Team"
LABEL description="AI-Powered Retrieval-Augmented Generation System for Academic Papers"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # OpenGL and graphics libraries
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    # Build tools
    build-essential \
    curl \
    wget \
    git \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# =============================================================================
# Dependencies Installation
# =============================================================================

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# =============================================================================
# Application Setup
# =============================================================================

# Copy application code
COPY . .

# Create required directories
RUN mkdir -p \
    data \
    logs \
    media \
    static

# Set proper permissions
RUN chmod +x scripts/*.sh 2>/dev/null || true

# =============================================================================
# Django Setup
# =============================================================================

# Change to Django project directory
WORKDIR /app/llm-integration/llmproject

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Go back to app root
WORKDIR /app

# =============================================================================
# Health Check
# =============================================================================

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# =============================================================================
# Startup Configuration
# =============================================================================

# Expose port
EXPOSE 8000

# Set default command
CMD ["sh", "-c", "cd llm-integration/llmproject && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]

# =============================================================================
# Development Override (Multi-stage build)
# =============================================================================

FROM base AS development

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-django \
    black \
    flake8 \
    ipython \
    jupyter

# Set development environment
ENV DJANGO_DEBUG=True
ENV DEV_MODE=True

CMD ["sh", "-c", "cd llm-integration/llmproject && python manage.py migrate && python manage.py runserver 0.0.0.0:8000 --settings=llmproject.settings"]
