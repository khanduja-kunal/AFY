import os
import uuid
import yt_dlp
from pytube import YouTube
from app.utils.validation import slugify

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_video_yt_dlp(url: str, format: str, quality: str) -> str:
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'video')
        slug = slugify(title)
        short_id = uuid.uuid4().hex[:8]
        file_name = f"{slug}__{short_id}.{format}"
        file_path = os.path.join(DOWNLOAD_DIR, file_name)

        ydl_opts = {
            'format': 'bestaudio/best' if format == 'mp3'
                      else f'bestvideo[height<={quality.replace("p", "")}]+bestaudio/best',
            'outtmpl': file_path,
            'merge_output_format': format if format != 'mp3' else None,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return file_path
    except Exception as e:
        raise Exception(f"yt-dlp failed: {str(e)}")

# Function to download video using pytube
def download_video_pytube(url: str, format: str, quality: str) -> str:
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension=format).get_by_resolution(quality)
        if not stream:
            raise Exception(f"No stream available for quality {quality}.")
        slug = slugify(yt.title)
        short_id = uuid.uuid4().hex[:8]
        file_name = f"{slug}__{short_id}.{format}"
        file_path = os.path.join(DOWNLOAD_DIR, file_name)
        stream.download(output_path=DOWNLOAD_DIR, filename=file_name)
        return file_path
    except Exception as e:
        raise Exception(f"pytube failed: {str(e)}")
