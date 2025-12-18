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

# Old repos use filters.edited / filters.forwarded
# Create safe dummy filters so plugins never crash
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
prefixes = PREFIXES  # backward compatibility for plugins

PLUGINS = dict(root="plugins")

# =================================================
# BOT CLIENT
# =================================================

bot = Client(
    name="mrwolf_bot",               # no spaces, avoids old sessions
    bot_token=os.environ["BOT_TOKEN"],
    api_id=int(os.environ["API_ID"]),
    api_hash=os.environ["API_HASH"],
    plugins=PLUGINS,
    workers=50,
    sleep_threshold=20
)

# =================================================
# DUMMY WEB SERVER (RENDER FREE FIX)
# =================================================

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

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
        # Start dummy HTTP server for Render
        threading.Thread(target=run_web, daemon=True).start()

        # Start Telegram bot
        await bot.start()
        me = await bot.get_me()
        LOGGER.info(f"<--- @{me.username} Started Successfully --->")

        # Keep process alive forever (Render-friendly)
        while True:
            await asyncio.sleep(60)

    except asyncio.CancelledError:
        LOGGER.warning("Process cancelled (Render shutdown)")
    except Exception:
        LOGGER.exception("Bot crashed due to error")

# =================================================
# RUN
# =================================================

if __name__ == "__main__":
    asyncio.run(main())
