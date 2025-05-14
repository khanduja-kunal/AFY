import re
from yt_dlp import YoutubeDL
from fastapi import HTTPException, status
from datetime import datetime
from app.db.models import DownloadHistory, User
from app.core.config import MAX_VIDEO_DURATION, MAX_VIDEO_SIZE

async def validate_video_constraints(request_url: str, session, current_user: User):
    with YoutubeDL({'quiet': True, 'noplaylist': True}) as ydl:
        info = ydl.extract_info(request_url, download=False)
        size = info.get("filesize") or info.get("filesize_approx") or 0
        duration = info.get("duration") or 0

        if size and size > MAX_VIDEO_SIZE:
            await log_failure(session, request_url, current_user.id)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Video size exceeds 3GB limit. Size: {round(size / (1024 ** 3), 2)} GB"
            )

        if duration and duration > MAX_VIDEO_DURATION:
            await log_failure(session, request_url, current_user.id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Video duration exceeds 5 hour limit. Duration: {round(duration / 3600, 2)} hours"
            )

        return info


async def log_failure(session, url: str, user_id: int):
    """Logs a failed download attempt in history."""
    history = DownloadHistory(
        url=url,
        status="Failed",
        downloaded_at=datetime.utcnow(),
        filename="",
        user_id=user_id

    )
    session.add(history)
    await session.commit()

def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "_", text)

def is_valid_youtube_url(url: str) -> bool:
    if url.count("http://") > 1 or url.count("https://") > 1:
        return False
    if url.count("www.") > 1:
        return False
    youtube_pattern = (
        r'^(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|(?:v|e(?:mbed)?)\/|.*[?&]v=|.*[?&]embed\/|.*\/)([a-zA-Z0-9_-]{11})'
    )
    return re.match(youtube_pattern, url.strip()) is not None
