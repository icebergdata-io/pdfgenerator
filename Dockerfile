# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Expose port 8080 for FastAPI
EXPOSE 8080

# Install system dependencies and Poppler
RUN apt-get update && apt-get install -y \
    libxml2-dev \
    libxslt-dev \
    poppler-utils \
    tesseract-ocr \
    libtesseract-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy just the requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set the PATH to include Poppler binaries
ENV PATH="/usr/bin:${PATH}"

# Run the FastAPI application with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]