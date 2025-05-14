from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine 
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL_ASYNC

# DB Engine and session setup
engine = create_async_engine(DATABASE_URL_ASYNC, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Function to provide DB session to routes
async def get_session():
    async with async_session() as session:
        yield session
