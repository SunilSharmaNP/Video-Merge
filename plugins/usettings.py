import time
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup
from helpers.msg_utils import MakeButtons
from helpers.utils import UserSettings

@Client.on_message(filters.command(["settings"]))
async def f1(c: Client, m: Message):
    status_msg = await m.reply("Please wait...", quote=True)
    usettings = UserSettings(m.from_user.id, m.from_user.first_name)
    await userSettings(status_msg, m.from_user.id, m.from_user.first_name, m.from_user.last_name, usettings)

async def userSettings(
    editable: Message,
    uid: int,
    fname: str,
    lname: str,
    usettings: UserSettings,
):
    b = MakeButtons()
    # Determine merge mode string
    modes = {
        1: "Video 🎥 + Video 🎥",
        2: "Video 🎥 + Audio 🎵",
        3: "Video 🎥 + Subtitle 📜",
        4: "Extract Streams 🔄",
        5: "URL Merge 🔗"
    }
    mode_id = usettings.merge_mode if usettings.merge_mode in modes else 1
    mode_str = modes.get(mode_id, modes[1])

    edit_meta = "✅" if usettings.edit_metadata else "❌"
    ban_status = "🚫 BANNED" if usettings.banned else "✅ Active"
    allow_status = "⚡ Allowed" if usettings.allowed else "❗ Not Allowed"

    text = f"""
<b><u>Merge Bot Settings</u></b>
<b>User:</b> <a href='tg://user?id={uid}'>{fname} {lname}</a>
<b>ID:</b> {uid}
<b>Status:</b> {ban_status} | {allow_status}
<b>Edit Metadata:</b> {edit_meta}
<b>Merge Mode:</b> {mode_str}
"""

    buttons = [
        [
            InlineKeyboardButton("🔀 Change Mode", callback_data=f"ch@ng3M0de_{uid}_{(mode_id % len(modes)) + 1}"),
            InlineKeyboardButton("✏️ Toggle Metadata", callback_data=f"toggleEdit_{uid}")
        ],
        [
            InlineKeyboardButton("❌ Close", callback_data="close")
        ]
    ]

    await editable.edit(
        text=text,
        reply_markup=InlineKeyboardMarkup(b.makebuttons(
            [ "Change Mode", mode_str, "Edit Metadata", edit_meta, "Close" ],
            [ f"ch@ng3M0de_{uid}_{(mode_id % len(modes)) + 1}", "ignore",
              f"toggleEdit_{uid}", "ignore", "close" ],
            rows=2
        ))
    )
