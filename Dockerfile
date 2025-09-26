# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV TAU_BENCH_LOG_DIR=/app/logs
ENV HOST=0.0.0.0
ENV PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY setup.py README.md MANIFEST.in ./
COPY tau_bench/ tau_bench/

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Create logs directory
RUN mkdir -p /app/logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the API server
CMD ["tau-bench-server", "--host", "0.0.0.0", "--port", "8000", "--log-dir", "/app/logs"]