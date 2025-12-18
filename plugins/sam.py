#  MIT License
#  Fixed for Pyrogram v2 (no silent handlers, proper Client usage)

import requests
import json
import cloudscraper
from pyrogram import Client, filters
from pyrogram.types import Message
from pyromod import listen
import os


@Client.on_message(filters.command("samyak"))
async def samyak_handler(client: Client, m: Message):

    editable = await m.reply_text(
        "Send **ID & Password** like this:\n\n`ID*Password`"
    )

    login_msg: Message = await client.listen(editable.chat.id)
    raw = login_msg.text
    await login_msg.delete()

    email, password = raw.split("*", 1)

    session = requests.Session()

    login_url = "https://samyak.teachx.in/pages/login2"
    headers = {
        "Auth-Key": "appxapi",
        "User-Id": "-2",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "okhttp/4.9.1",
    }

    res = session.post(
        login_url,
        data={"email": email, "password": password},
        headers=headers,
    ).json()

    userid = res["data"]["userid"]
    token = res["data"]["token"]

    auth_headers = {
        "Authorization": token,
        "User-ID": userid,
        "auth-key": "appxapi",
        "client-service": "Appx",
        "User-Agent": "Mozilla/5.0",
    }

    await editable.edit("✅ **Login Successful**")

    courses = session.get(
        f"https://samyakapi.teachx.in/get/mycourseweb?userid={userid}",
        headers=auth_headers,
    ).json()["data"]

    txt = ""
    for c in courses:
        txt += f"```{c['id']}``` - **{c['course_name']}**\n\n"

    await editable.edit(f"**Your Batches:**\n\n{txt}")

    ask = await m.reply_text("Send **Batch ID**")
    batch_msg = await client.listen(ask.chat.id)
    batch_id = batch_msg.text
    await batch_msg.delete()

    subjects = session.get(
        f"https://samyakapi.teachx.in/get/allsubjectfrmlivecourseclass?courseid={batch_id}",
        headers=auth_headers,
    ).json()["data"]

    subject_ids = ""
    subject_text = ""
    for s in subjects:
        subject_ids += f"{s['subjectid']}&"
        subject_text += f"```{s['subjectid']}``` - **{s['subject_name']}**\n\n"

    await m.reply_text(subject_text)

    ask2 = await m.reply_text(
        f"Send **Subject IDs**\n\n```{subject_ids}```"
    )
    sub_msg = await client.listen(ask2.chat.id)
    selected_subjects = sub_msg.text.split("&")
    await sub_msg.delete()

    filename = "Samyak-IAS.txt"

    for subject_id in selected_subjects:
        if not subject_id.strip():
            continue

        topics = session.get(
            f"https://samyakapi.teachx.in/get/alltopicfrmlivecourseclass?courseid={batch_id}&subjectid={subject_id}",
            headers=auth_headers,
        ).json()["data"]

        for topic in topics:
            tid = topic["topicid"]
            tname = topic["topic_name"]

            data = session.get(
                f"https://samyakapi.teachx.in/get/livecourseclassbycoursesubtopconceptapiv3",
                params={
                    "courseid": batch_id,
                    "subjectid": subject_id,
                    "topicid": tid,
                    "start": -1,
                },
                headers=auth_headers,
            ).json()["data"]

            for item in data:
                title = item["Title"]

                if item["download_link"]:
                    dec = session.post(
                        "https://samyak.teachx.in/pages/decrypt",
                        data={"link": item["download_link"]},
                        headers=headers,
                    ).text
                    url = f"https://cdn.jwplayer.com/manifests/{dec}"
                    with open(filename, "a") as f:
                        f.write(f"{title}:{url}\n")

                if item["pdf_link"]:
                    pdf = session.post(
                        "https://samyak.teachx.in/pages/decrypt",
                        data={"link": item["pdf_link"]},
                        headers=headers,
                    ).text
                    with open(filename, "a") as f:
                        f.write(f"{title}:{pdf}\n")

    await m.reply_document(filename)
    await m.reply_text("✅ **Done**")

    os.remove(filename)
