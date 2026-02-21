import os
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message
from pyromod import listen

# ================= CONFIG =================
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

ALLOWED_USERS = [123456789]  # <-- अपनी Telegram ID डालो

bot = Client(
    "yt_pdf_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ================= START =================
@bot.on_message(filters.command("start"))
async def start(_, m: Message):
    await m.reply_text("🤖 Bot is alive.\nPrivate command required.")

# ================= PRIVATE COMMAND =================
@bot.on_message(filters.command("jaanu"))
async def jaanu(bot: Client, m: Message):

    if m.from_user.id not in ALLOWED_USERS:
        return

    # TXT FILE
    q1 = await bot.ask(m.chat.id, "📄 TXT file upload karo")
    txt_path = await q1.download()
    await q1.delete()
    await q1.request.delete()

    # BATCH NAME
    q2 = await bot.ask(m.chat.id, "📚 Batch / Course Name likho")
    batch = q2.text
    await q2.delete()
    await q2.request.delete()

    # QUALITY
    q3 = await bot.ask(m.chat.id, "🎞 Video Quality (360 / 480 / 720 / 1080)")
    quality = q3.text
    await q3.delete()
    await q3.request.delete()

    # CREDIT
    q4 = await bot.ask(m.chat.id, "✍️ Credit Name")
    credit = q4.text
    await q4.delete()
    await q4.request.delete()

    # THUMB
    q5 = await bot.ask(m.chat.id, "🖼 Thumbnail bhejo ya `no` likho")
    if q5.text and q5.text.lower() == "no":
        thumb = None
        await q5.delete()
        await q5.request.delete()
    else:
        thumb = await q5.download()
        await q5.delete()
        await q5.request.delete()

    # READ TXT
    with open(txt_path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    count = 1

    for line in lines:
        if "|" not in line:
            continue

        title, link = line.split("|", 1)
        title = title.strip()
        link = link.strip()

        name = f"{batch} - {count} - {title}"

        # ========== PDF ==========
        if link.lower().endswith(".pdf"):
            os.system(f'wget "{link}" -O "{name}.pdf"')
            await bot.send_document(
                m.chat.id,
                document=f"{name}.pdf",
                caption=f"📘 {name}\n\n© {credit}"
            )
            os.remove(f"{name}.pdf")
            count += 1
            continue

        # ========== YOUTUBE ==========
        if "youtube.com" in link or "youtu.be" in link:
            ydl_opts = {
                "format": f"b[height<={quality}]/bv*[height<={quality}]+ba/b",
                "outtmpl": f"{name}.mp4",
                "quiet": True
            }

            status = await m.reply_text(f"⬇️ Downloading\n{name}")

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([link])

                await bot.send_video(
                    m.chat.id,
                    video=f"{name}.mp4",
                    caption=f"🎬 {name}\n🎞 {quality}p\n\n© {credit}",
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

bot.run()
