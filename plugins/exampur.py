#  MIT License
#  Copyright (c) 2019-present Dan
#  Fixed for Pyrogram v2

from pyrogram import Client, filters
from pyrogram.types import Message
import requests
import json
import cloudscraper
import urllib.parse
import os


@Client.on_message(filters.command("exampur"))
async def account_login(client: Client, m: Message):

    editable = await m.reply_text(
        "Send **ID*PASSWORD**\nExample:\n`email@gmail.com*password`"
    )

    input1: Message = await client.listen(editable.chat.id)
    raw = input1.text
    await input1.delete(True)

    email, password = raw.split("*", 1)

    login_url = "https://auth.exampurcache.xyz/auth/login"
    payload = {
        "phone_ext": "91",
        "phone": "",
        "email": email,
        "password": password,
    }

    scraper = cloudscraper.create_scraper()
    res = scraper.post(login_url, json=payload).json()

    token = res["data"]["authToken"]

    headers = {
        "appauthtoken": token,
        "User-Agent": "Dart/2.15(dart:io)",
    }

    await editable.edit("✅ **Login Successful**")

    courses = requests.get(
        "https://auth.exampurcache.xyz/mycourses", headers=headers
    ).json()["data"]

    text = "**BATCH ID - BATCH NAME**\n\n"
    for c in courses:
        text += f"`{c['_id']}` - **{c['title']}**\n"

    await m.reply_text(text)

    ask = await m.reply_text("Send **Batch ID**")
    batch_id = (await client.listen(ask.chat.id)).text

    subjects = requests.get(
        f"https://auth.exampurcache.xyz/course_subject/{batch_id}",
        headers=headers,
    ).json()["data"]

    subject_ids = "&".join(s["_id"] for s in subjects)

    await m.reply_text(
        f"Send Subject IDs like `id1&id2`\n\nFull batch:\n```{subject_ids}```"
    )

    ask2 = await m.reply_text("Send **Subject IDs**")
    selected = (await client.listen(ask2.chat.id)).text

    file_name = "Exampur.txt"
    open(file_name, "w").close()

    for sid in selected.split("&"):
        chapters = requests.get(
            f"https://auth.exampurcache.xyz/course_material/chapter/{sid}/{batch_id}",
            headers=headers,
        ).json()["data"]

        for ch in chapters:
            enc = urllib.parse.quote(ch, safe="")
            material = requests.get(
                f"https://auth.exampurcache.xyz/course_material/material/{sid}/{batch_id}/{enc}",
                headers=headers,
            ).json()["data"]

            for v in material:
                title = v["title"]
                link = v["video_link"]
                with open(file_name, "a") as f:
                    f.write(f"{title}:{link}\n")

    await m.reply_document(file_name)
    os.remove(file_name)

    await m.reply_text("✅ Done")
