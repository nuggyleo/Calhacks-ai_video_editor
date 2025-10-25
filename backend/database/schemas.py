from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True


# Project Schemas
class ProjectBase(BaseModel):
    name: str

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    media_bin: Optional[str] = None  # JSON string
    chat_history: Optional[str] = None  # JSON string

class Project(ProjectBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    media_bin: str
    chat_history: str

    class Config:
        orm_mode = True


# SavedVideo Schemas
class SavedVideoBase(BaseModel):
    filename: str
    url: str
    thumbnail: Optional[str] = None
    description: Optional[str] = None

class SavedVideoCreate(SavedVideoBase):
    pass  # No project_id needed anymore

class SavedVideo(SavedVideoBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True
