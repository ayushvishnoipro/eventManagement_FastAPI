from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from . import models, schemas
from .auth import get_password_hash, verify_password

def create_user(db: Session, user: schemas.UserCreate):
    # Check if user already exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_event(db: Session, event: schemas.EventCreate):
    db_event = models.Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_events(db: Session):
    return db.query(models.Event).all()

def get_event(db: Session, event_id: int):
    return db.query(models.Event).filter(models.Event.id == event_id).first()

def register_user_for_event(db: Session, user_id: int, event_id: int):
    # Get event and user
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user is already registered
    if user in event.attendees:
        raise HTTPException(status_code=400, detail="User already registered for this event")
    
    # Check capacity
    if len(event.attendees) >= event.capacity:
        raise HTTPException(status_code=400, detail="Event is at full capacity")
    
    # Register user
    event.attendees.append(user)
    db.commit()
    return {"message": "Successfully registered for event"}
