#  MIT License
#  Copyright (c) 2019-present Dan
#  Code edited By Cryptostark (fixed for Pyrogram v2)

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait

import requests
import json
import time
import os
import re
import cloudscraper

ACCOUNT_ID = "6206459123001"
BCOV_POLICY = "BCpkADawqM1474MvKwYlMRZNBPoqkJY-UWm7zE1U769d5r5kqTjG0v8L-THXuVZtdIQJpfMPB37L_VJQxTKeNeLO2Eac_yMywEgyV9GjFDQ2LTiT4FEiHhKAUvdbx9ku6fGnQKSMB8J5uIDd"
BC_URL = f"https://edge.api.brightcove.com/playback/v1/accounts/{ACCOUNT_ID}/videos"
BC_HDR = {"BCOV-POLICY": BCOV_POLICY}


@Client.on_message(filters.command("cw"))
async def account_login(client: Client, m: Message):

    s = requests.Session()

    editable = await m.reply_text(
        "Send **ID*PASSWORD**\nOR send **TOKEN**"
    )
    input1: Message = await client.listen(editable.chat.id)
    raw_text = input1.text.strip()

    login_url = "https://elearn.crwilladmin.com/api/v1/login-other"
    headers = {
        "Host": "elearn.crwilladmin.com",
        "Appver": "1.55",
        "Apptype": "android",
        "Content-Type": "application/json; charset=UTF-8",
        "user-agent": "okhttp/5.0.0",
    }

    data = {
        "deviceType": "android",
        "deviceIMEI": "08750aa91d7387ab",
        "deviceModel": "Realme",
        "deviceVersion": "Android 11",
        "email": "",
        "password": "",
    }

    if "*" in raw_text:
        data["email"], data["password"] = raw_text.split("*", 1)
        r = s.post(login_url, headers=headers, json=data)
        if r.status_code != 200:
            await editable.edit("❌ Login failed")
            return
        token = r.json()["data"]["token"]
    else:
        token = raw_text

    batch_data = s.get(
        f"https://elearn.crwilladmin.com/api/v1/comp/my-batch?token={token}"
    ).json()["data"]["batchData"]

    txt = ""
    for b in batch_data:
        aa = f"```{b['id']}``` - **{b['batchName']}**\n\n"
        if len(txt + aa) > 4096:
            await m.reply_text(txt)
            txt = ""
        txt += aa

    await editable.edit(f"**Your Batches:**\n\n{txt}")

    ask = await m.reply_text("Send **Batch ID**")
    inp2: Message = await client.listen(ask.chat.id)
    batch_id = inp2.text

    topics = s.get(
        f"https://elearn.crwilladmin.com/api/v1/comp/batch-topic/{batch_id}?type=class&token={token}"
    ).json()["data"]["batch_topic"]

    ids = "&".join(str(t["id"]) for t in topics)
    await m.reply_text(f"Send Topic IDs:\n```{ids}```")

    inp3: Message = await client.listen(ask.chat.id)
    topic_ids = inp3.text.split("&")

    out_file = f"careerwill_{batch_id}.txt"
    open(out_file, "w").close()

    for tid in topic_ids:
        if not tid.strip():
            continue

        res = s.get(
            f"https://elearn.crwilladmin.com/api/v1/comp/batch-detail/{batch_id}?redirectBy=mybatch&topicId={tid}&token={token}"
        ).json()

        classes = res["data"]["class_list"]["classes"]
        classes.reverse()

        for c in classes:
            lesson = c["lessonName"].replace("/", "_")
            vid_id = c["lessonUrl"][0]["link"]

            if vid_id.startswith(("62", "63")):
                vdata = s.get(f"{BC_URL}/{vid_id}", headers=BC_HDR).json()
                src = vdata["sources"][5]["src"]
                tok = s.get(
                    f"https://elearn.crwilladmin.com/api/v1/livestreamToken?type=brightcove&vid={c['id']}&token={token}"
                ).json()["data"]["token"]
                link = f"{src}&bcov_auth={tok}"
            else:
                link = f"https://www.youtube.com/embed/{vid_id}"

            with open(out_file, "a") as f:
                f.write(f"{lesson}:{link}\n")

    await m.reply_document(out_file)

    ask_notes = await m.reply_text("Download notes? **y / n**")
    inp4: Message = await client.listen(ask_notes.chat.id)

    if inp4.text.lower() == "y":
        notes = s.get(
            f"https://elearn.crwilladmin.com/api/v1/comp/batch-notes/{batch_id}?token={token}"
        ).json()["data"]["notesDetails"]

        for n in notes:
            with open(out_file, "a") as f:
                f.write(f"{n['docTitle']}:{n['docUrl']}\n")

        await m.reply_document(out_file)

    await m.reply_text("✅ Done")
