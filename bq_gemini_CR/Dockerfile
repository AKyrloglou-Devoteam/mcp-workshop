# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
# Using --no-cache-dir to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY server.py .

# The PORT environment variable is automatically set by Cloud Run.
# Your application needs to listen on this port.
# Uvicorn will pick this up if $PORT is used in the CMD.
# Default is 8080 if PORT is not set.
ENV PORT 8080

# Expose the port the app runs on
EXPOSE $PORT

# Define the command to run the application using Uvicorn.
# It points to the 'http_app' ASGI application instance in 'server.py'.
# The host must be 0.0.0.0 to be accessible.
CMD ["uvicorn", "server:http_app", "--host", "0.0.0.0", "--port", "$PORT"]