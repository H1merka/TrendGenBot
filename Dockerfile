# Use an extended base image with minimal Debian system
FROM python:3.11

# Install essential build tools and required system libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libjpeg-dev \
    libxml2-dev \
    libxslt1-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size

# Set working directory inside container
WORKDIR /app

# Copy requirements file and install Python dependencies
COPY app/requirements.txt .

# Upgrade pip and install CPU-only version of PyTorch, then other requirements
RUN pip install --upgrade pip \
 && pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu \
 && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source code into the container
COPY app/ .

# Set environment variable to disable Python output buffering (useful for logging)
ENV PYTHONUNBUFFERED=1

# Define default command to run the app
CMD ["python", "main.py"]
