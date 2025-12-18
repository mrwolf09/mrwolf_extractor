#  MIT License
#  Fixed for Pyrogram v2 – txt handler (TeachX based institutes)
#  Cleaned imports, correct handler, no silent failures

import requests
import json
from pyrogram import Client, filters
from pyrogram.types import Message
from pyromod import listen
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode
import os


@Client.on_message(filters.command("txt"))
async def txt_handler(client: Client, m: Message):

    await m.reply_text(
        "**Send Institute API host**\n\n"
        "`rozgarapinew.teachx.in`\n"
        "`lastexamapi.teachx.in`\n"
        "`missionapi.appx.co.in`"
    )

    inst_msg: Message = await client.listen(m.chat.id)
    INS = inst_msg.text.strip()
    await inst_msg.delete()

    ask = await m.reply_text("Send **ID*Password**")
    cred: Message = await client.listen(ask.chat.id)
    email, password = cred.text.split("*", 1)
    await cred.delete()

    session = requests.Session()

    login_url = f"https://{INS}/post/login"
    headers = {
        "Client-Service": "Appx",
        "Auth-Key": "appxapi",
        "User-ID": "-2",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "okhttp/4.9.1",
    }

    login = session.post(
        login_url,
        data={"email": email, "password": password},
        headers=headers,
    ).json()

    userid = login["data"]["userid"]
    token = login["data"]["token"]

    auth = {
        "Client-Service": "Appx",
        "Auth-Key": "appxapi",
        "User-ID": userid,
        "Authorization": token,
        "User-Agent": "okhttp/4.9.1",
        "Host": INS,
    }

    await m.reply_text("✅ **Login Successful**")

    courses = session.get(
        f"https://{INS}/get/mycourse?userid={userid}",
        headers=auth,
    ).json()["data"]

    txt = ""
    for c in courses:
        txt += f"```{c['id']}``` - **{c['course_name']}**\n\n"

    await m.reply_text(f"**Your Batches**\n\n{txt}")

    bid_msg = await client.listen(m.chat.id)
    batch_id = bid_msg.text
    await bid_msg.delete()

    subjects = session.get(
        f"https://{INS}/get/allsubjectfrmlivecourseclass?courseid={batch_id}",
        headers=auth,
    ).json()["data"]

    subject_ids = ""
    for s in subjects:
        subject_ids += f"{s['subjectid']}&"

    await m.reply_text(
        f"Send **Subject IDs**\n\n```{subject_ids}```"
    )

    sub_msg = await client.listen(m.chat.id)
    subject_id = sub_msg.text
    await sub_msg.delete()

    topics = session.get(
        f"https://{INS}/get/alltopicfrmlivecourseclass?courseid={batch_id}&subjectid={subject_id}",
        headers=auth,
    ).json()["data"]

    topic_ids = ""
    for t in topics:
        topic_ids += f"{t['topicid']}&"

    await m.reply_text(
        f"Send **Topic IDs**\n\n```{topic_ids}```"
    )

    topic_msg = await client.listen(m.chat.id)
    topic_list = topic_msg.text.split("&")
    await topic_msg.delete()

    filename = "TeachX-TXT.txt"

    for tid in topic_list:
        if not tid.strip():
            continue

        if INS == "missionapi.appx.co.in":
            url = f"https://{INS}/get/livecourseclassbycoursesubtopconceptapiv3?topicid={tid}&start=-1&conceptid=4&courseid={batch_id}&subjectid={subject_id}"
        else:
            url = f"https://{INS}/get/livecourseclassbycoursesubtopconceptapiv3?topicid={tid}&start=-1&conceptid=1&courseid={batch_id}&subjectid={subject_id}"

        data = session.get(url, headers=auth).json()["data"]

        for item in data:
            title = item["Title"].replace(":", "").replace("&", "").strip()

            enc = item["download_link"] or item["pdf_link"]
            if not enc:
                continue

            key = b"638udh3829162018"
            iv = b"fedcba9876543210"

            raw = bytearray.fromhex(b64decode(enc.encode()).hex())
            cipher = AES.new(key, AES.MODE_CBC, iv)
            link = unpad(cipher.decrypt(raw), AES.block_size).decode()

            with open(filename, "a") as f:
                f.write(f"{title}:{link}\n")

    await m.reply_document(filename)
    await m.reply_text("✅ **Done**")
    os.remove(filename)
