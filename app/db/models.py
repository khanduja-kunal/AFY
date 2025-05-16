"""# app/db/models.py
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Boolean, text
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# Download History Model for the database
class DownloadHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str
    status: str
    downloaded_at: datetime
    filename: str
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="downloads") 

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_admin: bool = Field(default=False, sa_column=Column(Boolean, server_default=text("false")))
    downloads: List[DownloadHistory] = Relationship(back_populates="user")

# Pydantic schema for responses (optional in API)
class DownloadHistoryResponse(BaseModel):
    url: str
    status: str
    downloaded_at: datetime
    filename: str

    class Config:
        orm_mode = True

# Request model to be used in FastAPI for download requests
class DownloadRequest(BaseModel):
    url: str
    format: str = "mp4"
    quality: str = "720p"

# Task Status Response for checking task status
class TaskStatusResponse(BaseModel):
    status: str
    result: Optional[dict]

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    is_admin: bool = False

class UserRead(BaseModel):
    id: int
    email: EmailStr

class AdminUserRead(UserRead):
    is_admin: bool

class UserUpdate(BaseModel):
    email: Optional[str]
    password: Optional[str]

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
"""

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Boolean, text
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# Download History Model for the database
class DownloadHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str
    status: str
    downloaded_at: datetime
    filename: str
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    transcript_status: str = Field(default="NotRequested")  # Added
    user: Optional["User"] = Relationship(back_populates="downloads") 

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_admin: bool = Field(default=False, sa_column=Column(Boolean, server_default=text("false")))
    downloads: List[DownloadHistory] = Relationship(back_populates="user")

# Pydantic schema for responses
class DownloadHistoryResponse(BaseModel):
    url: str
    status: str
    downloaded_at: datetime
    filename: str
    transcript_status: str  # Added

    class Config:
        orm_mode = True

# Request model for download requests
class DownloadRequest(BaseModel):
    url: str
    format: str = "mp4"
    quality: str = "720p"
    include_transcript: bool = False  # Added

# Task Status Response
class TaskStatusResponse(BaseModel):
    status: str
    result: Optional[dict]

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    is_admin: bool = False

class UserRead(BaseModel):
    id: int
    email: EmailStr

class AdminUserRead(UserRead):
    is_admin: bool

class UserUpdate(BaseModel):
    email: Optional[str]
    password: Optional[str]

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"