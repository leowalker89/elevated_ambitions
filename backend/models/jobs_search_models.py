from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class SearchMetadata(BaseModel):
    """Metadata about the search request and response"""
    id: str
    status: str
    created_at: datetime
    request_time_taken: float
    parsing_time_taken: float
    total_time_taken: float
    request_url: str
    html_url: str
    json_url: str

class SearchParameters(BaseModel):
    """Parameters used for the search"""
    engine: str
    q: str  # search query
    google_domain: str
    hl: str  # language
    gl: str  # geography/location

class SearchInformation(BaseModel):
    """Information about the search results"""
    query_displayed: str
    detected_location: str

class JobHighlight(BaseModel):
    """Highlights/sections of a job posting"""
    title: str
    items: List[str]

class DetectedExtensions(BaseModel):
    """Detected metadata about the job"""
    posted_at: Optional[str] = None
    schedule: Optional[str] = None
    salary: Optional[str] = None
    health_insurance: Optional[bool] = None
    dental_insurance: Optional[bool] = None
    paid_time_off: Optional[bool] = None

class ApplyLink(BaseModel):
    """Links to apply for the job"""
    link: str
    source: str

class JobListing(BaseModel):
    """Individual job posting"""
    position: int
    title: str
    company_name: str
    location: str
    via: str
    description: str
    job_highlights: List[JobHighlight]
    extensions: Optional[List[str]] = None
    detected_extensions: Optional[DetectedExtensions] = None
    apply_link: str
    apply_links: List[ApplyLink]
    sharing_link: str

class JobSearchResponse(BaseModel):
    """Complete response from the Google Jobs API"""
    search_metadata: SearchMetadata
    search_parameters: SearchParameters
    search_information: SearchInformation
    jobs: List[JobListing]