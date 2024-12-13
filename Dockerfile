FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Add backend to Python path
ENV PYTHONPATH="${PYTHONPATH}:/app/backend"

# Install system dependencies with retry logic
RUN for i in {1..3}; do \
    apt-get update -y && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        && rm -rf /var/lib/apt/lists/* && break \
    || { echo "Retrying apt-get install..."; sleep 1; }; \
    done

# Copy requirements first for better caching
COPY pyproject.toml .

# Install Python dependencies
RUN pip install -e .

# Copy the rest of the application
COPY backend/ backend/
COPY .env .

# Use a shell as default command instead of running tests
CMD ["bash"]