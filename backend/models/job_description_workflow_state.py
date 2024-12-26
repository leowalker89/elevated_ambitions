from typing import Optional, Dict, Literal
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from backend.models.job_description_models import JobDescription, GraderOutput

class JobDescriptionProcessingState(BaseModel):
    """
    Manages the workflow state for processing job descriptions from raw postings to structured data.
    """
    model_config = ConfigDict(from_attributes=True)
    
    job_id: str = Field(description="Unique identifier for the job posting")
    raw_job_data: Dict = Field(description="Original unprocessed job posting data")
    structured_job: Optional[JobDescription] = None
    grader_output: Optional[GraderOutput] = None
    attempts: int = Field(default=0, ge=0)
    max_attempts: int = Field(default=3, ge=1)
    status: Literal["extracting", "grading", "completed", "failed"] = Field(default="extracting")
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None