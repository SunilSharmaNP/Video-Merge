# plugins/mergeVideo.py - Enhanced to use your merger and uploader

import asyncio
import os
import time
from pyrogram import Client
from pyrogram.types import CallbackQuery

# Original imports
from __init__ import LOGGER, UPLOAD_AS_DOC, UPLOAD_TO_DRIVE, queueDB, formatDB

# Enhanced imports - using your functions
from config import Config
from helpers.utils import UserSettings
from helpers.merger import merge_videos  # YOUR merger
from helpers.uploader import uploadVideo, upload_to_gofile  # Enhanced uploader
from helpers.downloader import download_from_tg  # YOUR downloader
from helpers.ffmpeg_helper import take_screen_shot
from helpers.rclone_upload import rclone_driver
from bot import delete_all

# NEW: Import your upload flag
from __init__ import UPLOAD_TO_GOFILE

async def mergeNow(c: Client, cb: CallbackQuery, new_file_name: str):
    """Enhanced merge function using your merger and uploader"""
    user_id = cb.from_user.id
    
    try:
        # Initial status
        await cb.message.edit_text("🚀 **Starting Enhanced Merge Process...**")
        
        # Get user settings
        user = UserSettings(user_id, cb.from_user.first_name)
        
        # Get video files from queue
        video_messages = []
        if queueDB.get(user_id, None) and queueDB[user_id]["videos"]:
            try:
                video_messages = await c.get_messages(
                    chat_id=cb.message.chat.id, 
                    message_ids=queueDB[user_id]["videos"]
                )
            except Exception as e:
                LOGGER.error(f"Error getting messages: {e}")
                await cb.message.edit_text("❌ **Error getting video files!**")
                return
        
        if not video_messages or len(video_messages) < 2:
            await cb.message.edit_text("❌ **Need at least 2 videos to merge!**")
            return
        
        # Download files using YOUR enhanced downloader
        video_files = []
        status_msg = cb.message
        
        for i, msg in enumerate(video_messages):
            if hasattr(msg, 'video') or hasattr(msg, 'document'):
                try:
                    await status_msg.edit_text(f"📥 **Downloading file {i+1}/{len(video_messages)}...**")
                    # Using YOUR download function
                    file_path = await download_from_tg(msg, user_id, status_msg)
                    if file_path:
                        video_files.append(file_path)
                        LOGGER.info(f"Downloaded: {file_path}")
                except Exception as e:
                    LOGGER.error(f"Download failed for message {msg.id}: {e}")
                    continue
        
        if len(video_files) < 2:
            await status_msg.edit_text("❌ **Failed to download enough files for merging!**")
            return
        
        # Use YOUR enhanced merger
        LOGGER.info(f"Starting merge for user {user_id} with {len(video_files)} files")
        merged_file = await merge_videos(video_files, user_id, status_msg)
        
        if not merged_file:
            await status_msg.edit_text("❌ **Merge failed!** Check logs for details.")
            return
        
        # Get file properties for upload
        file_size = os.path.getsize(merged_file)
        custom_filename = os.path.splitext(os.path.basename(new_file_name))[0]
        
        # Create thumbnail (original logic)
        video_thumbnail = None
        try:
            if user.thumbnail:
                video_thumbnail = f"downloads/{user_id}_thumb.jpg"
                if not os.path.exists(video_thumbnail):
                    video_thumbnail = None
            
            if not video_thumbnail:
                await status_msg.edit_text("📸 **Creating thumbnail...**")
                video_thumbnail = await take_screen_shot(merged_file, f"downloads/{user_id}/", 10)
        except Exception as e:
            LOGGER.error(f"Thumbnail creation failed: {e}")
            video_thumbnail = None
        
        # Get video metadata for upload (original logic)
        width = height = duration = 0
        try:
            import ffmpeg
            probe = ffmpeg.probe(merged_file)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            if video_stream:
                width = int(video_stream.get('width', 0))
                height = int(video_stream.get('height', 0))
                duration = float(probe['format'].get('duration', 0))
        except:
            pass
        
        # ENHANCED: Determine upload destination and upload
        if UPLOAD_TO_GOFILE.get(f"{user_id}", False):
            # Use YOUR GoFile upload function
            await upload_to_gofile(merged_file, status_msg, custom_filename)
            
        elif UPLOAD_TO_DRIVE.get(f"{user_id}", False):
            # Original Drive upload using rclone
            await status_msg.edit_text("☁️ **Uploading to Google Drive...**")
            try:
                await rclone_driver(merged_file, new_file_name, user_id, c, cb.message)
            except Exception as e:
                LOGGER.error(f"Drive upload failed: {e}")
                await status_msg.edit_text(f"❌ **Drive upload failed!**\nError: `{str(e)}`")
                
        else:
            # Enhanced Telegram upload using original function + your features
            upload_as_doc = UPLOAD_AS_DOC.get(f"{user_id}", False)
            
            await uploadVideo(
                c=c,
                cb=cb,
                merged_video_path=merged_file,
                width=width,
                height=height,
                duration=duration,
                video_thumbnail=video_thumbnail,
                file_size=file_size,
                upload_mode=upload_as_doc,
                custom_filename=custom_filename,
                upload_to_gofile_flag=False  # Enhanced parameter
            )
        
    except Exception as e:
        LOGGER.error(f"Enhanced merge error: {e}")
        await cb.message.edit_text(f"❌ **Merge process failed!**\nError: `{str(e)}`")
        
    finally:
        # Cleanup (original logic enhanced)
        try:
            # Clean up downloaded files
            for file_path in video_files:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    
            # Clean up merged file
            if 'merged_file' in locals() and merged_file and os.path.exists(merged_file):
                os.remove(merged_file)
                
            # Clean up thumbnail
            if video_thumbnail and os.path.exists(video_thumbnail) and "_thumb.jpg" in video_thumbnail:
                try:
                    os.remove(video_thumbnail)
                except:
                    pass
                    
            # Clean up directories
            await delete_all(root=f"downloads/{user_id}/")
            
        except Exception as e:
            LOGGER.error(f"Cleanup error: {e}")
            
        # Clear queues (original logic)
        queueDB.update({user_id: {"videos": [], "subtitles": [], "audios": []}})
        formatDB.update({user_id: None})
        
        # Reset upload flags (enhanced)
        UPLOAD_AS_DOC.update({f"{user_id}": False})
        UPLOAD_TO_DRIVE.update({f"{user_id}": False})
        UPLOAD_TO_GOFILE.update({f"{user_id}": False})
