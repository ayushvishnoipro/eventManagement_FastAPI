from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str = "customer"

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    
    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class EventBase(BaseModel):
    title: str
    description: str
    datetime: datetime
    location: str
    capacity: int

class EventCreate(EventBase):
    pass

class Event(EventBase):
    id: int
    attendees: List[User] = []
    
    class Config:
        orm_mode = True

class EventRegistration(BaseModel):
    event_id: int

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User
