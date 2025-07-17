# 1. Base Image: Naya aur supported version
FROM python:3.9-slim-bullseye

# apt-get ko non-interactive mode me chalane ke liye
ENV DEBIAN_FRONTEND=noninteractive

# 2. Kaam karne ke liye directory set karein
WORKDIR /usr/src/mergebot

# 3. Zaroori system packages install karein
# Bullseye me 'p7zip-rar' nahi hai. Uski jagah 'unrar' istemal karenge.
# 'unrar' "non-free" repository me hota hai, isliye sources.list me 'contrib' aur 'non-free' add karna hoga.
RUN sed -i 's/ main/ main contrib non-free/g' /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    git \
    p7zip-full \
    unrar \
    xz-utils \
    wget \
    curl \
    pv \
    jq \
    ffmpeg \
    unzip \
    mediainfo \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 4. Rclone (Commented hai, agar zaroorat ho to uncomment karein)
# RUN curl https://rclone.org/install.sh | bash

# 5. Python dependencies install karein
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Bot ka saara source code copy karein
COPY . .

# 7. Start script ko executable banayein
RUN chmod +x start.sh

# 8. Container start hone par yeh command chalayein
CMD ["bash", "start.sh"]
