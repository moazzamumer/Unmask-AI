# Use an official Python image
FROM python:3.11-slim

# Install required system dependencies for WeasyPrint
RUN apt-get update && apt-get install -y \
    build-essential \
    libpango-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libcairo2 \
    libffi-dev \
    libgobject-2.0-0 \
    curl \
    git \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy your project files
COPY . /app

# Install pip dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Set FastAPI as the default command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
