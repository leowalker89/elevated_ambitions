from typing import List, Optional
from pydantic import BaseModel, Field

class CompanyOverview(BaseModel):
    """
    Captures key information about the hiring organization.
    This provides context about the company's profile, culture, and operating environment
    to help candidates assess organizational fit.
    """
    company_name: Optional[str] = Field(None, description="Company name.")
    about: Optional[str] = Field(None, description="Company overview from provided information.")
    mission_and_values: Optional[str] = Field(None, description="Company mission, vision, or values if stated.")
    size: Optional[str] = Field(None, description="Company size details if provided.")
    industry: Optional[str] = Field(
        None, 
        description="Primary industry if stated. Common values: tech, finance, healthcare, education, "
                   "manufacturing, ecommerce, media, entertainment, government, consulting, retail, "
                   "energy, telecom, transportation, real_estate, consumer_goods, biotech, "
                   "pharmaceuticals, non_profit. Use best match or 'other' if none fit."
    )
    locations: Optional[str] = Field(None, description="Company or role location(s) if mentioned.")

class RoleSummary(BaseModel):
    """
    Provides a high-level overview of the position being offered.
    This summary helps candidates quickly understand the role's scope,
    level, and basic working arrangements.
    """
    title: str = Field(..., description="Job title as stated.")
    job_level: Optional[str] = None
    role_type: Optional[str] = Field(
        None, 
        description="Role type if explicitly mentioned. Common values: individual_contributor, "
                   "management, executive_management. Use best match based on context."
    )
    employment_type: Optional[str] = Field(None, description="Employment type (e.g., full-time) if stated.")
    remote_options: Optional[str] = Field(None, description="e.g., 'remote', 'on-site', 'hybrid' if stated.")
    team_or_department: Optional[str] = Field(None, description="Team or department name if mentioned.")

class JobMetadata(BaseModel):
    """
    Contains administrative and source information about a job posting.
    This metadata helps track and manage job postings across different platforms
    and maintain data provenance.
    """
    job_id: Optional[str] = Field(None, description="Unique job ID if provided.")
    source_url: Optional[str] = Field(None, description="URL of the original posting if available.")
    date_posted: Optional[str] = Field(None, description="Date the job was posted, e.g. '2024-05-01'.")
    apply_link: Optional[str] = Field(None, description="Direct link to apply for the job if provided.")
    source_platform: Optional[str] = Field(None, description="Platform or job board where this posting originated.")

class ResponsibilitiesAndQualifications(BaseModel):
    """
    Details the core expectations and requirements for the role.
    This section helps candidates evaluate their fit for the position
    based on their skills, experience, and capabilities.
    """
    responsibilities: Optional[List[str]] = Field(None, description="List of responsibilities if provided.")
    required_qualifications: Optional[List[str]] = Field(None, description="Essential qualifications if stated.")
    preferred_qualifications: Optional[List[str]] = Field(None, description="Preferred qualifications if stated.")
    tools_and_technologies: Optional[List[str]] = Field(None, description="Mentioned tools, languages, frameworks.")

class CompensationAndBenefits(BaseModel):
    """
    Outlines the total compensation package offered.
    This information helps candidates evaluate the financial and
    lifestyle benefits associated with the position.
    """
    salary_range: Optional[str] = Field(None, description="Stated pay range if provided.")
    bonus_and_equity: Optional[str] = Field(None, description="Bonus, equity, or RSU info if mentioned.")
    benefits_and_perks: Optional[List[str]] = Field(None, description="List of benefits and perks if stated.")

class AdditionalInformation(BaseModel):
    """
    Contains supplementary details about the role and application process.
    This section captures important information that doesn't fit into
    other categories but may be valuable for candidates.
    """
    highlights: Optional[List[str]] = Field(None, description="Unique highlights if any.")
    posting_age: Optional[str] = Field(None, description="e.g., '3 weeks ago' if provided.")
    application_instructions: Optional[str] = Field(None, description="Special apply instructions if stated.")
    recruitment_process: Optional[str] = Field(None, description="Notes on interview or hiring process if given.")

class JobDescription(BaseModel):
    """
    A comprehensive, structured representation of a job posting.
    This model organizes all aspects of a job posting into logical sections,
    making it easier to process, analyze, and present job information consistently.
    
    Required fields:
    - role_summary: Contains essential job information like title and level
    
    Optional fields:
    - All other sections that may not be present in every job posting
    """
    metadata: Optional[JobMetadata] = None
    company_overview: Optional[CompanyOverview] = None
    role_summary: RoleSummary  # Required field
    responsibilities_and_qualifications: Optional[ResponsibilitiesAndQualifications] = None
    compensation_and_benefits: Optional[CompensationAndBenefits] = None
    additional_information: Optional[AdditionalInformation] = None


class GraderOutput(BaseModel):
    """Simple grader output with just score and feedback."""
    overall_quality_score: float = Field(ge=0.0, le=1.0)
    overall_feedback: str