import pytest
from datetime import datetime, UTC
import json
from models.job_description_workflow_state import JobDescriptionProcessingState
from models.job_description_models import (
    JobDescription, JobMetadata, CompanyOverview, RoleSummary,
    ResponsibilitiesAndQualifications, CompensationAndBenefits,
    AdditionalInformation
)
from models.jobs_search_models import JobListing, JobHighlight, ApplyLink, DetectedExtensions
from agents.nodes import extraction_node, grader_node

# Sample job data using JobListing model
SAMPLE_JOB = JobListing(
    position=10,
    title="AI Engineer",
    company_name="Chai",
    location="Palo Alto, CA",
    via="Jobs",
    description="""Founded by a team of Cambridge ex quant-traders and researchers, with over 5 trillion tokens served per month to 5 million users, Chai has quickly established itself as the fastest-growing AI startup in Palo Alto.

We are looking for someone to run, optimize, and improve our revenue generation strategy. You will be responsible for moving us from $10 million in yearly revenue to $100 million.""",
    job_highlights=[
        JobHighlight(
            title="Qualifications",
            items=[
                "You have a track record of making money",
                "You are goal oriented and driven",
                "You have an excellent academic track record in a quantitative field"
            ]
        )
    ],
    extensions=["Full-time"],
    detected_extensions=DetectedExtensions(
        posted_at=None,
        schedule="Full-time",
        salary=None,
        health_insurance=None,
        dental_insurance=None,
        paid_time_off=None
    ),
    apply_link="https://jobs.ashbyhq.com/chai/3311b070-834b-435e-866c-76d774eef4dc",
    apply_links=[
        ApplyLink(
            link="https://jobs.ashbyhq.com/chai/3311b070-834b-435e-866c-76d774eef4dc",
            source="Jobs"
        )
    ],
    sharing_link="https://www.google.com/search?q=AI+Engineer+Palo+Alto+CA"
)

SAMPLE_STRUCTURED_JOB = JobDescription(
    metadata=JobMetadata(
        job_id=None,
        source_url=None,
        date_posted=None,
        apply_link=None,
        source_platform=None
    ),
    company_overview=CompanyOverview(
        company_name="Chai",
        about="Founded by a team of Cambridge ex quant-traders and researchers, with over 5 trillion tokens served per month to 5 million users, Chai has quickly established itself as the fastest-growing AI startup in Palo Alto.",
        mission_and_values=None,
        size=None,
        industry=None,
        locations="Palo Alto, CA"
    ),
    role_summary=RoleSummary(
        title="AI Engineer",
        job_level=None,
        role_type=None,
        employment_type=None,
        remote_options=None,
        team_or_department=None
    ),
    responsibilities_and_qualifications=ResponsibilitiesAndQualifications(
        responsibilities=[
            "Run, optimize, and improve our revenue generation strategy",
            "Move us from $10 million in yearly revenue to $100 million"
        ],
        required_qualifications=[
            "You have a track record of making money",
            "You are goal oriented and driven",
            "You have an excellent academic track record in a quantitative field"
        ],
        preferred_qualifications=None,
        tools_and_technologies=None
    ),
    compensation_and_benefits=CompensationAndBenefits(
        salary_range=None,
        bonus_and_equity=None,
        benefits_and_perks=None
    ),
    additional_information=AdditionalInformation(
        highlights=None,
        posting_age=None,
        application_instructions=None,
        recruitment_process=None
    )
)

@pytest.mark.asyncio
async def test_extraction_node():
    """Test the extraction of structured job information from raw data."""
    
    # Create initial state
    initial_state = JobDescriptionProcessingState(
        job_id="test_job_1",
        raw_job_data=SAMPLE_JOB.model_dump(),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    
    # Run extraction
    result_state = await extraction_node(initial_state)
    
    # Print detailed output
    print("\n=== Test Results ===")
    print(f"Status: {result_state.status}")
    print(f"Attempts: {result_state.attempts}")
    print(f"Error Message: {result_state.error_message}")
    print("\nStructured Job Output:")
    if result_state.structured_job:
        print(json.dumps(result_state.structured_job.model_dump(), indent=2))
    else:
        print("No structured job output generated")
    print("==================\n")
    
    # Basic assertions
    assert result_state is not None
    assert result_state.structured_job is not None
    assert result_state.error_message is None
    
    # Check specific fields
    structured_job = result_state.structured_job
    assert structured_job.company_overview.company_name == "Chai"
    assert structured_job.role_summary.title == "AI Engineer"
    assert "Palo Alto" in structured_job.company_overview.locations
    
    return result_state

@pytest.mark.asyncio
async def test_grader_node():
    """Test the grading of extracted job information."""
    
    # Create initial state with sample structured job
    initial_state = JobDescriptionProcessingState(
        job_id="test_job_1",
        raw_job_data=SAMPLE_JOB.model_dump(),
        structured_job=SAMPLE_STRUCTURED_JOB,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    
    # Run grader
    result_state = await grader_node(initial_state)
    
    # Print detailed output
    print("\n=== Grader Results ===")
    print(f"Status: {result_state.status}")
    print(f"Attempts: {result_state.attempts}")
    print(f"Error Message: {result_state.error_message}")
    print("\nGrader Output:")
    if result_state.grader_output:
        print(json.dumps(result_state.grader_output.model_dump(), indent=2))
    else:
        print("No grader output generated")
    print("==================\n")
    
    # Basic assertions
    assert result_state is not None
    assert result_state.grader_output is not None
    assert result_state.error_message is None
    
    # Check grading output
    grader_output = result_state.grader_output
    assert hasattr(grader_output, 'overall_grade'), "Grader output should have an overall grade"
    assert grader_output.overall_grade in ['A', 'B', 'C', 'D', 'F'], "Grade should be A-F"
    
    return result_state

if __name__ == "__main__":
    import asyncio
    
    async def run_tests():
        print("\nRunning extraction node test...")
        await test_extraction_node()
        
        print("\nRunning grader node test...")
        await test_grader_node()
    
    asyncio.run(run_tests())
