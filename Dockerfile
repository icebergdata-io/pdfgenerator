# Use an official Python runtime as a parent image
FROM python:3.11.5-slim

# Expose port 8080 for FastAPI
EXPOSE 8080

# Install system dependencies required for lxml
RUN apt-get update && apt-get install -y \
    libxml2-dev \
    libxslt-dev \
    && apt-get clean \
    poppler-utils \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run the FastAPI application with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
