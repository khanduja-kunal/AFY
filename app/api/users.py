'''from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from app.db.models import User, UserRead, UserUpdate
from app.db.session import get_session
from app.core.security import get_current_user, get_current_admin_user, get_password_hash

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

@router.get("/", response_model=list[UserRead])
async def get_all_users(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin_user)
):
    result = await session.execute(select(User))
    return result.scalars().all()

@router.get("/{user_id}", response_model=UserRead)
async def get_user_by_id(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin_user)
):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
'''