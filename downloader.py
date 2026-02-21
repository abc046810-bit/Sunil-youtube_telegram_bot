import yt_dlp
import os

def download_video(url):
    ydl_opts = {
        "format": "mp4",
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "quiet": True
    }

    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get("title", "video")
        filename = ydl.prepare_filename(info)

    return title, filename
