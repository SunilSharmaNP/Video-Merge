import asyncio
import os
import time
from pyrogram import Client
from pyrogram.types import CallbackQuery

from __init__ import LOGGER, UPLOAD_AS_DOC, UPLOAD_TO_DRIVE, UPLOAD_TO_GOFILE, queueDB, formatDB
from config import Config
from helpers.utils import UserSettings, get_readable_file_size
from helpers.merger import merge_videos, MergeSubNew
from helpers.uploader import uploadVideo, upload_to_gofile
from helpers.downloader import download_from_tg
from helpers.rclone_upload import rclone_driver
from bot import delete_all


async def mergeSub(c: Client, cb: CallbackQuery, new_file_name: str):
    user_id = cb.from_user.id
    try:
        await cb.message.edit_text("🚀 **Starting Subtitle Merge Process...**")
        user = UserSettings(user_id, cb.from_user.first_name)

        vid_id = queueDB.get(user_id, {}).get("videos", [None])[0]
        sub_ids = queueDB.get(user_id, {}).get("subtitles", [])
        if not vid_id or not sub_ids:
            await cb.message.edit_text("❌ **Need a base video and at least one subtitle file!**")
            return

        base_msg = await c.get_messages(cb.message.chat.id, vid_id)
        base_path = await download_from_tg(base_msg, user_id, cb.message)

        sub_paths = []
        for i, sid in enumerate(sub_ids, 1):
            if sid:
                msg = await c.get_messages(cb.message.chat.id, sid)
                await cb.message.edit_text(f"📥 **Downloading subtitle {i}/{len(sub_ids)}...**")
                path = await download_from_tg(msg, user_id, cb.message)
                if path:
                    sub_paths.append(path)

        merged = await MergeSubNew(base_path, None, user_id, sub_paths)
        if not merged:
            await cb.message.edit_text("❌ **Subtitle merge failed!**")
            return

        thumbnail = None
        if user.thumbnail:
            tn = f"downloads/{user_id}_thumb.jpg"
            thumbnail = tn if os.path.exists(tn) else None

        width = height = duration = 0
        file_size = os.path.getsize(merged)
        basename = os.path.splitext(os.path.basename(new_file_name))[0]

        if UPLOAD_TO_GOFILE.get(str(user_id)):
            await upload_to_gofile(merged, cb.message, basename)
        elif UPLOAD_TO_DRIVE.get(str(user_id)):
            await cb.message.edit_text("☁️ **Uploading to Google Drive...**")
            await rclone_driver(merged, new_file_name, user_id, c, cb.message)
        else:
            upload_mode = UPLOAD_AS_DOC.get(str(user_id), False)
            await uploadVideo(
                c,
                cb,
                merged,
                width,
                height,
                duration,
                thumbnail,
                file_size,
                upload_mode,
                basename,
                False,
            )
    except Exception as e:
        LOGGER.error(f"Subtitle merge error: {e}")
        await cb.message.edit_text(f"❌ **Subtitle merge failed!**\nError: `{e}`")
    finally:
        try:
            os.remove(merged)
        except:
            pass
        await delete_all(root=f"downloads/{user_id}/")
        queueDB[user_id] = {"videos": [], "subtitles": [], "audios": []}
        formatDB[user_id] = None
        UPLOAD_AS_DOC[str(user_id)] = False
        UPLOAD_TO_DRIVE[str(user_id)] = False
        UPLOAD_TO_GOFILE[str(user_id)] = False
