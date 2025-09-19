FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .

# Install OpenTelemetry auto-instrumentation packages
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir \
    opentelemetry-distro[otlp]==0.45b0 \
    opentelemetry-instrumentation[fastapi,requests,psutil]==0.45b0

# Copy your existing application code
COPY app/ ./app/

# Install auto-instrumentation
RUN opentelemetry-bootstrap -a install

# Set environment variables for OTEL
ENV OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
ENV OTEL_SERVICE_NAME=fastapi-app
ENV OTEL_SERVICE_VERSION=1.0.0
ENV OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
ENV OTEL_EXPORTER_OTLP_PROTOCOL=grpc
ENV OTEL_RESOURCE_ATTRIBUTES=service.name=fastapi-app,service.version=1.0.0

# Set PYTHONPATH to ensure proper module resolution for relative imports
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Start the application with auto-instrumentation
# Using python -m to run as module to handle relative imports properly
CMD ["opentelemetry-instrument", "python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]