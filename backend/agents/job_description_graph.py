from langgraph.graph import StateGraph, START, END
from datetime import datetime

from backend.models.job_description_workflow_state import JobDescriptionProcessingState
from backend.agents.nodes import extraction_node, grader_node

def should_continue(state: JobDescriptionProcessingState) -> str:
    """
    Determines if we should continue extraction or end the workflow.
    Only called after grading to decide next step.
    """
    # First check terminal states
    if state.status in ("failed", "completed"):
        return END
        
    # Check grading results
    if state.grader_output:
        # High quality - we're done
        if state.grader_output.overall_quality_score >= 0.9:
            state.status = "completed"
            return END
            
        # Max attempts reached - end with current result
        if state.attempts >= state.max_attempts:
            state.status = "failed"
            return END
            
        # Quality not good enough - try extraction again
        state.status = "extracting"
        return "extract_job"
    
    # Shouldn't get here, but default to extraction if we do
    return "extract_job"

def create_job_description_graph() -> StateGraph:
    """
    Creates and returns a compiled job description processing graph.
    """
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
    
    return workflow.compile()
