from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from .database import Base

# Many-to-many association table
event_registrations = Table(
    'event_registrations',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('event_id', Integer, ForeignKey('events.id'))
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="customer")  # "manager" or "customer"
    
    # Many-to-many relationship with events
    registered_events = relationship("Event", secondary=event_registrations, back_populates="attendees")

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    datetime = Column(DateTime)
    location = Column(String)
    capacity = Column(Integer)
    
    # Many-to-many relationship with users
    attendees = relationship("User", secondary=event_registrations, back_populates="registered_events")
