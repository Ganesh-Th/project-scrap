from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

class JobState(str, enum.Enum):
    QUEUED = "queued"
    FETCHING = "fetching"
    ANALYZING = "analyzing"
    CLUSTERING = "clustering"
    DONE = "done"
    FAILED = "failed"

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    app_name = Column(String, nullable=False)
    app_id = Column(String, nullable=False)
    state = Column(Enum(JobState), default=JobState.QUEUED)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    error_message = Column(Text, nullable=True)
    
    reviews = relationship("Review", back_populates="job", cascade="all, delete-orphan")
    themes = relationship("Theme", back_populates="job", cascade="all, delete-orphan")

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    author = Column(String)
    rating = Column(Float)
    content = Column(Text)
    date = Column(DateTime)
    sentiment = Column(String)  # positive, negative, neutral
    sentiment_score = Column(Float)
    
    # Multi-label classification
    is_bug = Column(Float, default=0.0)
    is_feature = Column(Float, default=0.0)
    is_usability = Column(Float, default=0.0)
    is_requirement = Column(Float, default=0.0)
    is_praise = Column(Float, default=0.0)
    
    cluster_id = Column(Integer, nullable=True)
    
    job = relationship("Job", back_populates="reviews")

class Theme(Base):
    __tablename__ = "themes"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    cluster_id = Column(Integer)
    title = Column(String)
    description = Column(Text)
    review_count = Column(Integer)
    avg_sentiment = Column(Float)
    
    job = relationship("Job", back_populates="themes")
    tasks = relationship("Task", back_populates="theme", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    theme_id = Column(Integer, ForeignKey("themes.id"), nullable=False)
    title = Column(String)
    description = Column(Text)
    
    # RICE scoring
    reach = Column(Integer, default=0)
    impact = Column(Integer, default=0)
    confidence = Column(Integer, default=0)
    effort = Column(Integer, default=1)
    rice_score = Column(Float, default=0.0)
    
    confirmed = Column(Integer, default=0)  # 0 = pending, 1 = confirmed, -1 = rejected
    
    theme = relationship("Theme", back_populates="tasks")
