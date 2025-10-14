# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3-slim

EXPOSE 8080

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install system dependencies for building Python packages and curl for health checks
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libc6-dev \
    pkg-config \
    curl \
    wget \
    tar \
    && rm -rf /var/lib/apt/lists/*

# Note: TA-Lib installation removed due to compatibility issues with ta-lib Python package

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install --upgrade pip && python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app

# Create necessary directories
RUN mkdir -p logs signal_output config models data

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the FastAPI application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
