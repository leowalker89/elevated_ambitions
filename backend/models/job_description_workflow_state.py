from typing import Optional, Dict
from enum import Enum
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from .job_description_models import JobDescription, GraderOutput

class JobDescriptionProcessingStatus(str, Enum):
    """Status of the job description extraction and processing workflow"""
    PENDING = "pending"
    EXTRACTING = "extracting"
    GRADING = "grading"
    DECIDING = "deciding"
    COMPLETED = "completed"
    FAILED = "failed"

class JobDescriptionProcessingState(BaseModel):
    """
    State management for job description extraction workflow.
    Tracks the progress of converting raw job postings into structured descriptions.
    """
    model_config = ConfigDict(from_attributes=True)  # Replace Config class
    
    job_id: str
    raw_job_data: Dict
    structured_job: Optional[JobDescription] = None
    grader_output: Optional[GraderOutput] = None
    attempts: int = 0
    max_attempts: int = 3
    status: JobDescriptionProcessingStatus = JobDescriptionProcessingStatus.PENDING
    last_feedback: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None