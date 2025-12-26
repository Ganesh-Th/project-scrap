from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Job, Review, Theme, Task, JobState
from app.schemas import (
    JobCreate, JobResponse, ReviewResponse, ThemeResponse, 
    TaskResponse, TaskUpdate, JobResults
)
from app.tasks.review_tasks import process_reviews

router = APIRouter(prefix="/api", tags=["jobs"])

@router.post("/jobs", response_model=JobResponse)
def create_job(job_data: JobCreate, db: Session = Depends(get_db)):
    """Create a new review analysis job"""
    # Create job
    job = Job(
        app_name=job_data.app_name,
        app_id=job_data.app_id,
        state=JobState.QUEUED
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Trigger async processing
    process_reviews.delay(job.id)
    
    return job

@router.get("/jobs", response_model=List[JobResponse])
def list_jobs(db: Session = Depends(get_db)):
    """List all jobs"""
    jobs = db.query(Job).order_by(Job.created_at.desc()).all()
    return jobs

@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get job details"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/jobs/{job_id}/results", response_model=JobResults)
def get_job_results(job_id: int, db: Session = Depends(get_db)):
    """Get complete job results including reviews and themes"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    reviews = db.query(Review).filter(Review.job_id == job_id).all()
    themes = db.query(Theme).filter(Theme.job_id == job_id).all()
    
    return {
        "job": job,
        "reviews": reviews,
        "themes": themes
    }

@router.get("/jobs/{job_id}/reviews", response_model=List[ReviewResponse])
def get_job_reviews(job_id: int, db: Session = Depends(get_db)):
    """Get reviews for a job"""
    reviews = db.query(Review).filter(Review.job_id == job_id).all()
    return reviews

@router.get("/jobs/{job_id}/themes", response_model=List[ThemeResponse])
def get_job_themes(job_id: int, db: Session = Depends(get_db)):
    """Get themes for a job"""
    themes = db.query(Theme).filter(Theme.job_id == job_id).all()
    return themes

@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """Update task RICE scores or confirmation status"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update fields
    if task_update.reach is not None:
        task.reach = task_update.reach
    if task_update.impact is not None:
        task.impact = task_update.impact
    if task_update.confidence is not None:
        task.confidence = task_update.confidence
    if task_update.effort is not None:
        task.effort = task_update.effort
    if task_update.confirmed is not None:
        task.confirmed = task_update.confirmed
    
    # Recalculate RICE score
    task.rice_score = (task.reach * task.impact * task.confidence) / (100 * task.effort)
    
    db.commit()
    db.refresh(task)
    
    return task

@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get task details"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
