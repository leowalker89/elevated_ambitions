from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from typing import Dict, Optional
from langchain.prompts import ChatPromptTemplate
from datetime import datetime

from models.job_description_models import JobDescription, GraderOutput
from models.job_description_workflow_state import JobDescriptionProcessingState, JobDescriptionProcessingStatus
from models.jobs_search_models import JobListing
from prompts.job_description_processing import job_description_annotator, job_description_grader

load_dotenv()

async def extraction_node(state: JobDescriptionProcessingState) -> dict:
    """Extract structured job information from raw job listing data.
    
    Args:
        state (JobDescriptionProcessingState): Current workflow state containing raw job data
        
    Returns:
        dict: Updates to the workflow state including:
            - status: Current processing status
            - attempts: Incremented attempt counter
            - structured_job: Extracted job data (if successful)
            - error_message: Any error information
            - updated_at: Timestamp of the update
    """
    state_updates = {
        "status": JobDescriptionProcessingStatus.EXTRACTING,
        "attempts": state.attempts + 1,
        "updated_at": datetime.now()
    }
    
    try:
        context = {
            "raw_job": state.raw_job_data,
            "attempt_number": state.attempts + 1,
            "previous_feedback": state.last_feedback or "None",
            "previous_extraction": state.structured_job.model_dump() if state.structured_job else "None"
        }
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", job_description_annotator),
            ("user", """
            Please parse this job listing into a structured format. Here's the context:
            
            Raw Job Data: {raw_job}
            Attempt Number: {attempt_number}
            Previous Feedback: {previous_feedback}
            Previous Structured Job: {previous_extraction}
            """)
        ])

        extraction_model = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            max_retries=2,
        ).with_structured_output(JobDescription)
        
        structured_job = await (prompt | extraction_model).ainvoke(context)
        
        state_updates.update({
            "structured_job": structured_job,
            "error_message": None
        })
        
    except Exception as e:
        state_updates.update({
            "status": JobDescriptionProcessingStatus.FAILED,
            "error_message": str(e)
        })
    
    return state_updates

async def grader_node(state: JobDescriptionProcessingState) -> dict:
    """Grade the quality of the structured job extraction.
    
    Args:
        state (JobDescriptionProcessingState): Current workflow state containing extracted job data
        
    Returns:
        dict: Updates to the workflow state including:
            - status: Updated processing status based on grade
            - grader_output: Grading results and feedback
            - last_feedback: Detailed feedback for potential retry
            - error_message: Any error information
            - updated_at: Timestamp of the update
    """
    state_updates = {
        "updated_at": datetime.now()
    }
    
    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", job_description_grader),
            ("user", """
            Please grade the following job description extraction:
            
            Original Job Listing: {raw_job}
            Extracted Job Description: {structured_job}
            """)
        ])
        
        grader_model = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            max_retries=2,
            stop_sequences=None,
        ).with_structured_output(GraderOutput)
        
        grader_output = await (prompt | grader_model).ainvoke({
            "raw_job": state.raw_job_data,
            "structured_job": state.structured_job
        })
        
        # Determine status based on grade
        if grader_output.overall_grade == 'A':
            status = JobDescriptionProcessingStatus.COMPLETED
            error_message = None
        elif state.attempts >= state.max_attempts:
            if grader_output.overall_grade == 'B':
                status = JobDescriptionProcessingStatus.COMPLETED
                error_message = None
            else:
                status = JobDescriptionProcessingStatus.FAILED
                error_message = f"Max attempts reached. Final grade: {grader_output.overall_grade}"
        else:
            status = JobDescriptionProcessingStatus.EXTRACTING
            error_message = None
        
        state_updates.update({
            "grader_output": grader_output,
            "status": status,
            "last_feedback": grader_output.overall_feedback,
            "error_message": error_message
        })
        
    except Exception as e:
        state_updates.update({
            "status": JobDescriptionProcessingStatus.FAILED,
            "error_message": str(e)
        })
    
    return state_updates