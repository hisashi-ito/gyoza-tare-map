FROM python:3.11-slim

# System dependencies for geopandas, playwright, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy source before installing (editable install requires src/ to exist)
COPY pyproject.toml ./
COPY src/ ./src/

# Install Python dependencies (editable install)
RUN pip install --no-cache-dir -e ".[dev]"

# Install Playwright browsers (optional; needed only for playwright sources)
RUN playwright install chromium --with-deps || true

COPY scripts/ ./scripts/
COPY seeds.yaml ./

# Data directories
RUN mkdir -p data/raw data/extracted data/classified data/geo outputs

CMD ["python", "scripts/run_pipeline.py"]
