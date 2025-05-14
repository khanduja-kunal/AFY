from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from celery import Celery
from app.db.models import DownloadRequest, User
from app.utils.validation import is_valid_youtube_url
from app.core.rate_limit import check_rate_limit
from app.db.session import get_session
from app.core.security import get_current_user
from app.utils.validation import validate_video_constraints
from app.core.config import CELERY_BROKER_URL


router = APIRouter()

celery_app = Celery("tasks", broker=CELERY_BROKER_URL, backend=CELERY_BROKER_URL)

ALLOWED_FORMATS = ['mp4', 'webm', 'mkv', 'mp3']
ALLOWED_QUALITIES = ['360p', '480p', '720p', '1080p', '4k']


@router.post("/download/")
async def download_trigger(
    request: DownloadRequest,
    current_user = Depends(get_current_user),
    client: Request = None,
    session: AsyncSession = Depends(get_session)
):
    client_ip = client.client.host
    check_rate_limit(client_ip)

    if not is_valid_youtube_url(request.url):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid YouTube URL.")
    
    if request.format not in ALLOWED_FORMATS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported format. Allowed: {ALLOWED_FORMATS}")
    if request.quality.lower() not in ALLOWED_QUALITIES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported quality. Allowed: {ALLOWED_QUALITIES}")

    await validate_video_constraints(request.url, session, current_user)

    task = celery_app.send_task(
        "app.worker.download_task.download_video_task",
        args=[request.url, request.format.lower(), request.quality.lower(), current_user.id],
    )
    return {"task_id": task.id, "message": "Download started"}
