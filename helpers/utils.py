import os
import ffmpeg
from typing import Union

SIZE_UNITS = ["B", "KB", "MB", "GB", "TB", "PB"]

def get_readable_file_size(size_in_bytes: int) -> str:
    if size_in_bytes is None or size_in_bytes == 0:
        return "0B"
    index = 0
    while size_in_bytes >= 1024 and index < len(SIZE_UNITS)-1:
        size_in_bytes /= 1024
        index += 1
    return f"{round(size_in_bytes,2)}{SIZE_UNITS[index]}"

def get_progress_bar(progress: float, length: int=20) -> str:
    filled = int(length*progress)
    return "█"*filled + "░"*(length-filled)

def get_time_left(elapsed: float, progress: float) -> str:
    if progress <= 0:
        return "Calculating..."
    total = elapsed / progress

class UserSettings:
    def __init__(self, uid, name):
        self.user_id = uid
        self.name = name
        self.merge_mode = 1
        self.edit_metadata = False
        self.allowed = False
        self.banned = False
        self.thumbnail = None

    def get(self):
        # load from database or defaults
        return {
            "user_id": self.user_id,
            "name": self.name,
            "merge_mode": self.merge_mode,
            "edit_metadata": self.edit_metadata,
            "allowed": self.allowed,
            "banned": self.banned,
            "thumbnail": self.thumbnail,
        }

    def set(self):
        # save to database
        pass

    left = total - elapsed
    if left < 60:
        return f"{int(left)}s"
    if left < 3600:
        m = int(left//60)
        s = int(left%60)
        return f"{m}m{s}s"
    h = int(left//3600)
    m = int((left%3600)//60)
    return f"{h}h{m}m"

async def get_video_properties(path: str) -> Union[dict, None]:
    try:
        probe = ffmpeg.probe(path)
        video = next(s for s in probe["streams"] if s["codec_type"]=="video")
        return {
            "duration": float(probe["format"].get("duration",0)),
            "width": int(video.get("width",0)),
            "height": int(video.get("height",0)),
            "streams": probe["streams"],
            "format": probe["format"],
        }
    except:
        return None

def is_url_safe(url: str, domains: list) -> bool:
    from urllib.parse import urlparse
    netloc = urlparse(url).netloc.lower()
    return any(d in netloc for d in domains)
