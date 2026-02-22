import os
import re
import time
import asyncio
import requests
import yt_dlp
import cloudscraper
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyromod import listen

# Env vars Render के लिए
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MY_USER_ID = int(os.getenv("MY_USER_ID", "0"))  # अपना ID डालो
PORT = int(os.getenv("PORT", 8080))

bot = Client("sk08_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("sk08") & filters.private)
async def sk08_handler(client, m: Message):
    if m.from_user.id != MY_USER_ID:
        return await m.reply("❌ सिर्फ ओनर के लिए!")
    
    await m.reply("🔥 `/sk08` एक्टिव! अब 3 चीजें भेजो:
1️⃣ स्टार्ट नंबर (1)
2️⃣ TXT फाइल (Chapter
Link)
3️⃣ थंब URL (no)")
    
    # 1. Start number
    inp1 = await bot.listen(m.chat.id)
    try: start_num = int(inp1.text or 1)
    except: start_num = 1
    await inp1.delete(True)
    
    # 2. TXT file
    await m.reply("📄 TXT भेजो!")
    txt_file = await bot.listen(m.chat.id)
    await txt_file.download("links.txt")
    await txt_file.delete(True)
    
    with open("links.txt", "r") as f:
        content = f.read()
    os.remove("links.txt")
    links = []
    for line in content.splitlines():
        if '
' in line:
            parts = line.split('
', 1)
            chapter = parts[0].strip()
            link = parts[1].strip()
            links.append((chapter, link))
    
    # 3. Thumb
    await m.reply("🖼️ थंब URL (jpg) या 'no'")
    thumb_inp = await bot.listen(m.chat.id)
    thumb = thumb_inp.text.strip() if thumb_inp.text != "no" else None
    await thumb_inp.delete(True)
    
    await m.reply(f"🚀 {len(links)} चैप्टर्स डाउनलोड स्टार्ट {start_num} से...")
    
    for i, (chapter, link) in enumerate(links[start_num-1:], start_num):
        try:
            name = f"{chapter}.mp4"
            if "youtube" in link or "youtu.be" in link:
                ydl_opts = {'format': 'best[height<=720]', 'outtmpl': name}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([link])
                await m.reply_video(name, caption=f"🎥 {chapter}
🔗 {link}")
                os.remove(name)
            elif ".pdf" in link:
                scraper = cloudscraper.create_scraper()
                url = link.replace(" ", "%20")
                resp = scraper.get(url)
                if resp.status_code == 200:
                    pdf_name = f"{chapter}.pdf"
                    with open(pdf_name, "wb") as f:
                        f.write(resp.content)
                    await m.reply_document(pdf_name, caption=f"📖 {chapter}
🔗 {link}")
                    os.remove(pdf_name)
                else:
                    await m.reply(f"❌ PDF fail: {link}")
            else:
                await m.reply(f"❓ Unknown: {link}")
            await asyncio.sleep(2)
        except Exception as e:
            await m.reply(f"⚠️ Error {chapter}: {str(e)}")
    
    await m.reply("✅ सभी डाउनलोड हो गए! /sk08 फिर ट्राई करो")

# Render keep-alive
async def root(request):
    return web.Response(text="SK08 Bot Alive!")

app = web.Application()
app.router.add_get("/", root)

async def main():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"Web on {PORT}")
    await bot.start()
    print("SK08 Bot चालू!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
    
