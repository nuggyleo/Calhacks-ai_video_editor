from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    saved_videos = relationship("SavedVideo", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Store project state as JSON
    media_bin = Column(Text, default="[]")  # JSON array of media files
    chat_history = Column(Text, default="[]")  # JSON array of chat messages
    
    # Relationships
    user = relationship("User", back_populates="projects")


class SavedVideo(Base):
    __tablename__ = "saved_videos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Changed from project_id to user_id
    filename = Column(String, nullable=False)
    url = Column(String, nullable=False)
    thumbnail = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="saved_videos")
