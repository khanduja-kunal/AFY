import os
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
                    filename="",
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
