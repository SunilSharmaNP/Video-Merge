import asyncio
import os
from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyromod.types import ListenerTypes
from pyromod.listen import Client

from bot import (
    LOGGER,
    UPLOAD_AS_DOC,
    UPLOAD_TO_DRIVE,
    UPLOAD_TO_GOFILE,
    delete_all,
    formatDB,
    gDict,
    queueDB,
    urlDB,
)
from helpers import database
from helpers.utils import UserSettings
from plugins.mergeVideo import mergeNow
from plugins.mergeVideoAudio import mergeAudio
from plugins.mergeVideoSub import mergeSub
from plugins.streams_extractor import streamsExtractor
from plugins.usettings import userSettings


@Client.on_callback_query()
async def callback_handler(c: Client, cb: CallbackQuery):
    data = cb.data
    uid = cb.from_user.id

    if data == "merge":
        await cb.message.edit(
            "Where do you want to upload?",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📤 To Telegram", callback_data="to_telegram"),
                    InlineKeyboardButton("🌫️ To Drive", callback_data="to_drive"),
                ],
                [InlineKeyboardButton("📁 To GoFile", callback_data="to_gofile")],
                [InlineKeyboardButton("⛔ Cancel", callback_data="cancel")],
            ])
        )
        return

    elif data == "to_gofile":
        UPLOAD_TO_GOFILE[str(uid)] = True
        UPLOAD_TO_DRIVE[str(uid)] = False
        await cb.message.edit(
            "📁 Upload to GoFile.io\nRename file? Default: **[@yashoswalyo]_merged.mkv**",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("👆 Default", callback_data="rename_NO"),
                    InlineKeyboardButton("✍️ Rename", callback_data="rename_YES"),
                ],
                [InlineKeyboardButton("⛔ Cancel", callback_data="cancel")],
            ])
        )
        return

    elif data == "to_drive":
        try:
            urc = await database.getUserRcloneConfig(uid)
            await c.download_media(urc, file_name=f"userdata/{uid}/rclone.conf")
        except:
            await cb.message.reply_text("Rclone not found, cannot upload to Drive")
        if not os.path.exists(f"userdata/{uid}/rclone.conf"):
            await cb.message.delete()
            await delete_all(f"downloads/{uid}/")
            queueDB[uid] = {"videos": [], "subtitles": [], "audios": []}
            formatDB[uid] = None
            return
        UPLOAD_TO_DRIVE[str(uid)] = True
        UPLOAD_TO_GOFILE[str(uid)] = False
        await cb.message.edit(
            "☁️ Upload to Drive\nRename file? Default: **[@yashoswalyo]_merged.mkv**",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("👆 Default", callback_data="rename_NO"),
                    InlineKeyboardButton("✍️ Rename", callback_data="rename_YES"),
                ],
                [InlineKeyboardButton("⛔ Cancel", callback_data="cancel")],
            ])
        )
        return

    elif data == "to_telegram":
        UPLOAD_TO_DRIVE[str(uid)] = False
        UPLOAD_TO_GOFILE[str(uid)] = False
        await cb.message.edit(
            "How do you want to upload the file?",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🎞️ Video", callback_data="video"),
                    InlineKeyboardButton("📁 Document", callback_data="document"),
                ],
                [InlineKeyboardButton("⛔ Cancel", callback_data="cancel")],
            ])
        )
        return

    elif data == "document":
        UPLOAD_AS_DOC[str(uid)] = True
        await cb.message.edit(
            "Upload as document\nRename file? Default: **[@yashoswalyo]_merged.mkv**",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("👆 Default", callback_data="rename_NO"),
                    InlineKeyboardButton("✍️ Rename", callback_data="rename_YES"),
                ],
                [InlineKeyboardButton("⛔ Cancel", callback_data="cancel")],
            ])
        )
        return

    elif data == "video":
        UPLOAD_AS_DOC[str(uid)] = False
        await cb.message.edit(
            "Upload as video\nRename file? Default: **[@yashoswalyo]_merged.mkv**",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("👆 Default", callback_data="rename_NO"),
                    InlineKeyboardButton("✍️ Rename", callback_data="rename_YES"),
                ],
                [InlineKeyboardButton("⛔ Cancel", callback_data="cancel")],
            ])
        )
        return

    elif data.startswith("rclone_"):
        if "save" in data:
            file_id = cb.message.reply_to_message.document.file_id
            LOGGER.info(f"Saving rclone config: {file_id}")
            await c.download_media(cb.message.reply_to_message, file_name=f"userdata/{uid}/rclone.conf")
            await database.addUserRcloneConfig(cb, file_id)
        else:
            await cb.message.delete()
        return

    elif data.startswith("rename_"):
        user = UserSettings(uid, cb.from_user.first_name)
        if "YES" in data:
            await cb.message.edit(
                "Current filename: **[@yashoswalyo]_merged.mkv**\n\n"
                "Send new filename (without extension), you have 1 minute."
            )
            try:
                res: Message = await c.listen(
                    cb.message.chat.id, filters.text, timeout=60, listener_type=ListenerTypes.MESSAGE
                )
            except asyncio.TimeoutError:
                await cb.message.edit("⏰ Timeout! Using default filename.")
                new_name = f"downloads/{uid}/[@yashoswalyo]_merged.mkv"
            else:
                new_name = f"downloads/{uid}/{res.text}.mkv"
                await res.delete(True)

        else:
            new_name = f"downloads/{uid}/[@yashoswalyo]_merged.mkv"

        mode = user.merge_mode
        if mode == 1:
            await mergeNow(c, cb, new_name)
        elif mode == 2:
            await mergeAudio(c, cb, new_name)
        elif mode == 3:
            await mergeSub(c, cb, new_name)
        return

    elif data == "cancel":
        await delete_all(f"downloads/{uid}/")
        queueDB[uid] = {"videos": [], "subtitles": [], "audios": []}
        formatDB[uid] = None
        await cb.message.edit("✅ Successfully Cancelled")
        await asyncio.sleep(2)
        await cb.message.delete(True)
        return

    elif data.startswith("gUPcancel"):
        _, chat_id, mes_id, from_usr = data.split("/")
        if str(uid) == from_usr:
            await c.answer_callback_query(cb.id, "Cancelling...", show_alert=False)
            gDict[int(chat_id)].append(int(mes_id))
        else:
            await c.answer_callback_query(
                cb.id,
                "⚠️ Unauthorized",
                show_alert=True,
                cache_time=0,
            )
        await delete_all(f"downloads/{uid}/")
        queueDB[uid] = {"videos": [], "subtitles": [], "audios": []}
        formatDB[uid] = None
        return

    elif data == "close":
        await cb.message.delete(True)
        try:
            await cb.message.reply_to_message.delete(True)
        except:
            pass
        return

    elif data.startswith("showFileName_"):
        msg_id = int(data.split("_", 1)[1])
        user = UserSettings(uid, cb.from_user.first_name)
        idx = queueDB[uid]["videos"].index(msg_id)
        main_msg = await c.get_messages(cb.message.chat.id, msg_id)
        sub_id = queueDB[uid]["subtitles"][idx]
        buttons = []
        if sub_id:
            sub_msg = await c.get_messages(cb.message.chat.id, sub_id)
            buttons = [
                [
                    InlineKeyboardButton("❌ Remove File", callback_data=f"removeFile_{msg_id}"),
                    InlineKeyboardButton("❌ Remove Subtitle", callback_data=f"removeSub_{idx}"),
                ],
                [InlineKeyboardButton("🔙 Back", callback_data="back")],
            ]
            text = (
                f"File: {main_msg.document.file_name}\n"
                f"Subtitle: {sub_msg.document.file_name}"
            )
        else:
            buttons = [
                [
                    InlineKeyboardButton("❌ Remove", callback_data=f"removeFile_{msg_id}"),
                    InlineKeyboardButton("📜 Add Subtitle", callback_data=f"addSub_{idx}"),
                ],
                [InlineKeyboardButton("🔙 Back", callback_data="back")],
            ]
            text = f"File: {main_msg.document.file_name}"
        await cb.message.edit(text, reply_markup=InlineKeyboardMarkup(buttons))
        return

    elif data.startswith("addSub_"):
        idx = int(data.split("_", 1)[1])
        vid_id = queueDB[uid]["videos"][idx]
        await cb.message.edit(
            "Send subtitle file (1 minute):",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=f"showFileName_{vid_id}")]]),
        )
        try:
            sub_msg: Message = await c.listen(cb.message.chat.id, filters.document, timeout=60)
        except asyncio.TimeoutError:
            await cb.message.edit("⏰ Timeout! Returning.")
            return
        ext = sub_msg.document.file_name.rsplit(".", 1)[-1].lower()
        if ext not in ["srt", "ass", "vtt"]:
            await sub_msg.reply("Invalid subtitle format", quote=True)
            return
        queueDB[uid]["subtitles"][idx] = sub_msg.id
        await sub_msg.reply("Subtitle added", quote=True)
        await cb.message.edit("Returning to file menu", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=f"showFileName_{vid_id}")]]))
        return

    elif data.startswith("removeSub_"):
        idx = int(data.split("_", 1)[1])
        vid_id = queueDB[uid]["videos"][idx]
        queueDB[uid]["subtitles"][idx] = None
        await cb.message.edit("Subtitle removed", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=f"showFileName_{vid_id}")]]))
        return

    elif data == "back":
        await showQueue(c, cb)
        return

    elif data.startswith("removeFile_"):
        msg_id = int(data.split("_", 1)[1])
        queueDB[uid]["videos"].remove(msg_id)
        queueDB[uid]["subtitles"].pop(queueDB[uid]["videos"].index(msg_id), None)
        await showQueue(c, cb)
        return

    elif data.startswith("ch@ng3M0de_"):
        _, uid_str, mode_str = data.split("_")
        user = UserSettings(int(uid_str), cb.from_user.first_name)
        user.merge_mode = int(mode_str)
        user.set()
        await userSettings(cb.message, int(uid_str), cb.from_user.first_name, cb.from_user.last_name, user)
        return

    elif data.startswith("toggleEdit_"):
        _, uid_str = data.split("_")
        user = UserSettings(int(uid_str), cb.from_user.first_name)
        user.edit_metadata = not user.edit_metadata
        user.set()
        await userSettings(cb.message, int(uid_str), cb.from_user.first_name, cb.from_user.last_name, user)
        return

    elif data.startswith("extract_"):
        parts = data.split("_")
        action, mid = parts[1], int(parts[2])
        await streamsExtractor(c, cb, mid, exAudios=(action=="audio"), exSubs=(action=="subtitle"))
        return

    else:
        await cb.answer("Unknown action", show_alert=False)
