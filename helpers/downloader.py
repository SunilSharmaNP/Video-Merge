# helpers/downloader.py (Enhanced URL and Telegram downloader)

import aiohttp
import os
import time
from config import Config
from helpers.utils import get_human_readable_size, get_progress_bar
from __init__ import LOGGER

# Throttling Logic for FloodWait prevention
last_edit_time = {}
EDIT_THROTTLE_SECONDS = 4.0

async def smart_progress_editor(status_message, text: str):
    """
    A custom editor that checks if enough time has passed before editing a message.
    This is the core of the FloodWait prevention.
    """
    if not status_message or not hasattr(status_message, 'chat'):
        return
        
    # Create a unique key for the message
    message_key = f"{status_message.chat.id}_{status_message.id}"
    now = time.time()
    # Get the last time we edited this message, defaulting to 0 if it's the first time
    last_time = last_edit_time.get(message_key, 0)
    
    # If more than EDIT_THROTTLE_SECONDS have passed, we can edit the message
    if (now - last_time) > EDIT_THROTTLE_SECONDS:
        try:
            await status_message.edit_text(text)
            # IMPORTANT: Update the last edit time for this message
            last_edit_time[message_key] = now
        except Exception:
            # If we still get an error (e.g., message not modified), we just ignore it
            # and try again on the next scheduled update.
            pass

async def download_from_url(url: str, user_id: int, status_message) -> str or None:
    """Downloads a file from a direct URL with smart progress reporting."""
    # Extract filename from URL or generate one
    file_name = url.split('/')[-1] or f"video_{int(time.time())}.mp4"
    
    # Remove query parameters from filename
    if '?' in file_name:
        file_name = file_name.split('?')[0]
    
    # Ensure user download directory exists
    user_download_dir = os.path.join(Config.DOWNLOAD_DIR, str(user_id))
    os.makedirs(user_download_dir, exist_ok=True)
    dest_path = os.path.join(user_download_dir, file_name)

    try:
        # Create timeout configuration
        timeout = aiohttp.ClientTimeout(total=Config.DOWNLOAD_TIMEOUT)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, allow_redirects=True) as resp:
                if resp.status == 200:
                    total_size = int(resp.headers.get('content-length', 0))
                    downloaded = 0
                    
                    # Check file size limit
                    if total_size > Config.MAX_FILE_SIZE:
                        await status_message.edit_text(
                            f"âŒ **File too large!**\n"
                            f"Size: `{get_human_readable_size(total_size)}`\n"
                            f"Max allowed: `{get_human_readable_size(Config.MAX_FILE_SIZE)}`"
                        )
                        return None
                    
                    with open(dest_path, 'wb') as f:
                        async for chunk in resp.content.iter_chunked(1024 * 1024):  # 1MB chunks
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            if total_size > 0:
                                progress = downloaded / total_size
                                # Build the progress message text
                                progress_text = (
                                    f"ðŸ“¥ **Downloading from URL...**\n"
                                    f"âž¢ `{file_name}`\n"
                                    f"âž¢ {get_progress_bar(progress)} `{progress:.1%}`\n"
                                    f"âž¢ **Size:** `{get_human_readable_size(downloaded)}` / `{get_human_readable_size(total_size)}`"
                                )
                                # Call our smart editor instead of editing directly
                                await smart_progress_editor(status_message, progress_text)
                    
                    # Send a final update to show the download is done
                    await status_message.edit_text(f"âœ… **Downloaded:** `{file_name}`\n\nPreparing to merge...")
                    LOGGER.info(f"Successfully downloaded {file_name} from URL for user {user_id}")
                    return dest_path
                else:
                    await status_message.edit_text(f"âŒ **Download Failed!**\nStatus: {resp.status} for URL: `{url}`")
                    LOGGER.error(f"Download failed with status {resp.status} for URL: {url}")
                    return None
                    
    except asyncio.TimeoutError:
        try:
            await status_message.edit_text(f"âŒ **Download Failed!**\nTimeout: Download took longer than {Config.DOWNLOAD_TIMEOUT} seconds")
        except Exception:
            pass
        LOGGER.error(f"Download timeout for URL: {url}")
        return None
    except Exception as e:
        # If the bot is already flood-waited, even sending an error can fail.
        # So we wrap this in a try/except block too.
        try:
            await status_message.edit_text(f"âŒ **Download Failed!**\nError: `{str(e)}`")
        except Exception:
            pass
        LOGGER.error(f"Download error for URL {url}: {str(e)}")
        return None

async def download_from_tg(message, user_id: int, status_message) -> str or None:
    """Downloads a file from Telegram with smart progress reporting."""
    user_download_dir = os.path.join(Config.DOWNLOAD_DIR, str(user_id))
    os.makedirs(user_download_dir, exist_ok=True)

    # We define the progress callback here, which will be called by Pyrogram
    async def progress_func(current, total):
        progress = current / total
        
        # Get proper file name
        file_name = "telegram_file.mp4"  # default
        if message.video and message.video.file_name:
            file_name = message.video.file_name
        elif message.document and message.document.file_name:
            file_name = message.document.file_name
        elif message.audio and message.audio.file_name:
            file_name = message.audio.file_name

        # Build the progress message text
        progress_text = (
            f"ðŸ“¥ **Downloading from Telegram...**\n"
            f"âž¢ `{file_name}`\n"
            f"âž¢ {get_progress_bar(progress)} `{progress:.1%}`\n"
            f"âž¢ **Size:** `{get_human_readable_size(current)}` / `{get_human_readable_size(total)}`"
        )
        # Call our smart editor
        await smart_progress_editor(status_message, progress_text)

    try:
        # Check file size before download
        file_size = 0
        if message.video:
            file_size = message.video.file_size
        elif message.document:
            file_size = message.document.file_size
        elif message.audio:
            file_size = message.audio.file_size
            
        if file_size > Config.MAX_FILE_SIZE:
            await status_message.edit_text(
                f"âŒ **File too large!**\n"
                f"Size: `{get_human_readable_size(file_size)}`\n"
                f"Max allowed: `{get_human_readable_size(Config.MAX_FILE_SIZE)}`"
            )
            return None
        
        file_path = await message.download(
            file_name=os.path.join(user_download_dir, ''),
            progress=progress_func
        )
        
        file_name = os.path.basename(file_path)
        await status_message.edit_text(f"âœ… **Downloaded:** `{file_name}`\n\nPreparing to merge...")
        LOGGER.info(f"Successfully downloaded {file_name} from Telegram for user {user_id}")
        return file_path
        
    except Exception as e:
        try:
            await status_message.edit_text(f"âŒ **Download Failed!**\nError: `{str(e)}`")
        except Exception:
            pass
        LOGGER.error(f"Telegram download error for user {user_id}: {str(e)}")
        return None

def is_valid_url(url: str) -> bool:
    """Validate if URL is properly formatted"""
    try:
        from urllib.parse import urlparse
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_domain_from_url(url: str) -> str:
    """Extract domain from URL"""
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc.lower()
    except:
        return ""
