# Use official Python base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY src/ /app/src/

# Expose port (metadata only)
EXPOSE 8000
EXPOSE 8501

# Command is overridden in deployment configurations
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
