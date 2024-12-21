from langgraph.graph import StateGraph, START, END
from datetime import datetime

from models.job_description_workflow_state import JobDescriptionProcessingState, ProcessingStatusType
from .nodes import extraction_node, grader_node

def should_continue(state: JobDescriptionProcessingState) -> str:
    """
    Determines the next step in the workflow based on current state.
    
    Args:
        state: Current workflow state containing status, grade, and attempt info
        
    Returns:
        str: Name of the next node to execute or END
    """
    # Check for failure or completion first
    if state.status in ("failed", "completed"):
        return END
        
    # If we're in extracting state, move to grading
    if state.status == "extracting":
        return "grade_extraction"
        
    # If we're in grading state, check grade and attempts
    if state.status == "grading":
        if state.grader_output and state.grader_output.overall_quality_score >= 0.8:
            return END
            
        if state.attempts >= state.max_attempts:
            return END
            
        # Otherwise, try extraction again
        return "extract_job"
        
    # Default to extraction
    return "extract_job"

# Build the graph
workflow = StateGraph(JobDescriptionProcessingState)

# Add nodes
workflow.add_node("extract_job", extraction_node)
workflow.add_node("grade_job", grader_node)

# Add edges
workflow.add_edge(START, "extract_job")
workflow.add_edge("extract_job", "grade_job")
workflow.add_conditional_edges(
    "grade_job",
    should_continue,
    {
        "extract_job": "extract_job",
        END: END
    }
)

# Compile the graph
graph = workflow.compile()
