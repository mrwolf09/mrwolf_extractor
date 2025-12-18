#  MIT License
#  Copyright (c) 2019-present Dan
#  Fixed for Pyrogram v2

from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config

AUTH_USERS = [int(x) for x in Config.AUTH_USERS.split(",") if x.strip()]
PREFIXES = ["/", "!", ".", "?"]


@Client.on_message(
    filters.private
    & filters.user(AUTH_USERS)
    & filters.command("forward", prefixes=PREFIXES)
)
async def forward_handler(client: Client, m: Message):

    msg = await client.ask(
        m.chat.id,
        "📌 **Forward any message from TARGET channel**\nBot must be admin in both channels."
    )

    if not msg.forward_from_chat:
        await m.reply_text("❌ Please forward a message from a channel.")
        return

    target_chat_id = msg.forward_from_chat.id

    msg1 = await client.ask(
        m.chat.id,
        "➡️ **Forward STARTING message from SOURCE channel**"
    )
    msg2 = await client.ask(
        m.chat.id,
        "➡️ **Forward ENDING message from SAME SOURCE channel**"
    )

    if not msg1.forward_from_chat or not msg2.forward_from_chat:
        await m.reply_text("❌ Invalid forwarded messages.")
        return

    source_chat_id = msg1.forward_from_chat.id
    start_id = msg1.forward_from_message_id
    end_id = msg2.forward_from_message_id

    await m.reply_text("✅ **Forwarding Started...**")

    for i in range(start_id, end_id + 1):
        try:
            await client.copy_message(
                chat_id=target_chat_id,
                from_chat_id=source_chat_id,
                message_id=i
            )
        except Exception:
            continue

    await m.reply_text("✅ **Done Forwarding**")
