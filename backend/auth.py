from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
import hashlib
import secrets

from .database import models, schemas

# --- Secret Key and Algorithm ---
SECRET_KEY = "a_very_secret_key"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password, hashed_password):
    """Verify a password against its hash"""
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def get_password_hash(password):
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email=email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict):
    """Create a simple access token"""
    # For simplicity, we'll create a token with email and expiry
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = f"{data['sub']}:{expire.timestamp()}"
    return hashlib.sha256(token_data.encode()).hexdigest()
