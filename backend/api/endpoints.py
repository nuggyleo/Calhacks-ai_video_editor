from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
import json
from datetime import datetime

from .. import auth
from ..database import schemas, models
from ..database.database import SessionLocal

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = auth.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return auth.create_user(db=db, user=user)

@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"sub": user.email}
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ==================== PROJECT ENDPOINTS ====================

@router.get("/projects/", response_model=List[schemas.Project])
def get_user_projects(user_email: str, db: Session = Depends(get_db)):
    """Get all projects for a user"""
    user = auth.get_user_by_email(db, email=user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.projects


@router.post("/projects/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, user_email: str, db: Session = Depends(get_db)):
    """Create a new project for a user"""
    user = auth.get_user_by_email(db, email=user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_project = models.Project(
        name=project.name,
        user_id=user.id,
        media_bin="[]",
        chat_history="[]"
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.get("/projects/{project_id}", response_model=schemas.Project)
def get_project(project_id: int, user_email: str, db: Session = Depends(get_db)):
    """Get a specific project"""
    user = auth.get_user_by_email(db, email=user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/projects/{project_id}", response_model=schemas.Project)
def update_project(project_id: int, project_update: schemas.ProjectUpdate, user_email: str, db: Session = Depends(get_db)):
    """Update a project (name, media_bin, chat_history)"""
    user = auth.get_user_by_email(db, email=user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == user.id
    ).first()
    
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Update fields if provided
    if project_update.name is not None:
        db_project.name = project_update.name
    if project_update.media_bin is not None:
        db_project.media_bin = project_update.media_bin
    if project_update.chat_history is not None:
        db_project.chat_history = project_update.chat_history
    
    db_project.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_project)
    return db_project


@router.delete("/projects/{project_id}")
def delete_project(project_id: int, user_email: str, db: Session = Depends(get_db)):
    """Delete a project"""
    user = auth.get_user_by_email(db, email=user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == user.id
    ).first()
    
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted successfully"}


# ==================== SAVED VIDEO ENDPOINTS ====================

@router.get("/saved-videos/", response_model=List[schemas.SavedVideo])
def get_saved_videos(user_email: str, db: Session = Depends(get_db)):
    """Get all saved videos for a user (global, not per-project)"""
    user = auth.get_user_by_email(db, email=user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user.saved_videos


@router.post("/saved-videos/", response_model=schemas.SavedVideo)
def save_video(video: schemas.SavedVideoBase, user_email: str, db: Session = Depends(get_db)):
    """Save a video to user's saved collection (global)"""
    user = auth.get_user_by_email(db, email=user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_video = models.SavedVideo(
        user_id=user.id,
        filename=video.filename,
        url=video.url,
        thumbnail=video.thumbnail,
        description=video.description
    )
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video


@router.delete("/saved-videos/{video_id}")
def delete_saved_video(video_id: int, user_email: str, db: Session = Depends(get_db)):
    """Delete a saved video"""
    user = auth.get_user_by_email(db, email=user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_video = db.query(models.SavedVideo).filter(
        models.SavedVideo.id == video_id,
        models.SavedVideo.user_id == user.id
    ).first()
    
    if not db_video:
        raise HTTPException(status_code=404, detail="Saved video not found")
    
    db.delete(db_video)
    db.commit()
    return {"message": "Saved video deleted successfully"} 