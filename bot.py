import os
from telegram import Update, Document
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from downloader import download_video
from txt_handler import process_txt
from caption import make_caption

BOT_TOKEN = os.environ.get("BOT_TOKEN")

ALLOWED_USERS = [123456789]  # <-- अपना Telegram User ID डालो

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return
    await update.message.reply_text("YouTube Downloader Bot Ready ✅")

async def yt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return

    if not context.args:
        await update.message.reply_text("YouTube link दो")
        return

    url = context.args[0]
    msg = await update.message.reply_text("Downloading...")

    title, file_path = download_video(url)
    caption = make_caption(title, "001")

    await update.message.reply_video(
        video=open(file_path, "rb"),
        caption=caption
    )

    os.remove(file_path)
    await msg.delete()

async def txt_file_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return

    document: Document = update.message.document

    if not document.file_name.endswith(".txt"):
        return

    file = await document.get_file()
    txt_path = f"downloads/{document.file_name}"
    await file.download_to_drive(txt_path)

    results = process_txt(txt_path)

    vid_id = 1
    for title, video_path in results:
        caption = make_caption(title, f"{vid_id:03}")
        await update.message.reply_video(
            video=open(video_path, "rb"),
            caption=caption
        )
        os.remove(video_path)
        vid_id += 1

    os.remove(txt_path)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("yt", yt_command))
    app.add_handler(MessageHandler(filters.Document.ALL, txt_file_handler))

    app.run_polling()

if __name__ == "__main__":
    main()
