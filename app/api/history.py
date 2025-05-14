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
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.models import DownloadHistory
from app.db.session import get_session
from app.core.security import get_current_user
from app.db.models import User
from sqlmodel import select

router = APIRouter(prefix="/history", tags=["History"])

@router.get("/", response_model=list[DownloadHistory])
async def get_history(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    if current_user.is_admin:
        # Admins see all download history
        statement = select(DownloadHistory)
    else:
        # Regular users see only their download history
        statement = select(DownloadHistory).where(DownloadHistory.user_id == current_user.id)
    
    result = await session.exec(statement)
    downloads = result.all()
    return downloads