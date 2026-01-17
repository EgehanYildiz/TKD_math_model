# Use official Python runtime as a parent image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code and artifacts
COPY . .

# Expose port (Railway passes PORT env var, but good to document)
EXPOSE 5000

# Run gunicorn
# dynamic port from shell env is handled by gunicorn binding if we use cmd properly or relying on railway's default
CMD gunicorn --bind 0.0.0.0:$PORT app:app
