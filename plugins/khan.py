#  MIT License
#  Fixed for Pyrogram v2

import requests
import json
from pyrogram import Client, filters
from pyrogram.types import Message
from pyromod import listen


@Client.on_message(filters.command("khan"))
async def khan_handler(client: Client, m: Message):

    editable = await m.reply_text(
        "Send **ID & Password** like this:\n\n`ID*Password`"
    )

    input1: Message = await client.listen(editable.chat.id)
    raw_text = input1.text
    await input1.delete()

    username, password = raw_text.split("*", 1)

    login_url = "https://api.penpencil.xyz/v1/oauth/token"

    headers = {
        "authorization": "Bearer c5c5e9c5721a1c4e322250fb31825b62f9715a4572318de90cfc93b02a8a8a75",
        "client-id": "5f439b64d553cc02d283e1b4",
        "client-version": "21.0",
        "user-agent": "Android",
        "client-type": "MOBILE",
        "content-type": "application/json; charset=UTF-8",
    }

    payload = {
        "username": username,
        "password": password,
        "organizationId": "5f439b64d553cc02d283e1b4",
        "client_id": "system-admin",
        "client_secret": "KjPXuAVfC5xbmgreETNMaL7z",
        "grant_type": "password",
    }

    s = requests.Session()
    r = s.post(login_url, headers=headers, json=payload)

    if r.status_code != 200:
        await editable.edit("❌ Login failed")
        return

    token = r.json()["data"]["access_token"]
    await editable.edit("✅ **Login Successful**")

    headers["authorization"] = f"Bearer {token}"

    batches = s.get(
        "https://api.penpencil.xyz/v3/batches/my-batches",
        headers=headers,
        params={
            "mode": "1",
            "organisationId": "5f439b64d553cc02d283e1b4",
            "page": "1",
        },
    ).json()["data"]

    text = ""
    for b in batches:
        text += f"```{b['_id']}``` - **{b['name']}**\n\n"

    await editable.edit(f"**Your Batches:**\n\n{text}")

    ask = await m.reply_text("Send **Batch ID**")
    batch_msg = await client.listen(ask.chat.id)
    batch_id = batch_msg.text
    await batch_msg.delete()

    details = s.get(
        f"https://api.penpencil.xyz/v3/batches/{batch_id}/details",
        headers=headers,
    ).json()["data"]

    batch_name = details["name"]
    subjects = details["subjects"]

    ids = ""
    out = ""
    for s1 in subjects:
        ids += f"{s1['_id']}&"
        out += f"```{s1['_id']}``` - **{s1['name']}**\n\n"

    ask2 = await m.reply_text(f"Send **Subject IDs**\n\n```{ids}```")
    sub_msg = await client.listen(ask2.chat.id)
    subject_ids = sub_msg.text.split("&")
    await sub_msg.delete()

    filename = f"KhanSir-{batch_name}.txt"

    for sid in subject_ids:
        if not sid.strip():
            continue

        page = 1
        while True:
            r = s.get(
                f"https://api.penpencil.xyz/v2/batches/{batch_id}/subject/{sid}/contents",
                headers=headers,
                params={"page": page, "contentType": "videos"},
            ).json()

            data = r.get("data", [])
            if not data:
                break

            for d in data:
                try:
                    title = d["topic"]
                    url = (
                        d["url"]
                        .replace("d1d34p8vz63oiq", "d3nzo6itypaz07")
                        .replace("mpd", "m3u8")
                    )
                    with open(filename, "a") as f:
                        f.write(f"{title}:{url}\n")
                except Exception:
                    pass

            page += 1

    await m.reply_document(filename)
    await m.reply_text("✅ **Done**")
