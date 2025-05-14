"""# app/api/users_self.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.models import User, UserRead, UserUpdate
from app.db.session import get_session
from app.core.security import get_current_user, get_password_hash

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserRead)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserRead)
async def update_my_profile(
    update_data: UserUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if update_data.email:
        current_user.email = update_data.email
    if update_data.password:
        current_user.hashed_password = get_password_hash(update_data.password)
    
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    return current_user
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.models import User, AdminUserRead, UserUpdate
from app.db.session import get_session
from app.core.security import get_current_user, get_password_hash

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=AdminUserRead)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=AdminUserRead)
async def update_my_profile(
    update_data: UserUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if update_data.email:
        current_user.email = update_data.email
    if update_data.password:
        current_user.hashed_password = get_password_hash(update_data.password)
    
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    return current_user