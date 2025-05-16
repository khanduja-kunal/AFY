"""from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import List
from app.db.models import DownloadHistory, DownloadHistoryResponse
from app.db.session import get_session

router = APIRouter()

@router.get("/history", response_model=List[DownloadHistoryResponse])
async def get_download_history(session: AsyncSession = Depends(get_session)):
    result = await session.exec(select(DownloadHistory))
    return result.all()
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.db.models import DownloadHistory, User
from app.db.session import get_session
from app.core.security import get_current_user
import os

router = APIRouter(prefix="/history", tags=["History"])

@router.get("/", response_model=list[dict])
async def get_history(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    if current_user.is_admin:
        # Admins see all download history
        statement = select(DownloadHistory)
    else:
        # Regular users see only their download history
        statement = select(DownloadHistory).where(DownloadHistory.user_id == current_user.id)
    
    result = await session.exec(statement)
    downloads = result.all()
    return [
        {
            "id": d.id,
            "url": d.url,
            "status": d.status,
            "downloaded_at": d.downloaded_at,
            "filename": d.filename,
            "user_id": d.user_id,
            "transcript_status": d.transcript_status
        }
        for d in downloads
    ]

@router.get("/transcript/{id}")
async def download_transcript(
    id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    statement = select(DownloadHistory).where(DownloadHistory.id == id)
    result = await session.exec(statement)
    history = result.first()
    if not history:
        raise HTTPException(status_code=404, detail="Download not found")
    if not current_user.is_admin and history.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if history.transcript_status != "Completed":
        raise HTTPException(status_code=400, detail="No transcript available")
    
    video_id = history.url.split("v=")[1].split("&")[0] if "v=" in history.url else "unknown"
    transcript_path = os.path.join("transcripts", f"{history.user_id}_{video_id}.txt")
    if not os.path.exists(transcript_path):
        raise HTTPException(status_code=404, detail="Transcript file not found")
    
    return FileResponse(
        transcript_path,
        media_type="text/plain",
        filename=f"transcript_{video_id}.txt"
    )