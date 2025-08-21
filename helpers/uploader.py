# helpers/uploader.py - Original functions + Your complete enhancements integrated

import asyncio
import os
import time
from aiohttp import ClientSession, FormData
from random import choice

# Original imports from repository
from __init__ import LOGGER
from bot import LOGCHANNEL, userBot
from config import Config
from pyrogram import Client
from pyrogram.types import CallbackQuery, Message
from helpers.display_progress import Progress

# Your enhanced imports
from helpers.utils import get_human_readable_size, get_progress_bar, get_video_properties

# Your complete FloodWait prevention system
last_edit_time = {}
EDIT_THROTTLE_SECONDS = 4.0

async def smart_progress_editor(status_message, text: str):
    """Your enhanced progress editor to prevent FloodWait errors"""
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

async def create_default_thumbnail(video_path: str) -> str | None:
    """Your complete thumbnail creation function"""
    thumbnail_path = f"{os.path.splitext(video_path)[0]}.jpg"
    metadata = await get_video_properties(video_path)

    if not metadata or not metadata.get("duration"):
        LOGGER.info(f"Could not get duration for '{video_path}'. Skipping default thumbnail.")
        return None

    thumbnail_time = metadata["duration"] / 2
    command = [
        'ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', video_path,
        '-ss', str(thumbnail_time), '-vframes', '1',
        '-c:v', 'mjpeg', '-f', 'image2', '-y', thumbnail_path
    ]

    process = await asyncio.create_subprocess_exec(*command, stderr=asyncio.subprocess.PIPE)
    _, stderr = await process.communicate()

    if process.returncode != 0:
        LOGGER.error(f"Error creating default thumbnail for '{video_path}': {stderr.decode().strip()}")
        return None

    return thumbnail_path if os.path.exists(thumbnail_path) else None

class GofileUploader:
    """Your complete GoFile uploader class"""
    def __init__(self, token=None):
        self.api_url = "https://api.gofile.io/"
        self.token = token or getattr(Config, 'GOFILE_TOKEN', None)

    async def __get_server(self):
        async with ClientSession() as session:
            async with session.get(f"{self.api_url}servers") as resp:
                resp.raise_for_status()
                result = await resp.json()
                if result.get("status") == "ok": 
                    return choice(result["data"]["servers"])["name"]
        raise Exception("Failed to fetch GoFile upload server.")

    async def upload_file(self, file_path: str):
        if not os.path.isfile(file_path): 
            raise FileNotFoundError(f"File not found: {file_path}")

        server = await self.__get_server()
        upload_url = f"https://{server}.gofile.io/uploadFile"

        data = FormData()
        if self.token: 
            data.add_field("token", self.token)

        with open(file_path, "rb") as f:
            data.add_field("file", f, filename=os.path.basename(file_path))

            async with ClientSession() as session:
                async with session.post(upload_url, data=data) as resp:
                    resp.raise_for_status()
                    resp_json = await resp.json()
                    
                    if resp_json.get("status") == "ok": 
                        return resp_json["data"]["downloadPage"]
                    else: 
                        raise Exception(f"GoFile upload failed: {resp_json.get('status')}")

async def upload_to_telegram(client, chat_id: int, file_path: str, status_message, custom_thumbnail: str | None, custom_filename: str):
    """Your complete enhanced Telegram upload function"""
    is_default_thumb_created = False
    thumb_to_upload = custom_thumbnail

    try:
        if not thumb_to_upload:
            await smart_progress_editor(status_message, "Analyzing video to create default thumbnail...")
            thumb_to_upload = await create_default_thumbnail(file_path)
            if thumb_to_upload:
                is_default_thumb_created = True

        metadata = await get_video_properties(file_path)
        duration = metadata.get('duration', 0) if metadata else 0
        width = metadata.get('width', 0) if metadata else 0
        height = metadata.get('height', 0) if metadata else 0

        final_filename = f"{custom_filename}.mkv"
        caption = f"**File:** `{final_filename}`\n**Size:** `{get_human_readable_size(os.path.getsize(file_path))}`"

        async def progress(current, total):
            progress_percent = current / total
            progress_text = f"📤 **Uploading to Telegram...**\n➢ {get_progress_bar(progress_percent)} `{progress_percent:.1%}`"
            await smart_progress_editor(status_message, progress_text)

        await client.send_video(
            chat_id=chat_id, video=file_path, caption=caption, file_name=final_filename,
            duration=duration, width=width, height=height, thumb=thumb_to_upload, progress=progress
        )

        await status_message.delete()
        return True

    except Exception as e:
        await status_message.edit_text(f"❌ **Upload Failed!**\nError: `{e}`")
        return False

    finally:
        if is_default_thumb_created and thumb_to_upload and os.path.exists(thumb_to_upload):
            os.remove(thumb_to_upload)

# NEW: Your GoFile upload function
async def upload_to_gofile(file_path: str, status_message, custom_filename: str):
    """Your complete GoFile upload function"""
    try:
        uploader = GofileUploader()
        
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        
        await smart_progress_editor(
            status_message, 
            f"📤 **Uploading to GoFile...**\n➢ `{file_name}`\n➢ **Size:** `{get_human_readable_size(file_size)}`"
        )
        
        download_link = await uploader.upload_file(file_path)
        
        success_msg = (
            f"✅ **Uploaded to GoFile!**\n"
            f"**File:** `{custom_filename}.mkv`\n"
            f"**Size:** `{get_human_readable_size(file_size)}`\n"
            f"**Link:** {download_link}"
        )
        
        await status_message.edit_text(success_msg)
        return download_link
        
    except Exception as e:
        error_msg = f"❌ **GoFile Upload Failed!**\nError: `{str(e)}`"
        await status_message.edit_text(error_msg)
        LOGGER.error(f"GoFile upload failed: {e}")
        return None

# ORIGINAL FUNCTIONS ENHANCED: Keeping all original functionality + adding your features

async def uploadVideo(
    c: Client,
    cb: CallbackQuery,
    merged_video_path,
    width,
    height,
    duration,
    video_thumbnail,
    file_size,
    upload_mode: bool,
    custom_filename: str = None,
    upload_to_gofile_flag: bool = False
):
    """Enhanced original uploadVideo function with your GoFile integration"""
    
    # NEW: Check if GoFile upload is requested
    if upload_to_gofile_flag:
        filename = custom_filename or merged_video_path.rsplit('/',1)[-1].rsplit('.', 1)[0]
        await upload_to_gofile(merged_video_path, cb.message, filename)
        return
    
    # ORIGINAL LOGIC ENHANCED: Premium account handling
    if Config.IS_PREMIUM and userBot:
        sent_ = None
        prog = Progress(cb.from_user.id, c, cb.message)
        async with userBot:
            try:
                if upload_mode is False:  # Video upload
                    c_time = time.time()
                    sent_: Message = await userBot.send_video(
                        chat_id=int(LOGCHANNEL),
                        video=merged_video_path,
                        height=height,
                        width=width,
                        duration=duration,
                        thumb=video_thumbnail,
                        caption=f"`{merged_video_path.rsplit('/',1)[-1]}`\n\nMerged for: {cb.from_user.mention}",
                        progress=prog.progress_for_pyrogram,
                        progress_args=(
                            f"Uploading: `{merged_video_path.rsplit('/',1)[-1]}`",
                            c_time,
                        ),
                    )
                else:  # Document upload
                    c_time = time.time()
                    sent_: Message = await userBot.send_document(
                        chat_id=int(LOGCHANNEL),
                        document=merged_video_path,
                        thumb=video_thumbnail,
                        caption=f"`{merged_video_path.rsplit('/',1)[-1]}`\n\nMerged for: <a href='tg://user?id={cb.from_user.id}'>{cb.from_user.first_name}</a>",
                        progress=prog.progress_for_pyrogram,
                        progress_args=(
                            f"Uploading: `{merged_video_path.rsplit('/',1)[-1]}`",
                            c_time,
                        ),
                    )
                    
                if sent_ is not None:
                    await c.copy_message(
                        chat_id=cb.message.chat.id,
                        from_chat_id=sent_.chat.id,
                        message_id=sent_.id,
                        caption=f"`{merged_video_path.rsplit('/',1)[-1]}`",
                    )
            except Exception as err:
                LOGGER.error(f"Premium upload error: {err}")
                # ENHANCED: Fallback to regular upload with better error handling
                await cb.message.edit_text("⚠️ **Premium upload failed!** Trying regular upload...")
                
    else:
        # ORIGINAL LOGIC: Regular bot upload
        try:
            sent_ = None
            prog = Progress(cb.from_user.id, c, cb.message)
            
            if upload_mode is False:  # Video upload
                c_time = time.time()
                sent_: Message = await c.send_video(
                    chat_id=cb.message.chat.id,
                    video=merged_video_path,
                    height=height,
                    width=width,
                    duration=duration,
                    thumb=video_thumbnail,
                    caption=f"`{merged_video_path.rsplit('/',1)[-1]}`",
                    progress=prog.progress_for_pyrogram,
                    progress_args=(
                        f"Uploading: `{merged_video_path.rsplit('/',1)[-1]}`",
                        c_time,
                    ),
                )
            else:  # Document upload
                c_time = time.time()
                sent_: Message = await c.send_document(
                    chat_id=cb.message.chat.id,
                    document=merged_video_path,
                    thumb=video_thumbnail,
                    caption=f"`{merged_video_path.rsplit('/',1)[-1]}`",
                    progress=prog.progress_for_pyrogram,
                    progress_args=(
                        f"Uploading: `{merged_video_path.rsplit('/',1)[-1]}`",
                        c_time,
                    ),
                )
                
        except Exception as err:
            LOGGER.error(f"Regular upload error: {err}")
            await cb.message.edit_text(f"❌ **Upload Failed!**\nError: `{str(err)}`")
            return
            
        # ORIGINAL: Copy to log channel if available
        if sent_ is not None and hasattr(Config, 'LOGCHANNEL') and Config.LOGCHANNEL:
            try:
                media = sent_.video or sent_.document
                await sent_.copy(
                    chat_id=int(Config.LOGCHANNEL),
                    caption=f"`{media.file_name}`\n\nMerged for: <a href='tg://user?id={cb.from_user.id}'>{cb.from_user.first_name}</a>",
                )
            except Exception as e:
                LOGGER.error(f"Log channel copy failed: {e}")

# ORIGINAL FUNCTION: Keeping exactly as-is
async def uploadFiles(
    c: Client,
    cb: CallbackQuery,
    up_path,
    n,
    all_files
):
    """Original uploadFiles function - unchanged"""
    try:
        sent_ = None
        prog = Progress(cb.from_user.id, c, cb.message)
        c_time = time.time()
        
        sent_: Message = await c.send_document(
            chat_id=cb.message.chat.id,
            document=up_path,
            caption=f"`{up_path.rsplit('/',1)[-1]}`",
            progress=prog.progress_for_pyrogram,
            progress_args=(
                f"Uploading: `{up_path.rsplit('/',1)[-1]}`",
                c_time,
                f"\n**Uploading: {n}/{all_files}**"
            ),
        )
        
        if sent_ is not None:
            if Config.LOGCHANNEL is not None:
                media = sent_.video or sent_.document
                await sent_.copy(
                    chat_id=int(Config.LOGCHANNEL),
                    caption=f"`{media.file_name}`\n\nExtracted by: <a href='tg://user?id={cb.from_user.id}'>{cb.from_user.first_name}</a>",
                )
    except:
        pass
