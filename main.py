#  MIT License
#
#  Copyright (c) 2019-present Dan
#  https://github.com/delivrance
#

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
    name="StarkBot",
    bot_token=os.environ.get("BOT_TOKEN"),
    api_id=int(os.environ.get("API_ID")),
    api_hash=os.environ.get("API_HASH"),
    plugins=PLUGINS,
    workers=50,
    sleep_threshold=20
)

# ---------------- MAIN ---------------- #

async def main():
    try:
        await bot.start()
        bot_info = await bot.get_me()
        LOGGER.info(f"<--- @{bot_info.username} Started Successfully --->")
        await idle()
    except Exception as e:
        LOGGER.exception("Bot crashed due to error:")
        raise e
    finally:
        await bot.stop()
        LOGGER.info("<--- Bot Stopped --->")

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    asyncio.run(main())
