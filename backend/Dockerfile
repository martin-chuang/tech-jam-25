# Development Dockerfile for Flask backend with hot reload and venv
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    build-essential \
    cmake \
    make \
    git \
    libomp-dev \
    libgmp-dev \
    libmpfr-dev \
    libmpc-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv

# Make sure we use venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy backend requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies in venv
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Set working directory to backend
WORKDIR /app/backend

# Expose the Flask development server port
EXPOSE 5000

# Set environment variables for development
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1
ENV PYTHONPATH=/app

# Start the Flask development server with hot reload using venv python
CMD ["/opt/venv/bin/python", "app.py"]