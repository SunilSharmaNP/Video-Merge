import os
from collections import defaultdict
import logging
from logging.handlers import RotatingFileHandler
import time
import sys
import re
from helpers.msg_utils import MakeButtons

"""Enhanced Constants for New Features"""
# Original constants
MERGE_MODE = {}  # Maintain each user merge_mode
UPLOAD_AS_DOC = {}  # Maintain each user ul_type
UPLOAD_TO_DRIVE = {}  # Maintain each user drive_choice
UPLOAD_TO_GOFILE = {}  # NEW: Maintain each user gofile_choice

FINISHED_PROGRESS_STR = os.environ.get("FINISHED_PROGRESS_STR", "â–ˆ")
UN_FINISHED_PROGRESS_STR = os.environ.get("UN_FINISHED_PROGRESS_STR", "â–‘")
EDIT_SLEEP_TIME_OUT = 10
gDict = defaultdict(lambda: [])
queueDB = {}
formatDB = {}
replyDB = {}
urlDB = {}  # NEW: For URL queue management

# Enhanced file extensions
VIDEO_EXTENSIONS = ["mkv", "mp4", "webm", "ts", "wav", "mov", "avi", "flv", "3gp", "m4v"]
AUDIO_EXTENSIONS = ["aac", "ac3", "eac3", "m4a", "mka", "thd", "dts", "mp3", "flac", "ogg"]
SUBTITLE_EXTENSIONS = ["srt", "ass", "mka", "mks", "vtt", "sub", "idx"]

# NEW: URL support constants
URL_REGEX = re.compile(
    r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
)

# Enhanced logging configuration
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
logging.getLogger("aiohttp").setLevel(logging.WARNING)  # NEW

LOGGER = logging.getLogger(__name__)
BROADCAST_MSG = """
**Total: {}
Done: {}**
"""
bMaker = MakeButtons()

# NEW: Progress tracking helpers
last_edit_time = {}
EDIT_THROTTLE_SECONDS = 4.0
