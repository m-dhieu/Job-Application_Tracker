from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ApplicationStatus(str, Enum):
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    REJECTED = "rejected"
    ACCEPTED = "accepted"
    WITHDRAWN = "withdrawn"

class EmploymentType(str, Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"

# User Models
class UserCreate(BaseModel):
    email: str = Field(..., description="Valid email address")
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)

class UserLogin(BaseModel):
    email: str = Field(..., description="Valid email address")
    password: str

class UserProfile(BaseModel):
    phone: Optional[str] = None
    location: Optional[str] = None
    resume_path: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    skills: Optional[List[str]] = None
    bio: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    created_at: Optional[str] = None
    last_login: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    resume_path: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    skills: Optional[List[str]] = None
    bio: Optional[str] = None

# Application Models
class JobApplicationCreate(BaseModel):
    job_title: str = Field(..., min_length=1, max_length=200)
    company_name: str = Field(..., min_length=1, max_length=100)
    job_url: Optional[str] = None
    status: ApplicationStatus = ApplicationStatus.APPLIED
    notes: Optional[str] = None
    salary_range: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[EmploymentType] = None
    source: Optional[str] = "manual"
    external_job_id: Optional[str] = None

class JobApplicationUpdate(BaseModel):
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    job_url: Optional[str] = None
    status: Optional[ApplicationStatus] = None
    notes: Optional[str] = None
    salary_range: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[EmploymentType] = None

class JobApplicationResponse(BaseModel):
    id: int
    user_id: int
    job_title: str
    company_name: str
    job_url: Optional[str] = None
    application_date: str
    status: str
    notes: Optional[str] = None
    salary_range: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    source: Optional[str] = None
    external_job_id: Optional[str] = None

class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus
    notes: Optional[str] = None

class ApplicationStatusHistory(BaseModel):
    id: int
    application_id: int
    status: str
    changed_at: str
    notes: Optional[str] = None

# Session Models
class LoginResponse(BaseModel):
    user: UserResponse
    session_token: str
    message: str

class SessionUser(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str

# Response Models
class MessageResponse(BaseModel):
    message: str
    success: bool = True

class ErrorResponse(BaseModel):
    message: str
    success: bool = False
    error_code: Optional[str] = None
