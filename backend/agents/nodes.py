from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from typing import Dict, Optional
from langchain.prompts import ChatPromptTemplate

from models.job_description_models import JobDescription, GraderOutput
from models.job_description_workflow_state import JobDescriptionProcessingState, JobDescriptionProcessingStatus
from models.jobs_search_models import JobListing
from prompts.job_description_processing import job_description_annotator, job_description_grader

load_dotenv()

async def extraction_node(state: JobDescriptionProcessingState) -> JobDescriptionProcessingState:
    """
    Extract structured job information from raw job listing data.
    
    Args:
        state: Current workflow state containing raw job data and processing history
        
    Returns:
        Updated workflow state with structured job information
    """
    # Build context for the prompt
    context = {
        "raw_job": state.raw_job_data,
        "attempt_number": state.attempts + 1,
        "previous_feedback": state.last_feedback if state.last_feedback else "None",
        "previous_structured_job": state.structured_job.dict() if state.structured_job else "None",
        "previous_grader_output": state.grader_output.dict() if state.grader_output else "None"
    }
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", job_description_annotator),
        ("user", """
        Please parse this job listing into a structured format. Here's the context:
        
        Raw Job Data: {raw_job}
        Attempt Number: {attempt_number}
        Previous Feedback: {previous_feedback}
        Previous Structured Job: {previous_structured_job}
        Previous Grader Output: {previous_grader_output}
        """)
    ])

    # Set up the model with structured output
    extraction_model = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        max_retries=2,
        stop_sequences=None,
    ).with_structured_output(JobDescription)
    
    try:
        # Update state status
        state.status = JobDescriptionProcessingStatus.EXTRACTING
        state.attempts += 1
        
        # Generate the structured job description
        chain = prompt | extraction_model
        structured_job = await chain.ainvoke(context)
        
        # Update state with structured job
        state.structured_job = structured_job
        
        return state
        
    except Exception as e:
        state.status = JobDescriptionProcessingStatus.FAILED
        state.error_message = str(e)
        return state

async def grader_node(state: JobDescriptionProcessingState) -> JobDescriptionProcessingState:
    """
    Grade the quality of the structured job extraction.
    
    Args:
        state: Current workflow state containing structured job data
        
    Returns:
        Updated workflow state with grading results
    """
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", job_description_grader),
        ("user", """
        Please grade the following job description extraction:
        
        Original Job Listing: {raw_job}
        Structured Output: {structured_job}
        """)
    ])
    
    # Set up the model with structured output
    grader_model = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        max_retries=2,
        stop_sequences=None,
    ).with_structured_output(GraderOutput)
    
    try:
        # Update state status
        state.status = JobDescriptionProcessingStatus.GRADING
        
        # Generate the grading output
        chain = prompt | grader_model
        grader_output = await chain.ainvoke({
            "raw_job": state.raw_job_data,
            "structured_job": state.structured_job
        })
        print("Grader Output:")
        print(grader_output)
        # Update state with grader output
        state.grader_output = grader_output
        
        # Determine next steps based on grade
        grader_dict = grader_output.model_dump() if hasattr(grader_output, 'model_dump') else grader_output
        if grader_dict['overall_grade'] in ['A', 'B']:
            state.status = JobDescriptionProcessingStatus.COMPLETED
        elif state.attempts >= state.max_attempts:
            state.status = JobDescriptionProcessingStatus.FAILED
            state.error_message = "Max attempts reached without achieving satisfactory grade"
        else:
            state.status = JobDescriptionProcessingStatus.PENDING
            state.last_feedback = grader_output.overall_feedback
        
        return state
        
    except Exception as e:
        state.status = JobDescriptionProcessingStatus.FAILED
        state.error_message = str(e)
        return state