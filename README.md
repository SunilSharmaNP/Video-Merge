# ðŸš€ Enhanced MERGE-BOT

<div align="center">

![Enhanced Merge Bot](https://img.shields.io/badge/Enhanced-Merge%20Bot-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?style=for-the-badge&logo=telegram)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge&logo=docker)

**A powerful Telegram bot for merging videos, audios, and subtitles with enhanced features**

[Features](#-features) â€¢ [Installation](#-installation) â€¢ [Configuration](#-configuration) â€¢ [Usage](#-usage) â€¢ [Docker](#-docker-deployment) â€¢ [Contributing](#-contributing)

</div>

## âœ¨ Features

### ðŸ”¥ **New Enhanced Features**
- **ðŸ”— Direct URL Downloads** - Download videos from direct links
- **ðŸ“ GoFile.io Upload** - Upload merged files to GoFile cloud storage  
- **ðŸš€ Smart Merging** - Dual-mode merging (Fast + Robust fallback)
- **ðŸ“Š Advanced Progress Tracking** - FloodWait prevention with throttled updates
- **ðŸ›¡ï¸ Enhanced Security** - Domain whitelist for safe URL downloads

### ðŸ“¹ **Core Merge Capabilities**
- **Video + Video** - Merge up to 10 videos into single file
- **Video + Audio** - Add multiple audio tracks to video
- **Video + Subtitle** - Embed multiple subtitle files
- **Stream Extraction** - Extract audio/subtitle streams from videos
- **Custom Thumbnails** - Set custom thumbnails for uploads

### ðŸŽ¯ **Upload Destinations**
- **ðŸ“¤ Telegram** - Direct upload to Telegram (up to 4GB with premium)
- **ðŸŒ«ï¸ Google Drive** - Upload using rclone configuration
- **ðŸ“ GoFile.io** - Cloud storage with sharing links

### ðŸ‘‘ **Advanced Features**
- **ðŸ” User Authentication** - Password-based access control
- **ðŸ‘¥ User Management** - Ban/unban users, broadcast messages
- **ðŸ“Š Statistics** - Detailed bot usage statistics
- **ðŸ”„ Auto Updates** - Upstream repository sync capability
- **ðŸ³ Docker Ready** - Easy VPS deployment with Docker

## ðŸ› ï¸ Installation

### Prerequisites
- Python 3.8 or higher
- FFmpeg installed
- MongoDB database
- Telegram Bot Token

### Method 1: Local Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-username/enhanced-merge-bot.git
cd enhanced-merge-bot
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp sample_config.env config.env
# Edit config.env with your values
```

5. **Run the bot**
```bash
python bot.py
```

### Method 2: Docker Installation (Recommended)

```bash
# Clone and build
git clone https://github.com/your-username/enhanced-merge-bot.git
cd enhanced-merge-bot

# Configure environment
cp sample_config.env config.env
# Edit config.env

# Build and run
docker build -t enhanced-merge-bot .
docker run -d --name merge-bot enhanced-merge-bot
```

## âš™ï¸ Configuration

### Required Environment Variables

```env
# Telegram Configuration
API_HASH = "your_api_hash"              # From my.telegram.org
BOT_TOKEN = "your_bot_token"            # From @BotFather
TELEGRAM_API = "your_api_id"            # From my.telegram.org
OWNER = "your_user_id"                  # Your Telegram user ID
OWNER_USERNAME = "your_username"        # Without @
PASSWORD = "user_login_password"        # For user authentication

# Database
DATABASE_URL = "mongodb_connection_string"

# Logging
LOGCHANNEL = "-100xxxxxxxxxx"           # Channel ID with -100 prefix
```

### Optional Enhanced Features

```env
# GoFile.io Integration
GOFILE_TOKEN = "your_gofile_token"      # Optional: Better upload limits

# URL Download Settings
ENABLE_URL_DOWNLOAD = "True"            # Enable URL downloads
MAX_CONCURRENT_DOWNLOADS = "3"          # Simultaneous downloads
DOWNLOAD_TIMEOUT = "300"                # Timeout in seconds
MAX_FILE_SIZE = "4294967296"            # Max file size (4GB)

# Performance Tuning
DOWNLOAD_DIR = "downloads"              # Download directory
```

### Supported URL Domains

The bot supports downloads from these domains by default:
- Google Drive
- Mega.nz  
- MediaFire
- Discord CDN
- GitHub
- Dropbox
- OneDrive
- GoFile.io
- PixelDrain

## ðŸŽ® Usage

### Basic Commands

| Command | Description | Access |
|---------|-------------|---------|
| `/start` | Start the bot | All users |
| `/login <password>` | Login to use bot | All users |
| `/help` | Show help message | Authenticated |
| `/settings` | User settings menu | Authenticated |
| `/stats` | Bot statistics | Owner/Authenticated |

### Admin Commands  

| Command | Description | Access |
|---------|-------------|--------|
| `/ban <user_id>` | Ban a user | Owner only |
| `/unban <user_id>` | Unban a user | Owner only |  
| `/broadcast` | Broadcast message | Owner only |
| `/log` | Get log file | Owner only |

### Merge Modes

1. **Video-Video Mode** - Merge multiple videos
2. **Video-Audio Mode** - Add audio tracks to video
3. **Video-Subtitle Mode** - Add subtitle files to video  
4. **Extract Mode** - Extract streams from video
5. **URL-Merge Mode** - Download from URLs and merge

### How to Use

1. **Authentication**: Send `/login <password>` to access the bot
2. **Set Mode**: Use `/settings` to choose merge mode
3. **Send Files**: Send videos, audios, or subtitles OR send direct URLs
4. **Choose Upload**: Select Telegram, Drive, or GoFile for output
5. **Wait**: Bot will merge and upload automatically

### URL Download Examples

Send any of these message types:
```
https://example.com/video.mp4
https://drive.google.com/file/d/xxx/view
https://mega.nz/file/xxx
```

Multiple URLs in one message:
```
https://example.com/video1.mp4
https://example.com/video2.mp4
https://example.com/video3.mp4
```

## ðŸ³ Docker Deployment

### Using Docker Compose

```yaml
version: '3.8'
services:
  enhanced-merge-bot:
    build: .
    container_name: merge-bot
    restart: unless-stopped
    volumes:
      - ./downloads:/usr/src/mergebot/downloads
      - ./userdata:/usr/src/mergebot/userdata
      - ./logs:/usr/src/mergebot/logs
    env_file:
      - config.env
    depends_on:
      - mongodb

  mongodb:
    image: mongo:latest
    container_name: merge-bot-db
    restart: unless-stopped
    volumes:
      - mongo_data:/data/db

volumes:
  mongo_data:
```

Run with:
```bash
docker-compose up -d
```

### VPS Deployment Commands

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clone and deploy
git clone https://github.com/your-username/enhanced-merge-bot.git
cd enhanced-merge-bot
cp sample_config.env config.env

# Edit config.env with nano/vim
nano config.env

# Build and run
docker build -t enhanced-merge-bot .
docker run -d --name merge-bot --restart unless-stopped enhanced-merge-bot

# View logs
docker logs -f merge-bot
```

## ðŸ“Š Performance & Limits

| Feature | Limit | Notes |
|---------|-------|-------|
| Video Files | 10 per merge | Telegram limit |
| File Size | 4GB | With premium account |
| Concurrent Downloads | 3 | Configurable |
| Download Timeout | 5 minutes | Configurable |
| Upload Destinations | 3 options | Telegram/Drive/GoFile |

## ðŸ”§ Advanced Configuration

### Custom FFmpeg Settings

Modify `helpers/merger.py` for custom encoding:

```python
command = [
    'ffmpeg', '-hide_banner', *input_args, 
    '-filter_complex', filter_complex_str,
    '-c:v', 'libx264',    # Video codec
    '-preset', 'fast',    # Encoding speed
    '-crf', '23',         # Quality (lower = better)
    '-c:a', 'aac',        # Audio codec
    '-b:a', '192k',       # Audio bitrate
    '-y', output_path
]
```

### Adding New Domains

Edit `config.py` to add supported domains:

```python
SUPPORTED_DOMAINS = [
    "your-domain.com",
    "another-domain.com",
    # ... existing domains
]
```

## ðŸ¤ Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## ðŸ“ License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## ðŸ™ Credits

- **Original MERGE-BOT** by [@yashoswalyo](https://github.com/yashoswalyo)
- **Pyrogram** - Modern Telegram MTProto API framework
- **FFmpeg** - Multimedia framework for video processing
- **Contributors** - All who helped improve this bot

## âš ï¸ Disclaimer

This bot is for educational purposes. Users are responsible for complying with copyright laws and terms of service of file hosting platforms.

## ðŸ“ž Support

- **Issues**: [GitHub Issues](https://github.com/your-username/enhanced-merge-bot/issues)
- **Telegram**: [@your_support_group](https://t.me/your_support_group)
- **Email**: your-email@example.com

---

<div align="center">

**â­ Star this repo if you found it helpful!**

Made with â¤ï¸ by [Your Name](https://github.com/your-username)

</div>
