from pyrogram import Client, filters
from pyrogram.types import Message
import os
import sys

# =========================
# /start command
# =========================

@Client.on_message(filters.command("start"))
async def start_msg(client: Client, m: Message):
    await client.send_photo(
        chat_id=m.chat.id,
        photo="https://telegra.ph/file/cef3ef6ee69126c23bfe3.jpg",
        caption=(
            "**Hi, I am All in One Extractor Bot 🤖**\n\n"
            "Press **/pw** for **Physics Wallah**\n"
            "Press **/e1** for **E1 Coaching App**\n"
            "Press **/vidya** for **Vidya Bihar App**\n"
            "Press **/ocean** for **Ocean Gurukul App**\n"
            "Press **/winners** for **The Winners Institute**\n"
            "Press **/rgvikramjeet** for **Rg Vikramjeet App**\n"
            "Press **/txt** for **Text Extractors**\n"
            "Press **/cp** for **ClassPlus App**\n"
            "Press **/cw** for **CareerWill App**\n"
            "Press **/khan** for **Khan GS App**\n"
            "Press **/exampur** for **Exampur App**\n"
            "Press **/mgconcept** for **MG Concept App**\n"
            "Press **/down** for **Download URL Lists**\n"
            "Press **/forward** to **Forward Channel Content**\n\n"
            "**Bot Owner : 𝒞𝓇𝓎𝓅𝓉💞𝓈𝓉𝒶𝓇𝓀**"
        )
    )

# =========================
# /restart command
# =========================

@Client.on_message(filters.command("restart"))
async def restart_handler(client: Client, m: Message):
    await m.reply_text("♻️ Restarting bot...")
    os.execl(sys.executable, sys.executable, *sys.argv)

# =========================
# /log command
# =========================

@Client.on_message(filters.command("log"))
async def log_handler(client: Client, m: Message):
    if os.path.exists("log.txt"):
        await client.send_document(m.chat.id, "log.txt")
    else:
        await m.reply_text("No log file found.")
