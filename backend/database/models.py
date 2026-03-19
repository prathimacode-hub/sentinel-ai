from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from datetime import datetime
from database.db import Base


# -----------------------------
# STUDENT TABLE
# -----------------------------
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, unique=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


# -----------------------------
# EVENT TABLE
# -----------------------------
class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String)
    level = Column(String)
    score = Column(Float)
    explanation = Column(String)
    reasons = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)


# -----------------------------
# EVIDENCE TABLE
# -----------------------------
class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer)
    image_path = Column(String)
    video_path = Column(String)
    audio_path = Column(String)
    hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
