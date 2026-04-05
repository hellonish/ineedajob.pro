from pydantic import BaseModel, Field
from typing import Dict, List, Optional

# USER PROFILE MODELS

class Education(BaseModel):
    """One education entry: degree, school, dates, and optional details."""

    school: str = Field(description="Full name of the institution (university, college, school).")
    degree: str = Field(description="Degree or qualification earned (e.g. B.S., M.A., PhD, High School Diploma).")
    field_of_study: str = Field(description="Major, discipline, or program name (e.g. Computer Science, Economics).")
    start_date: str = Field(description="When the education started. Use consistent format: YYYY-MM or 'Month YYYY'.")
    end_date: Optional[str] = Field(default=None, description="When it ended. Use 'present' or leave empty if ongoing.")
    description: Optional[str] = Field(default=None, description="Optional notes: thesis, honors, relevant coursework, activities.")
    subjects: List[str] = Field(default_factory=list, description="List of subjects, courses, or focus areas.")


class Experience(BaseModel):
    """One work or professional experience entry."""

    company: str = Field(description="Name of the employer or organization.")
    title: str = Field(description="Job title or role (e.g. Software Engineer, Intern).")
    location: str = Field(description="City, region, or country where the role was based; empty string if remote/unspecified.")
    start_date: str = Field(description="When the role started. Use consistent format: YYYY-MM or 'Month YYYY'.")
    end_date: Optional[str] = Field(default=None, description="When it ended. Use 'present' if current role.")
    description: Optional[str] = Field(default=None, description="Responsibilities, achievements, and key contributions in full.")
    urls: List[str] = Field(default_factory=list, description="Relevant links (company page, project, article).")
    skills: List[str] = Field(default_factory=list, description="Technologies, tools, or skills used in this role.")


class Project(BaseModel):
    """One project (personal, academic, or professional)."""

    name: str = Field(description="Project title or name.")
    description: str = Field(description="What the project does, your role, and outcomes. Full text, no truncation.")
    urls: List[str] = Field(default_factory=list, description="Links to repo, demo, write-up, or live project.")
    skills: List[str] = Field(default_factory=list, description="Technologies and skills used in the project.")


class SkillGroup(BaseModel):
    """Skills grouped by category. Key = category name (e.g. 'Programming', 'Tools'), value = list of skill strings."""

    skills: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Map of category name to list of skills. E.g. {'Programming': ['Python', 'JavaScript'], 'Tools': ['Git', 'Docker']}.",
    )


class Extracurricular(BaseModel):
    """Extracurricular activity: club, volunteer work, hobby, or side activity."""

    name: str = Field(description="Name of the activity, club, or organization.")
    description: str = Field(description="What you did, your role, and impact.")
    urls: List[str] = Field(default_factory=list, description="Relevant links.")
    skills: List[str] = Field(default_factory=list, description="Skills gained or used.")


class Certification(BaseModel):
    """Professional or educational certification."""

    name: str = Field(description="Full name of the certification (e.g. AWS Solutions Architect, PMP).")
    description: str = Field(description="Issuing body, scope, or what it certifies.")
    urls: List[str] = Field(default_factory=list, description="Link to credential or issuer.")
    skills: List[str] = Field(default_factory=list, description="Skills or domains the certification covers.")
    datetime: str = Field(description="When obtained. Use YYYY-MM or 'Month YYYY'.")


class Award(BaseModel):
    """Award, honor, or recognition."""

    name: str = Field(description="Name of the award or honor.")
    description: str = Field(description="Who gave it, for what, and context.")
    urls: List[str] = Field(default_factory=list, description="Link to announcement or details.")
    skills: List[str] = Field(default_factory=list, description="Relevant skills or domain.")
    datetime: str = Field(description="When received. Use YYYY-MM or 'Month YYYY'.")


class Person(BaseModel):
    """Structured profile of a person: contact, summary, work history, education, skills, projects, and more."""

    name: str = Field(description="Full name of the person.")
    headline: str = Field(description="Short professional headline or tagline (e.g. 'Senior Engineer | ML & Systems').")
    summary: str = Field(description="Professional summary or about section in full; do not truncate.")
    location: str = Field(description="Current or primary location (city, region, country).")
    company: str = Field(description="Current or most recent employer/organization name.")
    title: str = Field(description="Current or most recent job title.")
    email: str = Field(description="Primary email address; empty string if not found.")
    phone: str = Field(description="Primary phone number; empty string if not found.")
    website: str = Field(description="Personal or professional website URL; empty string if not found.")
    languages: List[str] = Field(default_factory=list, description="Spoken languages (e.g. English, Hindi).")
    extracurriculars: List[Extracurricular] = Field(default_factory=list, description="Clubs, volunteer work, hobbies, side activities.")
    skills: SkillGroup = Field(
        default_factory=lambda: SkillGroup(skills={}),
        description="Skills grouped by category. Use empty dict {} if none extracted.",
    )
    social_media: List[str] = Field(default_factory=list, description="URLs to LinkedIn, GitHub, Twitter, etc.")
    educations: List[Education] = Field(default_factory=list, description="Education history, most recent first if order is known.")
    experiences: List[Experience] = Field(default_factory=list, description="Work experience, most recent first if order is known.")
    projects: List[Project] = Field(default_factory=list, description="Notable projects with full descriptions.")
    certifications: List[Certification] = Field(default_factory=list, description="Certifications and credentials.")
    awards: List[Award] = Field(default_factory=list, description="Awards, honors, and recognition.")


# JOB POSTING + COMPANY MODELS

class Compensation(BaseModel):
    """Salary range and currency for a job."""

    min_salary: Optional[float] = Field(None, description="Minimum salary offered")
    max_salary: Optional[float] = Field(None, description="Maximum salary offered")
    currency: str = Field("USD", description="Currency of the compensation")
    details: Optional[str] = Field(None, description="Extra details, e.g., 'uncapped commission', 'equity options'")

class FundingInfo(BaseModel):
    """Funding and investor information for a company."""

    stage: Optional[str] = Field(None, description="E.g., Public Company, Growth Stage")
    total_funding_amount: Optional[str] = Field(None, description="E.g., '$4.92B'")
    key_investors: List[str] = Field(default_factory=list, description="List of key investor names")
    recent_events: List[str] = Field(default_factory=list, description="Recent funding rounds or grants")

class Leadership(BaseModel):
    """One leadership team member."""

    name: str = Field(description="Full name of the leader")
    role: str = Field(description="Job title or role at the company")

class NewsArticle(BaseModel):
    """One recent news item about the company."""

    title: str = Field(description="Headline or title of the article")
    source: Optional[str] = Field(None, description="Publication or source name")
    date: Optional[str] = Field(None, description="Publication date (YYYY-MM or free form)")

class Company(BaseModel):
    """Structured company profile: name, about, location, size, funding, leadership, news."""

    name: str = Field(description="Official name of the company")
    about: Optional[str] = Field(None, description="General description of the company")
    founded_year: Optional[int] = Field(None, description="Year the company was founded")
    headquarters: Optional[str] = Field(None, description="Headquarters location (city, country)")
    employee_count: Optional[str] = Field(None, description="E.g., '10001+ employees'")
    glassdoor_rating: Optional[float] = Field(None, description="Glassdoor rating if known")
    website: Optional[str] = Field(None, description="Company website URL (use empty string if unknown)")
    funding_info: Optional[FundingInfo] = Field(None, description="Funding stage and investor info")
    leadership_team: List[Leadership] = Field(default_factory=list, description="Key executives or leadership")
    recent_news: List[NewsArticle] = Field(default_factory=list, description="Recent news or press items")

class H1BSponsorship(BaseModel):
    """H1B visa sponsorship information."""

    likely_sponsor: Optional[bool] = Field(None, description="Indicator if the company is likely to sponsor H1B")
    historical_trends: Optional[Dict[str, int]] = Field(
        None,
        description="Year (as string, e.g. '2023') to total sponsorships count; JSON-safe",
    )

class PlatformMetadata(BaseModel):
    """Platform-specific match and scoring metadata."""

    match_percentage: Optional[int] = Field(None, description="Overall match score from the platform")
    exp_level_match: Optional[int] = Field(None, description="Experience level match score")
    skill_match: Optional[int] = Field(None, description="Skill match score")
    industry_exp_match: Optional[int] = Field(None, description="Industry experience match score")
    insider_connections_count: Optional[int] = Field(None, description="Number of insider connections")

class JobListing(BaseModel):
    """A single job posting: title, company, location, role details, compensation, and metadata."""

    job_title: str = Field(description="Title of the job (e.g. Senior Software Engineer)")
    company: Company = Field(description="Company offering the job")
    location: str = Field(description="Job location (city, region, or 'Remote')")
    url: Optional[str] = Field(None, description="URL of the job posting on the source platform")
    posted_at: Optional[str] = Field(None, description="When the job was posted (YYYY-MM-DD or free form)")
    job_type: Optional[str] = Field(None, description="E.g., Full-time, Part-time, Internship, Contract")
    work_model: Optional[str] = Field(None, description="E.g., Onsite, Hybrid, Remote")
    experience_level: Optional[str] = Field(None, description="E.g., Entry Level, 1-3+ years, 15+ years")

    compensation: Optional[Compensation] = Field(None, description="Salary range and currency if disclosed")

    about_the_role: Optional[str] = Field(None, description="General intro or summary of the position")
    responsibilities: List[str] = Field(default_factory=list, description="List of duties and day-to-day tasks")

    qualifications_required: List[str] = Field(default_factory=list, description="Hard requirements for the role")
    qualifications_preferred: List[str] = Field(default_factory=list, description="Nice-to-have skills")
    skills_tags: List[str] = Field(default_factory=list, description="Keywords/tags from the post (e.g., Python, SQL)")

    benefits: List[str] = Field(default_factory=list, description="Perks, health insurance, PTO, etc.")
    application_instructions: Optional[str] = Field(None, description="How to apply, e.g. 'email resume to X'")

    h1b_sponsorship: Optional[H1BSponsorship] = Field(None, description="H1B sponsorship info if known")
    platform_metadata: Optional[PlatformMetadata] = Field(None, description="Metadata specific to the job board")