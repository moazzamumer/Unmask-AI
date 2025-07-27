FROM python:3.11-bullseye   # Switch to bullseye for better apt support

# Prevent interactive apt installs
ENV DEBIAN_FRONTEND=noninteractive

# Install required system packages for WeasyPrint
RUN apt-get update --fix-missing && apt-get install -y \
    build-essential \
    libcairo2 \
    libpango-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libgobject-2.0-0 \
    libpangocairo-1.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install Python packages
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Run FastAPI using python main.py
CMD ["python", "main.py"]
