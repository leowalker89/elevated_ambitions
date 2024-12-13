from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field

class RoleTypeEnum(str, Enum):
    """
    Indicates the general role type.
    If not explicitly stated, leave as None.
    """
    IC = "individual_contributor"
    MANAGEMENT = "management"
    EXECUTIVE_MANAGEMENT = "executive_management"

class IndustryEnum(str, Enum):
    """
    A broad enumeration of possible industries.
    If not clearly stated, leave as None.
    """
    TECH = "tech"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    MANUFACTURING = "manufacturing"
    ECOMMERCE = "ecommerce"
    MEDIA = "media"
    ENTERTAINMENT = "entertainment"
    GOVERNMENT = "government"
    CONSULTING = "consulting"
    RETAIL = "retail"
    ENERGY = "energy"
    TELECOM = "telecom"
    TRANSPORTATION = "transportation"
    REAL_ESTATE = "real_estate"
    CONSUMER_GOODS = "consumer_goods"
    BIOTECH = "biotech"
    PHARMACEUTICALS = "pharmaceuticals"
    NON_PROFIT = "non_profit"
    OTHER = "other"

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
    industry: Optional[IndustryEnum] = Field(None, description="Primary industry if stated. Use enum if provided explicitly, else None.")
    locations: Optional[str] = Field(None, description="Company or role location(s) if mentioned.")

class RoleSummary(BaseModel):
    """
    Provides a high-level overview of the position being offered.
    This summary helps candidates quickly understand the role's scope,
    level, and basic working arrangements.
    """
    title: str = Field(..., description="Job title as stated.")
    job_level: Optional[str] = None
    role_type: Optional[RoleTypeEnum] = Field(None, description="Role type if explicitly mentioned.")
    employment_type: Optional[str] = Field(None, description="Employment type (e.g., full-time) if stated.")
    remote_options: Optional[str] = Field(None, description="e.g., 'remote', 'on-site', 'hybrid' if stated.")
    team_or_department: Optional[str] = Field(None, description="Team or department name if mentioned.")

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
    Use this class when parsing job descriptions or creating structured job postings.
    """
    metadata: JobMetadata
    company_overview: CompanyOverview
    role_summary: RoleSummary
    responsibilities_and_qualifications: ResponsibilitiesAndQualifications
    compensation_and_benefits: CompensationAndBenefits
    additional_information: AdditionalInformation

class GradeEnum(str, Enum):
    """
    Standardized letter grades for evaluating parsing quality.
    Definitions:
    - A: Exceptional - no significant issues
    - B: Good - minor issues
    - C: Acceptable - noticeable issues but still usable
    - D: Needs Improvement - major issues
    - F: Failed - critical problems preventing use
    """
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"

class GradingSection(BaseModel):
    """
    Evaluation of a specific section of annotated job data.
    Each rating is a letter grade (A, B, C, D, F).

    Field Guidelines:
    - accuracy_rating: Reflects how closely the extracted data matches the source.
      A: Perfect match, F: Severe inaccuracies.
    - assumption_rating: Reflects how well unsupported assumptions are avoided.
      A: No unfounded assumptions, F: Multiple unsupported details.
    - clarity_rating: Reflects how understandable the extracted data is.
      A: Very clear, F: Confusing or unclear.
    - conciseness_rating: Reflects how succinct and relevant the data is.
      A: Well-optimized, F: Overly verbose or too sparse.
    """
    section_name: str = Field(..., description="Name of the section being evaluated.")
    accuracy_rating: GradeEnum = Field(..., description="Accuracy of the extraction.")
    assumption_rating: GradeEnum = Field(..., description="Avoidance of unwarranted assumptions.")
    clarity_rating: GradeEnum = Field(..., description="Clarity of the extracted data.")
    conciseness_rating: GradeEnum = Field(..., description="Conciseness of the extracted data.")
    feedback: Optional[str] = Field(None, description="Additional comments on this section.")

class GraderOutput(BaseModel):
    """
    Comprehensive evaluation of the entire annotation.

    sections: Individual section evaluations.
    overall_grade: Summarizes the overall quality using the same A-F scale.
    - A: Exceptional across most or all sections
    - B: Generally good, minor improvements needed
    - C: Acceptable but requires improvements
    - D: Significant issues found
    - F: Critical failures present

    overall_feedback: General comments on the entire annotation.
    """
    sections: List[GradingSection] = Field(..., description="List of graded sections.")
    overall_grade: GradeEnum = Field(..., description="Overall letter grade for the annotation.")
    overall_feedback: Optional[str] = Field(None, description="Overall feedback and suggestions.")