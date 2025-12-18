#  MIT License
#  Copyright (c) 2019-present Dan

import os
import asyncio
import logging
import threading
from logging.handlers import RotatingFileHandler
from http.server import HTTPServer, BaseHTTPRequestHandler

from pyrogram import Client
import tgcrypto

from config import Config

# ================= LOGGING =================

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

# ================= CONFIG =================

AUTH_USERS = [int(x) for x in Config.AUTH_USERS.split(",") if x.strip()]
prefixes = ["/", "!", ".", "?"]

PLUGINS = dict(root="plugins")

# ================= BOT =================

bot = Client(
    name="mrwolf_bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=PLUGINS,
    workers=50,
    sleep_threshold=20,
)

# ================= HEALTH SERVER =================

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

# ================= MAIN =================

async def main():
    threading.Thread(target=run_web, daemon=True).start()

    await bot.start()
    me = await bot.get_me()
    LOGGER.info(f"@{me.username} started successfully")

    await asyncio.Event().wait()

# ================= RUN =================

if __name__ == "__main__":
    asyncio.run(main())
