import json
import pytest
from datetime import datetime
from pathlib import Path

from models.job_description_workflow_state import JobDescriptionProcessingState, JobDescriptionProcessingStatus
from agents.job_description_graph import graph

@pytest.fixture
def test_job_data():
    """Load test job listing data from JSON file"""
    test_data_path = Path(__file__).parent.parent / "data" / "test_raw_job_listing.json"
    with open(test_data_path, 'r') as f:
        return json.load(f)

async def test_job_description_extraction_workflow(test_job_data):
    """
    Test the complete job description extraction workflow.
    Verifies that a job listing can be processed into structured data
    with appropriate grading feedback.
    """
    # Initialize workflow state
    initial_state = JobDescriptionProcessingState(
        job_id=str(test_job_data["_id"]["$oid"]),
        raw_job_data=test_job_data,
        status=JobDescriptionProcessingStatus.EXTRACTING,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Run the workflow
    final_state_dict = await graph.ainvoke(initial_state)
    final_state = JobDescriptionProcessingState(**final_state_dict)
    
    # Verify the workflow completed successfully
    assert final_state.status in (
        JobDescriptionProcessingStatus.COMPLETED,
        JobDescriptionProcessingStatus.FAILED
    )
    
    # If completed, verify we have structured data and grading
    if final_state.status == JobDescriptionProcessingStatus.COMPLETED:
        # Check structured data
        assert final_state.structured_job is not None
        structured_job = final_state.structured_job
        
        # Verify key job details were extracted correctly
        assert structured_job.role_summary.title == test_job_data["title"]
        assert structured_job.company_overview.company_name == test_job_data["company_name"]
        
        # Verify grading output exists and has valid grade
        assert final_state.grader_output is not None
        assert final_state.grader_output.overall_grade in ("A", "B")
