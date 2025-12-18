#  MIT License
#  Copyright (c) 2019-present Dan
#  Code edited By Cryptostark (fixed for Pyrogram v2)

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait

import requests
import subprocess
import time
import os
import sys
from subprocess import getstatusoutput

import helper
from p_bar import progress_bar


@Client.on_message(filters.command("cpd"))
async def account_login(client: Client, m: Message):

    editable = await m.reply_text("**Send txt file**")
    input_file: Message = await client.listen(editable.chat.id)
    file_path = await input_file.download()
    await input_file.delete(True)

    try:
        with open(file_path, "r") as f:
            content = f.read().splitlines()
        links = [i.split(":", 1) for i in content if ":" in i]
        os.remove(file_path)
    except Exception:
        await m.reply_text("❌ Invalid file input.")
        if os.path.exists(file_path):
            os.remove(file_path)
        return

    editable = await m.reply_text(
        f"Total links found **{len(links)}**\n\nSend starting index (default 0)"
    )
    input1: Message = await client.listen(editable.chat.id)

    try:
        start_index = int(input1.text)
    except:
        start_index = 0

    editable = await m.reply_text("**Enter Title**")
    input_title: Message = await client.listen(editable.chat.id)
    title_text = input_title.text

    await m.reply_text("**Enter resolution**")
    input_res: Message = await client.listen(editable.chat.id)
    resolution = input_res.text

    editable = await m.reply_text(
        "Send **Thumbnail URL** or type **no**"
    )
    input_thumb: Message = await client.listen(editable.chat.id)
    thumb = input_thumb.text

    if thumb.startswith("http"):
        getstatusoutput(f"wget '{thumb}' -O thumb.jpg")
        thumb = "thumb.jpg"
    else:
        thumb = None

    count = start_index if start_index > 0 else 1

    for i in range(start_index, len(links)):
        try:
            name_raw = links[i][0]
            url = links[i][1]

            safe_name = (
                name_raw.replace("/", "")
                .replace(":", "")
                .replace("|", "")
                .replace("*", "")
                .replace("@", "")
                .replace("#", "")
                .strip()
            )

            name = f"{str(count).zfill(3)}) {safe_name}"

            prog = await m.reply_text(
                f"**Downloading**\n\n**Name:** `{name}`"
            )

            if "pdf" in url:
                cmd = f'yt-dlp -o "{name}.pdf" "{url}"'
            else:
                cmd = (
                    f'yt-dlp -o "{name}.mp4" '
                    f'--no-keep-video --remux-video mkv "{url}"'
                )

            download_cmd = (
                f"{cmd} -R 25 --fragment-retries 25 "
                f"--external-downloader aria2c "
                f"--downloader-args 'aria2c: -x 16 -j 32'"
            )
            os.system(download_cmd)

            if os.path.isfile(f"{name}.mkv"):
                filename = f"{name}.mkv"
            elif os.path.isfile(f"{name}.mp4"):
                filename = f"{name}.mp4"
            elif os.path.isfile(f"{name}.pdf"):
                filename = f"{name}.pdf"
            else:
                await prog.edit("❌ Download failed")
                continue

            subprocess.run(
                f'ffmpeg -i "{filename}" -ss 00:01:00 -vframes 1 "{filename}.jpg"',
                shell=True,
            )

            await prog.delete(True)
            reply = await m.reply_text(f"Uploading `{name}`")

            caption = (
                f"**Title »** {safe_name}\n"
                f"**Caption »** {title_text}\n"
                f"**Index »** {str(count).zfill(3)}"
            )

            if filename.endswith(".pdf"):
                await m.reply_document(filename, caption=caption)
            else:
                dur = int(helper.duration(filename))
                await m.reply_video(
                    filename,
                    supports_streaming=True,
                    caption=caption,
                    duration=dur,
                    thumb=thumb or f"{filename}.jpg",
                    progress=progress_bar,
                    progress_args=(reply, time.time()),
                )

            count += 1
            os.remove(filename)
            if os.path.exists(f"{filename}.jpg"):
                os.remove(f"{filename}.jpg")
            await reply.delete(True)
            time.sleep(1)

        except FloodWait as fw:
            await time.sleep(fw.value)
        except Exception as e:
            await m.reply_text(f"❌ Error: {e}")
            continue

    await m.reply_text("✅ Done")
