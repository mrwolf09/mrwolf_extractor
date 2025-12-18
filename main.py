#  MIT License
#  Copyright (c) 2019-present Dan
#  https://github.com/delivrance

import os
import asyncio
import logging
import threading
from logging.handlers import RotatingFileHandler
from http.server import HTTPServer, BaseHTTPRequestHandler

from pyrogram import Client, filters
from pyromod import listen
import tgcrypto

from config import Config

# =================================================
# PYROGRAM v1 → v2 COMPATIBILITY PATCH
# =================================================

if not hasattr(filters, "edited"):
    filters.edited = filters.create(lambda *_: False)

if not hasattr(filters, "forwarded"):
    filters.forwarded = filters.create(lambda *_: False)

# =================================================
# LOGGING
# =================================================

LOGGER = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler("log.txt", maxBytes=5_000_000, backupCount=10),
        logging.StreamHandler(),
    ],
)

# =================================================
# CONFIG
# =================================================

AUTH_USERS = [
    int(chat) for chat in Config.AUTH_USERS.split(",") if chat.strip()
]

PREFIXES = ["/", "~", "?", "!"]
prefixes = PREFIXES  # backward compatibility

PLUGINS = dict(root="plugins")

# =================================================
# BOT CLIENT
# =================================================

bot = Client(
    name="mrwolf_bot",
    bot_token=os.environ["BOT_TOKEN"],
    api_id=int(os.environ["API_ID"]),
    api_hash=os.environ["API_HASH"],
    plugins=PLUGINS,
    workers=50,
    sleep_threshold=20
)

# =================================================
# DEBUG HANDLER (TEMPORARY)
# =================================================

@bot.on_message(filters.all)
async def debug_all(_, m):
    try:
        print(
            "RECEIVED:",
            m.text,
            "FROM:",
            m.from_user.id if m.from_user else None,
            "CHAT:",
            m.chat.id
        )
    except Exception as e:
        print("DEBUG ERROR:", e)

# =================================================
# DUMMY WEB SERVER (RENDER FREE)
# =================================================

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_web():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    LOGGER.info(f"Health server running on port {port}")
    server.serve_forever()

# =================================================
# MAIN
# =================================================

async def main():
    try:
        threading.Thread(target=run_web, daemon=True).start()

        await bot.start()
        me = await bot.get_me()
        LOGGER.info(f"<--- @{me.username} Started Successfully --->")

        while True:
            await asyncio.sleep(60)

    except asyncio.CancelledError:
        LOGGER.warning("Cancelled by Render")
    except Exception:
        LOGGER.exception("Bot crashed")

# =================================================
# RUN
# =================================================

if __name__ == "__main__":
    asyncio.run(main())
