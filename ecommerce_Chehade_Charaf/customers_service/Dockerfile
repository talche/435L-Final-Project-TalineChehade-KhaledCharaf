
# Use the official Python image
FROM python:3.8-slim

# Set working directory inside the container
WORKDIR /app

# Install necessary system packages for dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libmariadb-dev \
    libmariadb-dev-compat \
    gcc \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file to the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8001
ENV FLASK_ENV=development

# Expose the application port
EXPOSE 8001

# Define the default command to run the application
CMD ["flask", "run"]

