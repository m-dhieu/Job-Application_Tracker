# Use the official slim Python image
FROM python:3.10-slim

# Set working directory inside container 
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY ./backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./backend/app ./app

# Copy static files
COPY ./frontend ./static/frontend
COPY ./index.html ./index.html

# Expose container port (configurable via environment variable; default 8080)
ENV PORT=8080
EXPOSE $PORT

# Run the FastAPI app with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
