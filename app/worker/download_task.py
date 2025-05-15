"""import os
from datetime import datetime
from celery import Celery
from sqlalchemy.orm import Session
from app.db.models import DownloadHistory 
from app.services.downloader import download_video_yt_dlp, download_video_pytube
from sqlalchemy import create_engine
from app.core.config import DATABASE_URL_SYNC, CELERY_BROKER_URL

# Celery Setup
celery = Celery("tasks", broker=CELERY_BROKER_URL)

# Database Setup (Sync for Celery)

engine = create_engine(DATABASE_URL_SYNC)

# Directory to store downloads
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Celery Task to download video
@celery.task(bind=True)
def download_video_task(self, url: str, format: str, quality: str, user_id: int):
    retries = 0
    max_retries = 3
    last_error = None
    download_success = False
    filename = ""

    # Try downloading with yt-dlp and retry up to 3 times
    while retries < max_retries and not download_success:
        try:
            # Try to download using yt-dlp first
            file_path = download_video_yt_dlp(url, format, quality)
            filename = os.path.basename(file_path)
            download_success = True
        except Exception as e:
            last_error = str(e)
            retries += 1
            self.update_state(state="RETRY", meta={"error": last_error, "retries": retries})

    # If yt-dlp failed, try pytube
    if not download_success:
        try:
            # Fall back to pytube for downloading
            file_path = download_video_pytube(url, format, quality)
            filename = os.path.basename(file_path)
            download_success = True
        except Exception as fallback_error:
            # Final failure — log as "Failed"
            self.update_state(state="FAILURE", meta={"error": str(fallback_error)})
            with Session(engine) as session:
                history = DownloadHistory(
                    url=url,
                    status="Failed",
                    downloaded_at=datetime.utcnow(),
                    filename="N/A",
                    user_id=user_id
                )
                session.add(history)
                session.commit()
            return {"status": "failed", "error": str(fallback_error)}

    if download_success:
        with Session(engine) as session:
            history = DownloadHistory(
                url=url,
                status="Completed",
                downloaded_at=datetime.utcnow(),
                filename=filename,
                user_id=user_id
            )
            session.add(history)
            session.commit()
        return {"status": "success", "file_path": filename}
"""

import os
from datetime import datetime
from celery import Celery
from sqlalchemy.orm import Session
from app.db.models import DownloadHistory
from app.services.downloader import download_video_yt_dlp, download_video_pytube
from app.services.transcriber import transcribe_audio
from sqlalchemy import create_engine
from app.core.config import DATABASE_URL_SYNC, CELERY_BROKER_URL
import yt_dlp

# Celery Setup
celery = Celery("tasks", broker=CELERY_BROKER_URL)

# Database Setup (Sync for Celery)
engine = create_engine(DATABASE_URL_SYNC)

# Directories
DOWNLOAD_DIR = "downloads"
TRANSCRIPT_DIR = "transcripts"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

def get_youtube_transcript(url: str) -> str:
    """
    Attempt to fetch YouTube auto-generated transcript.
    """
    try:
        ydl_opts = {
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en"],
            "skip_download": True,
            "quiet": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            subtitles = info.get("automatic_captions", {}).get("en", [])
            if subtitles:
                subtitle = subtitles[0].get("data", "")
                return subtitle if subtitle else ""
        return ""
    except Exception:
        return ""

def extract_video_id(url: str) -> str:
    """
    Extract video ID from YouTube URL.
    """
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get("id", "unknown")
    except Exception:
        return "unknown"

@celery.task(bind=True)
def download_video_task(self, url: str, format: str, quality: str, user_id: int, include_transcript: bool = True):
    retries = 0
    max_retries = 3
    last_error = None
    download_success = False
    filename = ""
    transcript_path = ""

    # Try downloading with yt-dlp and retry up to 3 times
    while retries < max_retries and not download_success:
        try:
            file_path = download_video_yt_dlp(url, format, quality)
            filename = os.path.basename(file_path)
            download_success = True
        except Exception as e:
            last_error = str(e)
            retries += 1
            self.update_state(state="RETRY", meta={"error": last_error, "retries": retries})

    # If yt-dlp failed, try pytube
    if not download_success:
        try:
            file_path = download_video_pytube(url, format, quality)
            filename = os.path.basename(file_path)
            download_success = True
        except Exception as fallback_error:
            # Final failure — log as "Failed"
            self.update_state(state="FAILURE", meta={"error": str(fallback_error)})
            with Session(engine) as session:
                history = DownloadHistory(
                    url=url,
                    status="Failed",
                    downloaded_at=datetime.utcnow(),
                    filename="N/A",
                    user_id=user_id
                )
                session.add(history)
                session.commit()
            return {"status": "failed", "error": str(fallback_error)}

    if download_success:
        try:
            # Handle transcript if requested
            video_id = extract_video_id(url)
            transcript_path = os.path.join(TRANSCRIPT_DIR, f"{user_id}_{video_id}.txt")
            audio_path = file_path if format == "mp3" else file_path.replace(f".{format}", ".mp3")

            if include_transcript:
                # Try YouTube transcript first
                transcript = get_youtube_transcript(url)
                if transcript:
                    os.makedirs(TRANSCRIPT_DIR, exist_ok=True)
                    with open(transcript_path, "w", encoding="utf-8") as f:
                        f.write(transcript)
                else:
                    # Extract audio if video format (yt-dlp already extracts mp3 for mp3 format)
                    if format != "mp3":
                        ydl_opts = {
                            "format": "bestaudio/best",
                            "outtmpl": audio_path,
                            "quiet": True,
                            "postprocessors": [{
                                "key": "FFmpegExtractAudio",
                                "preferredcodec": "mp3",
                                "preferredquality": "192",
                            }],
                        }
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            ydl.download([url])

                    # Transcribe audio
                    transcribe_audio(audio_path, transcript_path)

            # Clean up audio file
            if os.path.exists(audio_path) and audio_path != file_path:
                os.remove(audio_path)

            # Log success
            with Session(engine) as session:
                history = DownloadHistory(
                    url=url,
                    status="Completed",
                    downloaded_at=datetime.utcnow(),
                    filename=filename,
                    user_id=user_id
                )
                session.add(history)
                session.commit()
            return {"status": "success", "file_path": filename, "transcript_path": transcript_path if include_transcript else None}

        except Exception as e:
            # Log failure due to transcription
            self.update_state(state="FAILURE", meta={"error": str(e)})
            with Session(engine) as session:
                history = DownloadHistory(
                    url=url,
                    status="Failed",
                    downloaded_at=datetime.utcnow(),
                    filename=filename,
                    user_id=user_id
                )
                session.add(history)
                session.commit()
            return {"status": "failed", "error": str(e)}