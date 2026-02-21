# ================== IMPORTS ==================
import os
import asyncio
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message
from pyromod import listen

# ================== BOT CONFIG ==================
import os

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

bot = Client(
    "yt_pdf_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ================== START COMMAND (PUBLIC) ==================
@bot.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply_text(
        "🤖 Bot is alive.\n\nPrivate command required."
    )

# ================== PRIVATE COMMAND ==================
@bot.on_message(filters.command("jaanu"))
async def jaanu_handler(bot: Client, m: Message):

    # TXT FILE
    txt = await bot.ask(m.chat.id, "📄 TXT file upload karo")
    txt_path = await txt.download()

    # BATCH NAME
    batch = await bot.ask(m.chat.id, "📚 Batch / Course Name likho")
    batch_name = batch.text

    # QUALITY
    qual = await bot.ask(m.chat.id, "🎞 Video Quality (360 / 480 / 720 / 1080)")
    quality = qual.text

    # CREDIT
    credit = await bot.ask(m.chat.id, "✍️ Credit Name")
    credit_name = credit.text

    # THUMB
    thumb_msg = await bot.ask(m.chat.id, "🖼 Thumbnail bhejo ya `no` likho")
    if thumb_msg.text.lower() == "no":
        thumb = None
    else:
        thumb = await thumb_msg.download()

    # ================== PROCESS LINKS ==================
    with open(txt_path, "r", encoding="utf-8") as f:
        links = f.read().splitlines()

    count = 1

    for url in links:
        name = f"{batch_name} - {count}"

        # ---------- PDF ----------
        if url.lower().endswith(".pdf"):
            try:
                os.system(f'wget "{url}" -O "{name}.pdf"')
                caption_pdf = f"📘 {name}\n\n© {credit_name}"
                await bot.send_document(
                    m.chat.id,
                    document=f"{name}.pdf",
                    caption=caption_pdf
                )
                os.remove(f"{name}.pdf")
                count += 1
                continue
            except:
                continue

        # ---------- YOUTUBE ----------
        if "youtube.com" in url or "youtu.be" in url:
            ydl_opts = {
                "format": f"b[height<={quality}]/bv*[height<={quality}]+ba/b",
                "outtmpl": f"{name}.mp4",
                "quiet": True
            }

            status = await m.reply_text(f"⬇️ Downloading\n{name}")

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                caption_vid = (
                    f"🎬 {name}\n"
                    f"🎞 Quality: {quality}p\n\n"
                    f"© {credit_name}"
                )

                await bot.send_video(
                    m.chat.id,
                    video=f"{name}.mp4",
                    caption=caption_vid,
                    thumb=thumb
                )

                os.remove(f"{name}.mp4")
                await status.delete()
                count += 1

            except:
                await status.edit("❌ Failed")
                continue

    os.remove(txt_path)

    await m.reply_text("✅ All tasks completed")

# ================== RUN ==================
bot.run()
