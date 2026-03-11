# --- Stage 1: Build Frontend ---
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend

# Install dependencies (utilize caching)
COPY frontend/package*.json ./
RUN npm ci

# Copy frontend source and build
COPY frontend/ ./
RUN npm run build

# --- Stage 2: Final Application ---
FROM python:3.11-slim
WORKDIR /app

# Install ONLY essential system dependencies
# build-essential is often needed for pmdarima and bcrypt if wheels aren't available
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Copy built frontend from Stage 1
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Expose ports
EXPOSE 8000 8501

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    API_HOST=0.0.0.0 \
    API_PORT=8000

# Default command
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
