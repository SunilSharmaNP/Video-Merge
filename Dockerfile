# Enhanced Dockerfile for VPS deployment

FROM ubuntu:24.04

# Set working directory
WORKDIR /usr/src/mergebot
RUN chmod 777 /usr/src/mergebot

# Update system and install dependencies
RUN apt-get -y update \
    && apt-get -y upgrade \
    && apt-get install apt-utils -y \
    && apt-get install -y \
        python3-full \
        python3-pip \
        python3-venv \
        git \
        wget \
        curl \
        pv \
        jq \
        ffmpeg \
        mediainfo \
        neofetch \
        htop \
        nano \
        unzip \
        ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install rclone for drive uploads
RUN curl https://rclone.org/install.sh | bash

# Create Python virtual environment
RUN python3 -m venv venv && chmod +x venv/bin/python

# Copy requirements first for better Docker layer caching
COPY requirements.txt .
RUN venv/bin/python -m pip install --no-cache-dir --upgrade pip \
    && venv/bin/python -m pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p downloads userdata logs \
    && chmod -R 755 downloads userdata logs

# Make scripts executable
RUN chmod +x start.sh

# Set environment variables
ENV PYTHONPATH="/usr/src/mergebot:${PYTHONPATH}"
ENV PATH="/usr/src/mergebot/venv/bin:${PATH}"

# Expose ports (if using webhooks)
EXPOSE 8080 8443

# Health check to ensure the bot is running
HEALTHCHECK --interval=60s --timeout=10s --start-period=20s --retries=3 \
    CMD pgrep -f "python.*bot.py" > /dev/null || exit 1

# Create a non-root user for security
RUN groupadd -r botuser && useradd -r -g botuser botuser \
    && chown -R botuser:botuser /usr/src/mergebot

# Switch to non-root user
USER botuser

# Start the application
CMD ["bash", "start.sh"]

# Labels for better maintainability
LABEL maintainer="your-email@example.com"
LABEL version="2.0"
LABEL description="Enhanced Telegram Video Merge Bot with URL download and GoFile upload support"
LABEL source="https://github.com/your-username/enhanced-merge-bot"
