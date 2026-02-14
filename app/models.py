"""Database models"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

Base = declarative_base()

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    email = Column(String(255), unique=True)
    company = Column(String(255))
    project_type = Column(String(255))
    requirements = Column(Text)
    timeline = Column(String(100))
    budget = Column(String(100))
    status = Column(String(50), default="new")
    thread_id = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

class Proposal(Base):
    __tablename__ = "proposals"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer)
    proposal_text = Column(Text)
    cost_min = Column(Integer)
    cost_max = Column(Integer)
    status = Column(String(50), default="pending")
    draft_id = Column(String(255))
    approved = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

engine = create_engine("sqlite:///./copilot.db")
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
