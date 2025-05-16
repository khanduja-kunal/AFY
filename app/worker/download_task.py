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
import logging
from datetime import datetime
from celery import Celery
from sqlalchemy.orm import Session
from app.db.models import DownloadHistory
from app.services.downloader import download_video_yt_dlp, download_video_pytube
from app.services.transcriber import transcribe_audio
from sqlmodel import create_engine
from app.core.config import DATABASE_URL_SYNC, CELERY_BROKER_URL
import yt_dlp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
                subtitle_data = subtitles[0].get("data", "")
                logger.info(f"YouTube transcript fetched, length: {len(subtitle_data)}")
                return subtitle_data if subtitle_data else ""
        logger.info("No YouTube transcript available")
        return ""
    except Exception as e:
        logger.error(f"Failed to fetch YouTube transcript: {str(e)}")
        return ""

def extract_video_id(url: str) -> str:
    """
    Extract video ID from YouTube URL.
    """
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            video_id = info.get("id", "unknown")
            logger.info(f"Extracted video ID: {video_id}")
            return video_id
    except Exception as e:
        logger.error(f"Failed to extract video ID: {str(e)}")
        return "unknown"

def download_with_transcript(url: str, format: str, quality: str, user_id: int, task) -> dict:
    """
    Download video/audio and attempt to generate transcript.
    """
    transcript_status = "Failed"
    filename = "N/A"
    transcript_path = None
    
    try:
        # Download the requested file
        file_path = download_video_yt_dlp(url, format, quality)
        filename = os.path.basename(file_path)
        logger.info(f"Downloaded file: {file_path}")

        # Handle transcript
        video_id = extract_video_id(url)
        transcript_path = os.path.join(TRANSCRIPT_DIR, f"{user_id}_{video_id}.txt")
        logger.info(f"Transcript path: {transcript_path}")

        # Try YouTube transcript first
        transcript = get_youtube_transcript(url)
        if transcript:
            logger.info("Using YouTube transcript")
            os.makedirs(TRANSCRIPT_DIR, exist_ok=True)
            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(transcript)
            transcript_status = "Completed"
            logger.info(f"YouTube transcript saved to: {transcript_path}, length: {len(transcript)}")
        else:
            # Prepare audio for Deepgram transcription
            audio_path = file_path if format == "mp3" else os.path.join(DOWNLOAD_DIR, f"{os.path.splitext(filename)[0]}_audio.mp3")
            logger.info(f"Audio path for transcription: {audio_path}")

            if format != "mp3":
                logger.info(f"Extracting audio for {format} file")
                ydl_opts = {
                    "format": "bestaudio/best",
                    "outtmpl": audio_path.replace(".mp3", ""),
                    "quiet": True,
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }],
                }
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                    logger.info(f"Audio extracted to: {audio_path}")
                except Exception as e:
                    logger.error(f"Audio extraction failed: {str(e)}")
                    raise Exception(f"Audio extraction failed: {str(e)}")

            # Verify audio file exists
            if not os.path.exists(audio_path):
                logger.error(f"Audio file not found at: {audio_path}")
                raise Exception("Audio file not found")

            # Try Deepgram transcription
            transcript_path_result = transcribe_audio(audio_path, transcript_path)
            if transcript_path_result:
                transcript_status = "Completed"
                transcript_path = transcript_path_result
                logger.info(f"Deepgram transcript saved to: {transcript_path}")
            else:
                transcript_status = "Failed"
                logger.info("No transcript generated, marking transcript_status as Failed")

        # Clean up audio file (if different from file_path)
        if format != "mp3" and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
                logger.info(f"Cleaned up audio file: {audio_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up audio file {audio_path}: {str(e)}")

        # Log success
        with Session(engine) as session:
            history = DownloadHistory(
                url=url,
                status="Completed",
                downloaded_at=datetime.utcnow(),
                filename=filename,
                user_id=user_id,
                transcript_status=transcript_status
            )
            session.add(history)
            session.commit()
        logger.info(f"Download completed for user {user_id}, transcript status: {transcript_status}")
        return {
            "status": "success",
            "file_path": filename,
            "transcript_path": transcript_path if transcript_status == "Completed" else None
        }

    except Exception as e:
        logger.error(f"Download/transcription failed: {str(e)}")
        task.update_state(state="FAILURE", meta={"error": str(e)})
        with Session(engine) as session:
            history = DownloadHistory(
                url=url,
                status="Failed",
                downloaded_at=datetime.utcnow(),
                filename=filename if filename != "N/A" else "N/A",
                user_id=user_id,
                transcript_status=transcript_status
            )
            session.add(history)
            session.commit()
        return {"status": "failed", "error": str(e)}

@celery.task(bind=True)
def download_video_task(self, url: str, format: str, quality: str, user_id: int, include_transcript: bool = False):
    """
    Celery task to download video/audio with optional transcript.
    """
    logger.info(f"Starting task with include_transcript: {include_transcript}")
    retries = 0
    max_retries = 3
    last_error = None
    download_success = False
    filename = ""

    if include_transcript:
        logger.info(f"Starting download with transcript for URL: {url}")
        return download_with_transcript(url, format, quality, user_id, self)

    # Original download logic (no transcript)
    logger.info(f"Starting download without transcript for URL: {url}")
    while retries < max_retries and not download_success:
        try:
            file_path = download_video_yt_dlp(url, format, quality)
            filename = os.path.basename(file_path)
            download_success = True
            logger.info(f"Downloaded file: {file_path}")
        except Exception as e:
            last_error = str(e)
            retries += 1
            self.update_state(state="RETRY", meta={"error": last_error, "retries": retries})
            logger.warning(f"Retry {retries}/{max_retries} failed: {last_error}")

    # If yt-dlp failed, try pytube
    if not download_success:
        try:
            file_path = download_video_pytube(url, format, quality)
            filename = os.path.basename(file_path)
            download_success = True
            logger.info(f"Downloaded file with pytube: {file_path}")
        except Exception as fallback_error:
            self.update_state(state="FAILURE", meta={"error": str(fallback_error)})
            with Session(engine) as session:
                history = DownloadHistory(
                    url=url,
                    status="Failed",
                    downloaded_at=datetime.utcnow(),
                    filename="N/A",
                    user_id=user_id,
                    transcript_status="NotRequested"
                )
                session.add(history)
                session.commit()
            logger.error(f"Download failed: {str(fallback_error)}")
            return {"status": "failed", "error": str(fallback_error)}

    if download_success:
        with Session(engine) as session:
            history = DownloadHistory(
                url=url,
                status="Completed",
                downloaded_at=datetime.utcnow(),
                filename=filename,
                user_id=user_id,
                transcript_status="NotRequested"
            )
            session.add(history)
            session.commit()
        logger.info(f"Download completed for user {user_id}")
        return {"status": "success", "file_path": filename, "transcript_path": None}