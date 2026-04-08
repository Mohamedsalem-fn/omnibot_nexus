# --- Stage 1: Builder ---
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies required for building some python packages
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Create a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Stage 2: Runner ---
FROM python:3.11-slim

WORKDIR /app

# Create a non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . .

# Create data directory for SQLite
RUN mkdir -p data && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose Flask port
EXPOSE 8080

# Healthcheck
HEALTHCHECK CMD curl -f http://localhost:8080/health || exit 1

# Run the application
CMD ["python", "main.py"]