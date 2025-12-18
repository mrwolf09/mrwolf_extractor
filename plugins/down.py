#  MIT License
#  Copyright (c) 2019-present Dan
#  Code edited By Cryptostark (fixed for Pyrogram v2)

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait

import requests
import time
import os
import subprocess
from subprocess import getstatusoutput

import helper
from p_bar import progress_bar


@Client.on_message(filters.command("down"))
async def account_login(client: Client, m: Message):

    editable = await m.reply_text("**Send Text file containing URLs**")
    input_file: Message = await client.listen(editable.chat.id)
    file_path = await input_file.download()
    await input_file.delete(True)

    try:
        with open(file_path, "r") as f:
            lines = f.read().splitlines()
        links = [i.split(":", 1) for i in lines if ":" in i]
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

    editable = await m.reply_text("**Enter Batch Name**")
    input_batch: Message = await client.listen(editable.chat.id)
    batch_name = input_batch.text

    editable = await m.reply_text("**Downloaded By**")
    input_by: Message = await client.listen(editable.chat.id)
    downloaded_by = input_by.text

    editable = await m.reply_text("**Enter resolution**")
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

    editable = await m.reply_text("**Enter number of threads**")
    input_thr: Message = await client.listen(editable.chat.id)
    threads = int(input_thr.text)

    count = start_index + 1 if start_index >= 0 else 1

    cmd_list = []

    for i in range(start_index, len(links)):
        try:
            name_raw, url = links[i]
            name = (
                name_raw.replace("/", "")
                .replace(":", "")
                .replace("|", "")
                .replace("*", "")
                .replace("@", "")
                .replace("#", "")
                .strip()
            )
        except:
            continue

        if "youtu" in url:
            cmd_list.append(
                ["yt-dlp", "-S", f"height:{resolution},ext:mp4", "-N", "100", "-o", f"{name}.mp4", url]
            )
        elif url.endswith(".pdf"):
            cmd_list.append(["yt-dlp", "-o", f"{name}.pdf", url])
        else:
            cmd_list.append(
                ["yt-dlp", "-S", f"height:{resolution},ext:mp4", "-N", "100", "-o", f"{name}.mp4", url]
            )

    for i in range(0, len(cmd_list), threads):
        batch = cmd_list[i:i + threads]
        prog = await m.reply_text("⬇️ Downloading...")

        try:
            helper.pull_run(threads, batch)
        except Exception as e:
            await prog.edit(f"❌ Download error: {e}")
            continue

        await prog.delete(True)

        for cmd in batch:
            filename = cmd[-2] if cmd[-2].endswith((".mp4", ".pdf")) else cmd[-1]

            if not os.path.exists(filename):
                continue

            if filename.endswith(".pdf"):
                caption = (
                    f"{str(count).zfill(2)}. {filename}\n\n"
                    f"**Batch »** {batch_name}\n"
                    f"**Downloaded By »** {downloaded_by}"
                )
                await m.reply_document(filename, caption=caption)
                os.remove(filename)
                count += 1
                continue

            reply = await m.reply_text("⬆️ Uploading video...")
            subprocess.run(
                f'ffmpeg -i "{filename}" -ss 00:01:00 -y -vframes 1 "{filename}.jpg"',
                shell=True,
            )

            dur = int(helper.duration(filename))
            caption = (
                f"{str(count).zfill(2)}. {filename} - {resolution}p\n\n"
                f"**Batch »** {batch_name}\n"
                f"**Downloaded By »** {downloaded_by}"
            )

            await m.reply_video(
                filename,
                caption=caption,
                supports_streaming=True,
                duration=dur,
                thumb=thumb or f"{filename}.jpg",
                progress=progress_bar,
                progress_args=(reply, time.time()),
            )

            os.remove(filename)
            if os.path.exists(f"{filename}.jpg"):
                os.remove(f"{filename}.jpg")

            await reply.delete(True)
            count += 1

    await m.reply_text("✅ Done")
