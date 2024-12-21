from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from typing import Dict, Optional
from langchain.prompts import ChatPromptTemplate
from datetime import datetime

from models.job_description_models import JobDescription, GraderOutput
from models.job_description_workflow_state import JobDescriptionProcessingState, ProcessingStatusType
from prompts.job_description_processing import job_description_annotator, job_description_grader

load_dotenv()

async def extraction_node(state: JobDescriptionProcessingState) -> dict:
    """Extract structured job information from raw job listing data.
    
    Args:
        state (JobDescriptionProcessingState): Current workflow state containing raw job data
        
    Returns:
        dict: Updates to the workflow state including structured job data and status
    """
    state_updates = {
        "status": "extracting",
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
            stop_sequences=None
        ).with_structured_output(JobDescription)
        
        structured_job = await (prompt | extraction_model).ainvoke(context)
        
        state_updates.update({
            "structured_job": structured_job,
            "error_message": None
        })
        
    except Exception as e:
        state_updates.update({
            "status": "failed",
            "error_message": str(e)
        })
    
    return state_updates

async def grader_node(state: JobDescriptionProcessingState) -> dict:
    """Grade the quality of the structured job extraction.
    
    Args:
        state (JobDescriptionProcessingState): Current workflow state containing extracted job data
        
    Returns:
        dict: Updates to the workflow state including grading results and status
    """
    state_updates = {
        "updated_at": datetime.now()
    }
    
    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", job_description_grader),
            ("user", """
            Please evaluate the following job description extraction:
            
            Original Job Listing: {raw_job}
            Extracted Job Description: {structured_job}
            """)
        ])
        
        grader_model = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            max_retries=2,
            stop_sequences=None
        ).with_structured_output(GraderOutput)
        
        grader_output = await (prompt | grader_model).ainvoke({
            "raw_job": state.raw_job_data,
            "structured_job": state.structured_job
        })
        
        # Determine status based on quality score and improvement potential
        if grader_output.overall_quality_score >= 0.8:
            status = "completed"
            error_message = None
        elif state.attempts >= state.max_attempts:
            if grader_output.overall_quality_score >= 0.6:
                status = "completed"
                error_message = None
            else:
                status = "failed"
                error_message = f"Max attempts reached. Final quality score: {grader_output.overall_quality_score}"
        else:
            # Check if any sections need improvement and have untapped source data
            needs_another_pass = any(
                section.needs_improvement 
                for section in grader_output.sections
            )
            status = "extracting" if needs_another_pass else "completed"
            error_message = None
        
        state_updates.update({
            "grader_output": grader_output,
            "status": status,
            "last_feedback": grader_output.overall_feedback,
            "error_message": error_message
        })
        
    except Exception as e:
        state_updates.update({
            "status": "failed",
            "error_message": str(e)
        })
    
    return state_updates