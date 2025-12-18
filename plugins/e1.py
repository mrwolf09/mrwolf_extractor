#  MIT License
#  Copyright (c) 2019-present Dan
#  Fixed for Pyrogram v2

from pyrogram import Client, filters
from pyrogram.types import Message

import requests
import json
import cloudscraper
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode


@Client.on_message(filters.command("e1"))
async def account_login(client: Client, m: Message):

    editable = await m.reply_text(
        "Send **ID*PASSWORD**\nExample:\n`email@gmail.com*password`"
    )

    input1: Message = await client.listen(editable.chat.id)
    raw = input1.text
    await input1.delete(True)

    email, password = raw.split("*", 1)

    login_url = "https://e1coachingcenterapi.classx.co.in/post/userLogin"
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

    hdr = {
        "Auth-Key": "appxapi",
        "Client-Service": "Appx",
        "User-Id": userid,
        "Authorization": token,
    }

    await editable.edit("✅ **Login Successful**")

    course_res = requests.get(
        f"https://e1coachingcenterapi.classx.co.in/get/mycourse?userid={userid}",
        headers=hdr,
    ).json()

    courses = course_res["data"]

    text = "**COURSE ID - COURSE NAME**\n\n"
    for c in courses:
        text += f"`{c['id']}` - **{c['course_name']}**\n"

    await m.reply_text(text)

    ask = await m.reply_text("Send **Course ID**")
    course_id = (await client.listen(ask.chat.id)).text

    subj_res = requests.get(
        f"https://e1coachingcenterapi.classx.co.in/get/allsubjectfrmlivecourseclass?courseid={course_id}",
        headers=hdr,
    ).json()

    subjects = subj_res["data"]
    subj_text = "**SUBJECT ID - SUBJECT NAME**\n\n"
    for s in subjects:
        subj_text += f"`{s['subjectid']}` - **{s['subject_name']}**\n"

    await m.reply_text(subj_text)

    ask2 = await m.reply_text("Send **Subject ID**")
    subject_id = (await client.listen(ask2.chat.id)).text

    topic_res = requests.get(
        f"https://e1coachingcenterapi.classx.co.in/get/alltopicfrmlivecourseclass?courseid={course_id}&subjectid={subject_id}",
        headers=hdr,
    ).json()

    topics = topic_res["data"]
    topic_ids = "&".join(str(t["topicid"]) for t in topics)

    topic_text = "**TOPIC ID - TOPIC NAME**\n\n"
    for t in topics:
        topic_text += f"`{t['topicid']}` - **{t['topic_name']}**\n"

    await m.reply_text(topic_text)

    ask3 = await m.reply_text(
        f"Send Topic IDs like `1&2&3`\n\nFull batch:\n```{topic_ids}```"
    )
    selected = (await client.listen(ask3.chat.id)).text

    mm = "E1-Coaching-Center.txt"
    open(mm, "w").close()

    for tid in selected.split("&"):
        res = requests.get(
            f"https://e1coachingcenterapi.classx.co.in/get/livecourseclassbycoursesubtopconceptapiv3"
            f"?topicid={tid}&start=-1&conceptid=1&courseid={course_id}&subjectid={subject_id}",
            headers=hdr,
        ).json()

        for item in res["data"]:
            title = item["Title"]
            enc = item["embed_url"] or item["pdf_link"]

            key = b"638udh3829162018"
            iv = b"fedcba9876543210"

            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted = unpad(cipher.decrypt(b64decode(enc)), AES.block_size).decode()

            with open(mm, "a") as f:
                f.write(f"{title}:{decrypted}\n")

    await m.reply_document(mm)
    os.remove(mm)

    await m.reply_text("✅ Done")
