FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    python3-pip \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY . /app/

# Create necessary directories
RUN mkdir -p subs tmp

# Set default command
CMD ["python3", "run_all.py"] 