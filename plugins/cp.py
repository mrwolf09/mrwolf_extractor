#  MIT License
#  Copyright (c) 2019-present Dan
#  Code edited By Cryptostark (fixed for Pyrogram v2)

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait

import requests
import os
import sys
import time
from subprocess import getstatusoutput


@Client.on_message(filters.command("cp"))
async def account_login(client: Client, m: Message):

    s = requests.Session()

    editable = await m.reply_text("**Send Token from ClassPlus App**")
    input1: Message = await client.listen(editable.chat.id)
    raw_text0 = input1.text

    headers = {
        "authority": "api.classplusapp.com",
        "accept": "application/json, text/plain, */*",
        "api-version": "28",
        "device-id": "516",
        "origin": "https://web.classplusapp.com",
        "referer": "https://web.classplusapp.com/",
        "region": "IN",
        "user-agent": "Mozilla/5.0",
        "x-access-token": raw_text0,
    }

    resp = s.get(
        "https://api.classplusapp.com/v2/batches/details?limit=20&offset=0&sortBy=createdAt",
        headers=headers,
    )

    if resp.status_code != 200:
        await editable.edit("❌ Login failed. Check token.")
        return

    b_data = resp.json()["data"]["totalBatches"]

    text = ""
    for data in b_data:
        aa = f"```{data['batchId']}``` - **{data['batchName']}**\n\n"
        if len(text + aa) > 4096:
            await m.reply_text(text)
            text = ""
        text += aa

    await editable.edit(f"**You have these batches:**\n\n{text}")

    editable1 = await m.reply_text("**Now send the Batch ID to Download**")
    input2: Message = await client.listen(editable.chat.id)
    course_id = input2.text

    resp = s.get(
        f"https://api.classplusapp.com/v2/course/content/get?courseId={course_id}",
        headers=headers,
    )

    folders = resp.json()["data"]["courseContent"]

    text = ""
    for data in folders:
        aa = f"```{data['id']}``` - **{data['name']}**\n\n"
        if len(text + aa) > 4096:
            await m.reply_text(text)
            text = ""
        text += aa

    await editable.edit(f"**Folders:**\n\n{text}")

    editable2 = await m.reply_text("**Now send the Folder ID to Download**")
    input3: Message = await client.listen(editable.chat.id)
    folder_id = input3.text

    resp = s.get(
        f"https://api.classplusapp.com/v2/course/content/get?courseId={course_id}&folderId={folder_id}",
        headers=headers,
    )

    videos = resp.json()["data"]["courseContent"]

    file_name = "classplus.txt"
    with open(file_name, "w") as f:
        for data in videos:
            title = data.get("name")
            desc = data.get("description", "")
            url = data.get("url", "")
            f.write(f"{title} - {desc}:{url}\n")

    await m.reply_document(file_name)
    await m.reply_text("✅ ClassPlus extraction completed.")
