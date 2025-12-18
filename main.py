#  MIT License
#  Copyright (c) 2019-present Dan
#  https://github.com/delivrance

import os
import asyncio
import logging
from logging.handlers import RotatingFileHandler

from pyrogram import Client, idle, filters
from pyromod import listen
import tgcrypto

from config import Config

# -------------------------------------------------
# PYROGRAM COMPATIBILITY PATCH (CRITICAL)
# -------------------------------------------------

# Some old repos use filters.edited (removed in newer Pyrogram)
# Create a safe dummy filter so plugins don't crash
if not hasattr(filters, "edited"):
    filters.edited = filters.create(lambda *_: False)

# Some repos also use filters.forwarded
if not hasattr(filters, "forwarded"):
    filters.forwarded = filters.create(lambda *_: False)

# -------------------------------------------------
# LOGGING
# -------------------------------------------------

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

# -------------------------------------------------
# CONFIG
# -------------------------------------------------

AUTH_USERS = [
    int(chat) for chat in Config.AUTH_USERS.split(",") if chat.strip()
]

PREFIXES = ["/", "~", "?", "!"]
prefixes = PREFIXES  # backward compatibility for plugins

PLUGINS = dict(root="plugins")

# -------------------------------------------------
# BOT CLIENT
# -------------------------------------------------

bot = Client(
    name="mrwolf_bot",
    bot_token=os.environ["BOT_TOKEN"],
    api_id=int(os.environ["API_ID"]),
    api_hash=os.environ["API_HASH"],
    plugins=PLUGINS,
    workers=50,
    sleep_threshold=20
)

# -------------------------------------------------
# MAIN
# -------------------------------------------------

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

# -------------------------------------------------
# RUN
# -------------------------------------------------

if __name__ == "__main__":
    asyncio.run(main())
