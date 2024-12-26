from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from typing import Dict
from langchain.prompts import ChatPromptTemplate
from datetime import datetime

from backend.models.job_description_models import JobDescription, GraderOutput
from backend.models.job_description_workflow_state import JobDescriptionProcessingState
from backend.prompts.job_description_processing import job_description_annotator, job_description_grader

load_dotenv()

async def extraction_node(state: JobDescriptionProcessingState) -> dict:
    """Extract structured job information from raw job listing data."""
    state_updates = {
        "status": "extracting",
        "attempts": state.attempts + 1,
        "updated_at": datetime.now()
    }
    
    try:
        context = {
            "raw_job": state.raw_job_data,
            "attempt_number": state.attempts + 1,
            "previous_feedback": state.grader_output.overall_feedback if state.grader_output else "None",
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
            "status": "grading",
            "error_message": None
        })
        
    except Exception as e:
        state_updates.update({
            "status": "failed",
            "error_message": str(e)
        })
    
    return state_updates

async def grader_node(state: JobDescriptionProcessingState) -> dict:
    """Grade the quality of the structured job extraction using a lighter model."""
    state_updates = {
        "updated_at": datetime.now()
    }
    
    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", job_description_grader),
            ("user", """
            Original Job Listing: {raw_job}
            Extracted Job Description: {structured_job}
            """)
        ])
        
        grader_model = ChatGroq(
            model="llama-3.1-8b-instant",  # Using faster 8B model for grading
            temperature=0.1,
            max_retries=2,
            stop_sequences=None
        ).with_structured_output(GraderOutput)
        
        grader_output = await (prompt | grader_model).ainvoke({
            "raw_job": state.raw_job_data,
            "structured_job": state.structured_job
        })
        
        # Simple status determination based on quality score
        if grader_output.overall_quality_score >= 0.8:
            status = "completed"
            error_message = None
        elif state.attempts >= state.max_attempts:
            status = "failed"
            error_message = f"Max attempts reached. Final quality score: {grader_output.overall_quality_score}"
        else:
            status = "extracting"
            error_message = None
        
        state_updates.update({
            "grader_output": grader_output,
            "status": status,
            "error_message": error_message
        })
        
    except Exception as e:
        state_updates.update({
            "status": "failed",
            "error_message": str(e)
        })
    
    return state_updates