# Dockerfile for Python Flask Backend on Cloud Run

# Use an official lightweight Python image based on Debian Bookworm to reduce vulnerabilities.
# python:3.12-slim-bookworm is recommended based on vulnerability scan.
FROM python:3.12-slim-bookworm

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1  # Prevents python creating .pyc files
ENV PYTHONUNBUFFERED 1         # Ensures logs print directly to Cloud Run logs

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container first
# This leverages Docker layer caching - dependencies are only reinstalled if requirements.txt changes
COPY requirements.txt .

# Install system dependencies that might be needed by Python libraries.
# PyMuPDF sometimes needs fontconfig or other libraries, but often works without them
# on standard Debian-based images. Add dependencies here if installation fails later.
# Example: RUN apt-get update && apt-get install -y --no-install-recommends fontconfig && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    # Add any system dependencies here if needed for Bookworm
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies specified in requirements.txt
# --no-cache-dir reduces image size
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code from your local 'src' directory into the container's '/app/src' directory
# Make sure your Python files (api.py, vllm_handler.py, config.py, utils.py) are inside a 'src' folder
# in the same directory as this Dockerfile.
COPY src/ /app/src/

# Expose the port the app runs on.
# Cloud Run automatically provides a PORT environment variable (defaulting to 8080).
# Gunicorn will bind to this port.
EXPOSE 8080

# Define the command to run the application using Gunicorn (production WSGI server).
# -w 4: Number of worker processes (adjust based on load/instance size). 2-4 is common.
# --bind 0.0.0.0:8080: Listen on all interfaces on port 8080 (Gunicorn uses $PORT if set).
# src.api:app: Tells Gunicorn to run the 'app' object found in the 'src/api.py' module.
CMD ["gunicorn", "-w", "4", "--bind", "0.0.0.0:8080", "src.api:app"]
