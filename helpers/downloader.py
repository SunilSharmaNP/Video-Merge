# helpers/downloader.py (Fixed imports)

import aiohttp
import os
import time
from config import Config
from helpers.utils import get_readable_file_size, get_progress_bar

# --- Throttling Logic ---
last_edit_time = {}
EDIT_THROTTLE_SECONDS = 4.0

async def smart_progress_editor(status_message, text: str):
    """
    A custom editor that checks if enough time has passed before editing a message.
    This is the core of the FloodWait prevention.
    """
    if not status_message or not hasattr(status_message, 'chat'):
        return
        
    message_key = f"{status_message.chat.id}_{status_message.id}"
    now = time.time()
    last_time = last_edit_time.get(message_key, 0)

    if (now - last_time) > EDIT_THROTTLE_SECONDS:
        try:
            await status_message.edit_text(text)
            last_edit_time[message_key] = now
        except Exception:
            pass

async def download_from_url(url: str, user_id: int, status_message) -> str or None:
    """Downloads a file from a direct URL with smart progress reporting."""
    file_name = url.split('/')[-1] or f"video_{int(time.time())}.mp4"
    user_download_dir = os.path.join(Config.DOWNLOAD_DIR, str(user_id))
    os.makedirs(user_download_dir, exist_ok=True)
    dest_path = os.path.join(user_download_dir, file_name)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as resp:
                if resp.status == 200:
                    total_size = int(resp.headers.get('content-length', 0))
                    downloaded = 0

                    with open(dest_path, 'wb') as f:
                        async for chunk in resp.content.iter_chunked(1024 * 1024):
                            f.write(chunk)
                            downloaded += len(chunk)

                            if total_size > 0:
                                progress = downloaded / total_size
                                progress_text = (
                                    f"📥 **Downloading from URL...**\n"
                                    f"➢ `{file_name}`\n"
                                    f"➢ {get_progress_bar(progress)} `{progress:.1%}`\n"
                                    f"➢ **Size:** `{get_readable_file_size(downloaded)}` / `{get_readable_file_size(total_size)}`"
                                )
                                await smart_progress_editor(status_message, progress_text)

                    await status_message.edit_text(f"✅ **Downloaded:** `{file_name}`\n\nPreparing to merge...")
                    return dest_path
                else:
                    await status_message.edit_text(f"❌ **Download Failed!**\nStatus: {resp.status} for URL: `{url}`")
                    return None
    except Exception as e:
        try:
            await status_message.edit_text(f"❌ **Download Failed!**\nError: `{str(e)}`")
        except Exception:
            pass
        return None

async def download_from_tg(message, user_id: int, status_message) -> str or None:
    """Downloads a file from Telegram with smart progress reporting."""
    user_download_dir = os.path.join(Config.DOWNLOAD_DIR, str(user_id))
    os.makedirs(user_download_dir, exist_ok=True)

    async def progress_func(current, total):
        progress = current / total
        file_name = message.video.file_name if message.video and message.video.file_name else "telegram_video.mp4"

        progress_text = (
            f"📥 **Downloading from Telegram...**\n"
            f"➢ `{file_name}`\n"
            f"➢ {get_progress_bar(progress)} `{progress:.1%}`\n"
            f"➢ **Size:** `{get_readable_file_size(current)}` / `{get_readable_file_size(total)}`"
        )
        await smart_progress_editor(status_message, progress_text)

    try:
        file_path = await message.download(
            file_name=os.path.join(user_download_dir, ''),
            progress=progress_func
        )
        file_name = os.path.basename(file_path)
        await status_message.edit_text(f"✅ **Downloaded:** `{file_name}`\n\nPreparing to merge...")
        return file_path
    except Exception as e:
        try:
            await status_message.edit_text(f"❌ **Download Failed!**\nError: `{str(e)}`")
        except Exception:
            pass
        return None
