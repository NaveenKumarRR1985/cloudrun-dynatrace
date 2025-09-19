# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir \
    opentelemetry-distro[otlp]==0.45b0 \
    opentelemetry-instrumentation[fastapi,requests,psutil]==0.45b0

# Copy application code
COPY . .

# Create directories for logs and database
RUN mkdir -p /app/logs /app/data

# Install auto-instrumentation
RUN opentelemetry-bootstrap -a install

# Set environment variables for OTEL
ENV OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
ENV OTEL_SERVICE_NAME=aiml-app
ENV OTEL_SERVICE_VERSION=1.0.0
ENV OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
ENV OTEL_EXPORTER_OTLP_PROTOCOL=grpc
ENV OTEL_RESOURCE_ATTRIBUTES=service.name=aiml-app,service.version=1.0.0

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run the application
CMD ["opentelemetry-instrument", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]