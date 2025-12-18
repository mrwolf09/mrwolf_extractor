from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait

import requests
import time
import os
import re
from subprocess import getstatusoutput

# ================================
# PW COMMAND
# ================================

@Client.on_message(filters.command("pw"))
async def account_login(client: Client, m: Message):

    editable = await m.reply_text(
        "Send **Auth code** in this manner otherwise bot will not respond.\n\n"
        "Send like this:-  **AUTH CODE**"
    )

    input1: Message = await client.listen(editable.chat.id)
    raw_text1 = input1.text

    headers = {
        "Host": "api.penpencil.xyz",
        "authorization": f"Bearer {raw_text1}",
        "client-id": "5eb393ee95fab7468a79d189",
        "client-version": "12.84",
        "user-agent": "Android",
        "randomid": "e4307177362e86f1",
        "client-type": "MOBILE",
        "device-meta": "{APP_VERSION:12.84,DEVICE_MAKE:Asus,DEVICE_MODEL:ASUS_X00TD,OS_VERSION:6,PACKAGE_NAME:xyz.penpencil.physicswalb}",
        "content-type": "application/json; charset=UTF-8",
    }

    params = {
        "mode": "1",
        "filter": "false",
        "exam": "",
        "amount": "",
        "organisationId": "5eb393ee95fab7468a79d189",
        "classes": "",
        "limit": "20",
        "page": "1",
        "programId": "",
        "ut": "1652675230446",
    }

    await editable.edit("**You have these Batches :-**\n\n`Batch Name : Batch ID`")

    response = requests.get(
        "https://api.penpencil.xyz/v3/batches/my-batches",
        params=params,
        headers=headers,
    ).json()["data"]

    for data in response:
        await m.reply_text(f"`{data['name']}` : `{data['_id']}`")

    editable1 = await m.reply_text("**Now send the Batch ID to Download**")
    input3: Message = await client.listen(editable.chat.id)
    batch_id = input3.text

    response2 = requests.get(
        f"https://api.penpencil.xyz/v3/batches/{batch_id}/details",
        headers=headers,
    ).json()["data"]["subjects"]

    ids = ""
    for data in response2:
        ids += f"{data['_id']}&"

    await m.reply_text(f"**Enter this to download full batch:**\n```{ids}```")

    input4: Message = await client.listen(editable.chat.id)
    subject_ids = input4.text.split("&")

    await m.reply_text("**Enter resolution**")
    input5: Message = await client.listen(editable.chat.id)
    resolution = input5.text

    editable4 = await m.reply_text(
        "Send **Thumbnail URL** or type **no**"
    )
    input6: Message = await client.listen(editable.chat.id)
    thumb = input6.text

    if thumb.startswith("http"):
        getstatusoutput(f"wget '{thumb}' -O thumb.jpg")
        thumb = "thumb.jpg"
    else:
        thumb = None

    batch_name = "PW_BATCH"

    for subject in subject_ids:
        if not subject.strip():
            continue

        for page in range(1, 5):
            params_pg = {
                "page": str(page),
                "tag": "",
                "contentType": "exercises-notes-videos",
                "ut": "",
            }

            data_list = requests.get(
                f"https://api.penpencil.xyz/v2/batches/{batch_id}/subject/{subject}/contents",
                params=params_pg,
                headers=headers,
            ).json().get("data", [])

            for data in data_list:
                title = data["topic"]
                url = (
                    data["url"]
                    .replace("d1d34p8vz63oiq", "d3nzo6itypaz07")
                    .replace("mpd", "m3u8")
                )

                with open(f"{batch_name}.txt", "a") as f:
                    f.write(f"{title}:{url}\n")

    await m.reply_document(f"{batch_name}.txt")
