# Enhanced __init__.py integrated with original

import os
from collections import defaultdict
import logging
from logging.handlers import RotatingFileHandler
import time
import sys
import re
from helpers.msg_utils import MakeButtons

"""Enhanced Constants for New Features"""
# Original constants from repository
MERGE_MODE = {}  # Maintain each user merge_mode
UPLOAD_AS_DOC = {}  # Maintain each user ul_type
UPLOAD_TO_DRIVE = {}  # Maintain each user drive_choice

# NEW: Enhanced constants for your features
UPLOAD_TO_GOFILE = {}  # NEW: Maintain each user gofile_choice
urlDB = {}  # NEW: For URL queue management

FINISHED_PROGRESS_STR = os.environ.get("FINISHED_PROGRESS_STR", "█")
UN_FINISHED_PROGRESS_STR = os.environ.get("UN_FINISHED_PROGRESS_STR", "░")
EDIT_SLEEP_TIME_OUT = 10
gDict = defaultdict(lambda: [])
queueDB = {}
formatDB = {}
replyDB = {}

# Enhanced file extensions from original
VIDEO_EXTENSIONS = ["mkv", "mp4", "webm", "ts", "wav", "mov", "avi", "flv", "3gp", "m4v"]
AUDIO_EXTENSIONS = ["aac", "ac3", "eac3", "m4a", "mka", "thd", "dts", "mp3", "flac", "ogg"]
SUBTITLE_EXTENSIONS = ["srt", "ass", "mka", "mks", "vtt", "sub", "idx"]

# NEW: URL support constants for your features
URL_REGEX = re.compile(
    r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
)

# Original logging configuration
w = open("mergebotlog.txt", "w")
w.truncate(0)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler("mergebotlog.txt", maxBytes=50000000, backupCount=10),
        logging.StreamHandler(sys.stdout),  # to get sys messages
    ],
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)
# NEW: Enhanced logging
logging.getLogger("aiohttp").setLevel(logging.WARNING)

LOGGER = logging.getLogger(__name__)

# Original broadcast message
BROADCAST_MSG = """
**Total: {}
Done: {}**
"""

# Original button maker
bMaker = MakeButtons()

# NEW: Progress tracking helpers for your features
last_edit_time = {}
EDIT_THROTTLE_SECONDS = 4.0
