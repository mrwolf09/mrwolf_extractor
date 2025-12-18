#  MIT License
#  Fixed for Pyrogram v2

import requests
import json
import cloudscraper
from pyrogram import Client, filters
from pyrogram.types import Message
from pyromod import listen
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode
import os


@Client.on_message(filters.command("ocean"))
async def ocean_handler(client: Client, m: Message):

    editable = await m.reply_text(
        "Send **ID & Password** like this:\n\n`ID*Password`"
    )

    input1: Message = await client.listen(editable.chat.id)
    raw_text = input1.text
    await input1.delete()

    email, password = raw_text.split("*", 1)

    login_url = "https://oceangurukulsapi.classx.co.in/post/userLogin"
    headers = {
        "Auth-Key": "appxapi",
        "User-Id": "-2",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "okhttp/4.9.1",
    }

    data = {"email": email, "password": password}

    scraper = cloudscraper.create_scraper()
    res = scraper.post(login_url, data=data, headers=headers).json()

    userid = res["data"]["userid"]
    token = res["data"]["token"]

    auth_headers = {
        "Host": "oceangurukulsapi.classx.co.in",
        "Client-Service": "Appx",
        "Auth-Key": "appxapi",
        "User-Id": userid,
        "Authorization": token,
    }

    await editable.edit("✅ **Login Successful**")

    courses = requests.get(
        f"https://oceangurukulsapi.classx.co.in/get/mycourse?userid={userid}",
        headers=auth_headers,
    ).json()["data"]

    text = ""
    for c in courses:
        text += f"```{c['id']}``` - **{c['course_name']}**\n\n"

    await editable.edit(f"**Your Batches:**\n\n{text}")

    ask = await m.reply_text("Send **Batch ID**")
    batch_msg = await client.listen(ask.chat.id)
    batch_id = batch_msg.text
    await batch_msg.delete()

    subjects = requests.get(
        f"https://oceangurukulsapi.classx.co.in/get/allsubjectfrmlivecourseclass?courseid={batch_id}",
        headers=auth_headers,
    ).json()["data"]

    subject_ids = ""
    for s in subjects:
        subject_ids += f"{s['id']}&"

    ask2 = await m.reply_text(f"Send **Subject ID**\n\n```{subject_ids}```")
    sub_msg = await client.listen(ask2.chat.id)
    subject_id = sub_msg.text
    await sub_msg.delete()

    topics = requests.get(
        f"https://oceangurukulsapi.classx.co.in/get/alltopicfrmlivecourseclass?courseid={batch_id}&subjectid={subject_id}",
        headers=auth_headers,
    ).json()["data"]

    topic_ids = ""
    for t in topics:
        topic_ids += f"{t['topicid']}&"

    ask3 = await m.reply_text(f"Send **Topic IDs**\n\n```{topic_ids}```")
    topic_msg = await client.listen(ask3.chat.id)
    selected_topics = topic_msg.text.split("&")
    await topic_msg.delete()

    filename = "Ocean-Gurukul.txt"

    for tid in selected_topics:
        if not tid.strip():
            continue

        res = requests.get(
            "https://oceangurukulsapi.classx.co.in/get/livecourseclassbycoursesubtopconceptapiv3",
            params={
                "topicid": tid,
                "start": -1,
                "conceptid": 1,
                "courseid": batch_id,
                "subjectid": subject_id,
            },
            headers=auth_headers,
        ).json()

        for item in res["data"]:
            title = item["Title"]
            enc = item["download_link"] or item["pdf_link"]

            key = b"638udh3829162018"
            iv = b"fedcba9876543210"

            cipher = AES.new(key, AES.MODE_CBC, iv)
            raw = unpad(cipher.decrypt(bytearray.fromhex(b64decode(enc).hex())), 16)
            link = raw.decode("utf-8")

            with open(filename, "a") as f:
                f.write(f"{title}:{link}\n")

    await m.reply_document(filename)
    await m.reply_text("✅ **Done**")

    os.remove(filename)
