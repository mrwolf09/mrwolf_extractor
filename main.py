#  MIT License
#  Copyright (c) 2019-present Dan
#  https://github.com/delivrance

import os
import asyncio
import logging
from logging.handlers import RotatingFileHandler

from pyrogram import Client, idle
from pyromod import listen
import tgcrypto

from config import Config

# ---------------- LOGGING ---------------- #

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

# ---------------- CONFIG ---------------- #

AUTH_USERS = [
    int(chat) for chat in Config.AUTH_USERS.split(",") if chat.strip()
]

PREFIXES = ["/", "~", "?", "!"]
PLUGINS = dict(root="plugins")

# ---------------- BOT CLIENT ---------------- #

bot = Client(
    name="mrwolf_bot",          # ✅ NO SPACES, FRESH SESSION
    bot_token=os.environ["BOT_TOKEN"],
    api_id=int(os.environ["API_ID"]),
    api_hash=os.environ["API_HASH"],
    plugins=PLUGINS,
    workers=50,
    sleep_threshold=20
)

# ---------------- MAIN ---------------- #

async def main():
    started = False
    try:
        await bot.start()
        started = True
        me = await bot.get_me()
        LOGGER.info(f"<--- @{me.username} Started Successfully --->")
        await idle()
    except Exception:
        LOGGER.exception("Bot crashed due to error:")
        raise
    finally:
        if started:
            await bot.stop()
            LOGGER.info("<--- Bot Stopped --->")

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    asyncio.run(main())
