from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional, Dict

# The following classes are for the resume template

class ContactInfo(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None

class PersonalDetails(BaseModel):
    full_name: str
    contact_info: ContactInfo
    professional_summary: Optional[str] = None

class Education(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    graduation_date: Optional[str] = None

class WorkExperience(BaseModel):
    company: Optional[str] = None
    title: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None
    notable_contributions: Optional[List[str]] = None

class Project(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    technologies: Optional[str] = None
    role: Optional[str] = None

class Certification(BaseModel):
    title: Optional[str] = None
    certifying_body: Optional[str] = None
    date: Optional[str] = None

class Publication(BaseModel):
    title: Optional[str] = None
    co_authors: List[str] = []
    date: Optional[str] = None

class Award(BaseModel):
    title: Optional[str] = None
    awarding_body: Optional[str] = None
    date: Optional[str] = None

class VolunteerExperience(BaseModel):
    organization: Optional[str] = None
    role: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None

class AdditionalSections(BaseModel):
    volunteer_experience: Optional[List[VolunteerExperience]] = []
    languages: Optional[List[str]] = []
    interests: Optional[List[str]] = []

class Resume(BaseModel):
    personal_details: PersonalDetails
    education: List[Education] = []
    work_experience: List[WorkExperience] = []
    projects: List[Project] = []
    skills: List[str] = []
    certifications: List[Certification] = []
    publications: List[Publication] = []
    awards: List[Award] = []
    additional_sections: Optional[AdditionalSections] = None

## the following classes are for the interview profile
class InterviewResponse(BaseModel):
    background: Optional[str] = None
    question: str
    answer: str

class InterviewProfile(BaseModel):
    responses: Dict[str, List[InterviewResponse]] = Field(default_factory=dict)
