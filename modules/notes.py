#  Moon-Userbot - telegram userbot
#  Copyright (C) 2020-present Moon Userbot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from pyrogram import Client, filters, errors, enums
from pyrogram.types import Message

from utils.db import db
from utils.misc import modules_help, prefix
from utils.handlers import NoteSendHandler


@Client.on_message(filters.command(["save"], prefix) & filters.me)
async def save_note(client: Client, message: Message):
    await message.edit("<b>Loading...</b>", parse_mode=enums.ParseMode.HTML)

    try:
        chat = await client.get_chat(db.get("core.notes", "chat_id", 0))
    except (errors.RPCError, ValueError, KeyError):
        # group is not accessible or isn't created
        chat = await client.create_supergroup(
            "Moon_Userbot_Notes_Filters", "Don't touch this group, please"
        )
        db.set("core.notes", "chat_id", chat.id)

    chat_id = chat.id

    if message.reply_to_message and len(message.text.split()) >= 2:
        note_name = message.text.split(maxsplit=1)[1]
        if message.reply_to_message.media_group_id:
            checking_note = db.get("core.notes", f"note{note_name}", False)
            if not checking_note:
                get_media_group = [
                    _.id
                    for _ in await client.get_media_group(
                        message.chat.id, message.reply_to_message.id
                    )
                ]
                try:
                    message_id = await client.forward_messages(
                        chat_id, message.chat.id, get_media_group
                    )
                except errors.ChatForwardsRestricted:
                    await message.edit(
                        "<b>Forwarding messages is restricted by chat admins</b>",
                        parse_mode=enums.ParseMode.HTML
                    )
                    return
                note = {
                    "MESSAGE_ID": str(message_id[1].id),
                    "MEDIA_GROUP": True,
                    "CHAT_ID": str(chat_id),
                }
                db.set("core.notes", f"note{note_name}", note)
                await message.edit(f"<b>Note {note_name} saved</b>", parse_mode=enums.ParseMode.HTML)
            else:
                await message.edit("<b>This note already exists</b>", parse_mode=enums.ParseMode.HTML)
        else:
            checking_note = db.get("core.notes", f"note{note_name}", False)
            if not checking_note:
                try:
                    message_id = await message.reply_to_message.forward(chat_id)
                except errors.ChatForwardsRestricted:
                    message_id = await message.copy(chat_id)
                note = {
                    "MEDIA_GROUP": False,
                    "MESSAGE_ID": str(message_id.id),
                    "CHAT_ID": str(chat_id),
                }
                db.set("core.notes", f"note{note_name}", note)
                await message.edit(f"<b>Note {note_name} saved</b>", parse_mode=enums.ParseMode.HTML)
            else:
                await message.edit("<b>This note already exists</b>", parse_mode=enums.ParseMode.HTML)
    elif len(message.text.split()) >= 3:
        note_name = message.text.split(maxsplit=1)[1].split()[0]
        checking_note = db.get("core.notes", f"note{note_name}", False)
        if not checking_note:
            message_id = await client.send_message(
                chat_id, message.text.split(note_name)[1].strip()
            )
            note = {
                "MEDIA_GROUP": False,
                "MESSAGE_ID": str(message_id.id),
                "CHAT_ID": str(chat_id),
            }
            db.set("core.notes", f"note{note_name}", note)
            await message.edit(f"<b>Note {note_name} saved</b>", parse_mode=enums.ParseMode.HTML)
        else:
            await message.edit("<b>This note already exists</b>", parse_mode=enums.ParseMode.HTML)
    else:
        await message.edit(
            f"<b>Example: <code>{prefix}save note_name</code></b>",
            parse_mode=enums.ParseMode.HTML
        )

@Client.on_message(filters.command("note", prefix) & filters.me)
async def note_send(client: Client, message: Message):
    handler = NoteSendHandler(client, message)
    await handler.handle_note_send()



@Client.on_message(filters.command(["notes"], prefix) & filters.me)
async def notes(_, message: Message):
    await message.edit("<b>Loading...</b>", parse_mode=enums.ParseMode.HTML)
    text = "Available notes:\n\n"
    collection = db.get_collection("core.notes")
    for note in collection.keys():
        if note[:4] == "note":
            text += f"<code>{note[4:]}</code>\n"
    await message.edit(text, parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.command(["clear"], prefix) & filters.me)
async def clear_note(_, message: Message):
    if len(message.text.split()) >= 2:
        note_name = message.text.split(maxsplit=1)[1]
        find_note = db.get("core.notes", f"note{note_name}", False)
        if find_note:
            db.remove("core.notes", f"note{note_name}")
            await message.edit(f"<b>Note {note_name} deleted</b>", parse_mode=enums.ParseMode.HTML)
        else:
            await message.edit("<b>There is no such note</b>", parse_mode=enums.ParseMode.HTML)
    else:
        await message.edit(
            f"<b>Example: <code>{prefix}clear note_name</code></b>",
            parse_mode=enums.ParseMode.HTML
        )


modules_help["notes"] = {
    "save [name]*": "Save note",
    "note [name]*": "Get saved note",
    "notes": "Get note list",
    "clear [name]*": "Delete note",
}