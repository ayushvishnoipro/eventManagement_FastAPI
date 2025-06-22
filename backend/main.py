from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
from . import crud, models, schemas
from .database import SessionLocal, engine, get_db
from .auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from .roles import require_manager, require_customer

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Event Booking System", version="1.0.0")

# CORS middleware for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/signup", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

@app.post("/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@app.get("/events", response_model=list[schemas.Event])
def get_events(db: Session = Depends(get_db)):
    return crud.get_events(db)

@app.post("/events", response_model=schemas.Event)
def create_event(
    event: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_manager)
):
    return crud.create_event(db=db, event=event)

@app.post("/register")
def register_for_event(
    registration: schemas.EventRegistration,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_customer)
):
    return crud.register_user_for_event(db, current_user.id, registration.event_id)

@app.get("/")
def root():
    return {"message": "Event Booking System API"}
