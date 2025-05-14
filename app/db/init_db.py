# app/db/init_db.py
from sqlmodel import SQLModel
from app.db.session import engine

# Function to initialize the database
async def init_db():
    async with engine.begin() as conn:  # Engine from session.py
        await conn.run_sync(SQLModel.metadata.create_all)
