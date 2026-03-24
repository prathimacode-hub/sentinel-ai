import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from database.db import Base


# -----------------------------
# STUDENT TABLE
# -----------------------------
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)

    # Unique student identifier (used across system)
    student_id = Column(String, unique=True, index=True, nullable=False)

    # Optional student name
    name = Column(String, nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    # -----------------------------
    # RELATIONSHIPS
    # -----------------------------
    events = relationship(
        "Event",
        back_populates="student",
        cascade="all, delete-orphan"
    )


# -----------------------------
# EVENT TABLE (CORE DETECTION)
# -----------------------------
class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)

    # Link to student (foreign key)
    student_id = Column(String, ForeignKey("students.student_id"), nullable=False)

    # Risk level (HIGH / MEDIUM / LOW)
    level = Column(String, nullable=False)

    # Numeric cheating score
    score = Column(Float, nullable=False)

    # Human-readable explanation
    explanation = Column(String, nullable=True)

    # Store reasons/events as string (safe for SQLite)
    reasons = Column(String, nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    # -----------------------------
    # RELATIONSHIPS
    # -----------------------------
    student = relationship(
        "Student",
        back_populates="events"
    )

    evidence = relationship(
        "Evidence",
        back_populates="event",
        cascade="all, delete-orphan"
    )


# -----------------------------
# EVIDENCE TABLE (PROOF STORAGE)
# -----------------------------
class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)

    # Link to event
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)

    # File paths
    image_path = Column(String, nullable=True)
    video_path = Column(String, nullable=True)
    audio_path = Column(String, nullable=True)

    # Tamper-proof hash (for integrity)
    hash = Column(String, nullable=False)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    # -----------------------------
    # RELATIONSHIPS
    # -----------------------------
    event = relationship(
        "Event",
        back_populates="evidence"
    )
