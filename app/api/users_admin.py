# app/api/users_admin.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from app.db.models import User, AdminUserRead
from app.db.session import get_session
from app.core.security import get_current_admin_user

router = APIRouter(prefix="/admin/users", tags=["Admin"])

@router.get("/", response_model=list[AdminUserRead])
async def get_all_users(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin_user)
):
    result = await session.execute(select(User))
    return result.scalars().all()

@router.get("/{user_id}", response_model=AdminUserRead)
async def get_user_by_id(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin_user)
):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
