# Enhanced config.py integrated with original

import os

class Config(object):
    # Original configurations from repository
    API_HASH = os.environ.get("API_HASH")
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    TELEGRAM_API = os.environ.get("TELEGRAM_API")
    OWNER = os.environ.get("OWNER")
    OWNER_USERNAME = os.environ.get("OWNER_USERNAME")
    PASSWORD = os.environ.get("PASSWORD")
    DATABASE_URL = os.environ.get("DATABASE_URL")
    LOGCHANNEL = os.environ.get("LOGCHANNEL")  # Add channel id as -100 + Actual ID
    GDRIVE_FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID", "root")
    USER_SESSION_STRING = os.environ.get("USER_SESSION_STRING", None)
    IS_PREMIUM = False
    
    # NEW: Enhanced configurations for your features
    GOFILE_TOKEN = os.environ.get("GOFILE_TOKEN", None)
    ENABLE_URL_DOWNLOAD = os.environ.get("ENABLE_URL_DOWNLOAD", "True").lower() == "true"
    MAX_CONCURRENT_DOWNLOADS = int(os.environ.get("MAX_CONCURRENT_DOWNLOADS", "3"))
    DOWNLOAD_TIMEOUT = int(os.environ.get("DOWNLOAD_TIMEOUT", "300"))
    DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", "downloads")
    MAX_FILE_SIZE = int(os.environ.get("MAX_FILE_SIZE", "4294967296"))  # 4GB default
    
    # NEW: Supported URL domains for security
    SUPPORTED_DOMAINS = [
        "drive.google.com", "mega.nz", "mediafire.com", "zippyshare.com",
        "direct.link", "cdn.discordapp.com", "github.com", "raw.githubusercontent.com",
        "dropbox.com", "onedrive.live.com", "gofile.io", "pixeldrain.com"
    ]
    
    # Enhanced modes including your URL merge mode
    MODES = ["video-video", "video-audio", "video-subtitle", "extract-streams", "url-merge"]
