"""JobLens Engine Models - Pydantic schemas for the 6-step job application pipeline."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# ============================================================================
# STEP 1: Extract Profile
# ============================================================================

class TechnicalSkills(BaseModel):
    languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    cloud: List[str] = Field(default_factory=list)
    ai_ml: List[str] = Field(default_factory=list)
    devops: List[str] = Field(default_factory=list)
    other: List[str] = Field(default_factory=list)

class KeyExperience(BaseModel):
    company: str
    title: str
    duration: str
    key_achievements: List[str] = Field(..., description="2-3 top achievements with metrics")

class NotableProject(BaseModel):
    name: str
    description: str
    tech_stack: List[str]
    url: Optional[str] = None

class ExtractedProfile(BaseModel):
    """Step 1 output: Structured profile optimized for job applications."""
    current_title: str
    years_of_experience: int
    primary_role_type: str = Field(..., description="SWE / AI-ML / Backend / Cloud / DevOps / Full-Stack / Frontend / Data / Mobile")
    technical_skills: TechnicalSkills
    top_experiences: List[KeyExperience] = Field(..., description="Top 3-5 most relevant experiences")
    notable_projects: List[NotableProject] = Field(default_factory=list)
    open_source_contributions: List[str] = Field(default_factory=list)
    publications_or_talks: List[str] = Field(default_factory=list)
    professional_summary: str = Field(..., description="2-3 sentence professional summary")
    ai_verdict: str = Field(..., description="Rich text analysis of the candidate's profile - strengths, positioning advice, standout qualities")


# ============================================================================
# STEP 2: Parse JD
# ============================================================================

class ParsedJD(BaseModel):
    """Step 2 output: Fully parsed job description."""
    company_name: str
    role_title: str
    level: str = Field(..., description="junior / mid / senior / staff / lead / principal")
    location: str
    remote_policy: str = Field(..., description="remote / hybrid / onsite / not specified")
    required_skills: List[str]
    nice_to_have_skills: List[str]
    tech_stack: List[str]
    years_experience_required: str
    key_responsibilities: List[str]
    culture_signals: List[str] = Field(..., description="What kind of person/team this is")
    green_flags: List[str] = Field(..., description="Reasons this looks like a good opportunity")
    red_flags: List[str] = Field(..., description="Anything vague, concerning, or worth asking about")
    ats_keywords: List[str] = Field(..., description="Keywords critical for ATS screening")
    salary_range: Optional[str] = None
    role_summary: str = Field(..., description="2-sentence summary of what this role is really looking for")
    ai_verdict: str = Field(..., description="Rich analysis of the JD - what it reveals about the company, hidden requirements, and what to watch for")


# ============================================================================
# STEP 3: Company Intel
# ============================================================================

class CompanyIntel(BaseModel):
    """Step 3 output: Company research and intelligence."""
    company_description: str = Field(..., description="What the company actually does, not just their tagline")
    funding_stage: str = Field(default="Unknown")
    company_size: str = Field(default="Unknown")
    key_investors: List[str] = Field(default_factory=list)
    tech_stack_and_infra: List[str] = Field(default_factory=list)
    engineering_culture: str = Field(..., description="How they work, deploy, make decisions")
    recent_news: List[str] = Field(default_factory=list, description="Recent news, product launches, or leadership changes")
    interview_process: str = Field(default="Unknown", description="Typical interview stages, formats, difficulty")
    employee_sentiment: str = Field(default="Unknown", description="Why engineers join vs why they leave")
    competitors: List[str] = Field(default_factory=list)
    market_position: str = Field(default="Unknown")
    talking_points: List[str] = Field(..., description="Things to bring up in interviews to show homework")
    watch_outs: List[str] = Field(default_factory=list, description="Things to watch out for before accepting")
    ai_verdict: str = Field(..., description="Overall company assessment - opportunity quality, culture fit signals, and strategic advice")


# ============================================================================
# STEP 4: Match Analysis
# ============================================================================

class StrengthItem(BaseModel):
    area: str
    detail: str = Field(..., description="Specific evidence from background that matches JD requirement")

class GapItem(BaseModel):
    area: str
    severity: str = Field(..., description="critical / moderate / minor")
    detail: str
    quick_fix: str = Field(..., description="What to do about it before applying or how to address in interview")

class MatchAnalysis(BaseModel):
    """Step 4 output: Profile vs JD comparison with honest scoring."""
    technical_score: int = Field(..., ge=0, le=100)
    experience_score: int = Field(..., ge=0, le=100)
    project_relevance_score: int = Field(..., ge=0, le=100)
    culture_fit_score: int = Field(..., ge=0, le=100)
    overall_score: int = Field(..., ge=0, le=100)
    strengths: List[StrengthItem] = Field(..., description="Specific matches between background and JD")
    gaps: List[GapItem] = Field(..., description="Missing or weak areas with severity and remediation")
    unique_angles: List[str] = Field(..., description="What makes this candidate different from others")
    verdict: str = Field(..., description="Strong Fit / Good Fit / Stretch / Long Shot")
    tailored_pitch: str = Field(..., description="3-4 sentence first-person pitch specific to this company and role")
    ai_verdict: str = Field(..., description="Honest, detailed assessment with strategic advice on positioning")


# ============================================================================
# STEP 5: Contact Strategy
# ============================================================================

class ContactTarget(BaseModel):
    title: str = Field(..., description="Their likely title")
    why_they_matter: str
    priority: str = Field(..., description="high / medium / low")
    where_to_find: str = Field(..., description="LinkedIn search query, GitHub, Twitter/X, company website")
    outreach_message: str = Field(..., description="60-70 word DM/email. Specific to company. Include [YOUR_NAME] placeholder")
    approach: str = Field(..., description="cold message / mutual connection / comment on content / open source contribution")

class ContactStrategy(BaseModel):
    """Step 5 output: Who to contact and how."""
    contacts: List[ContactTarget] = Field(..., description="3-5 key contacts to reach")
    communities: List[str] = Field(default_factory=list, description="Slack, Discord, meetups where this company's engineers hang out")
    referral_strategy: str = Field(..., description="How to get a referral at this company specifically")
    networking_importance: str = Field(..., description="high / medium / low - whether networking matters or direct apply is fine")
    ai_verdict: str = Field(..., description="Strategic networking plan with prioritized actions")


# ============================================================================
# STEP 6: Action Plan
# ============================================================================

class ResumeEdit(BaseModel):
    action: str = Field(..., description="add / update / remove / reword")
    section: str
    detail: str = Field(..., description="Specific bullet-point level change tied to JD keywords")

class CoverLetterPlan(BaseModel):
    opening_hook: str = Field(..., description="First sentence that grabs attention for this specific role")
    key_points: List[str] = Field(..., description="3 key points tied directly to the JD")
    closing_line: str

class InterviewTopic(BaseModel):
    topic: str
    likely_question: str = Field(..., description="Realistic interview question they're likely to ask")
    what_theyre_testing: str = Field(..., description="What they're actually evaluating with this question")

class FollowUpStep(BaseModel):
    day: str = Field(..., description="e.g. 'Day 3', 'Day 7', 'Day 14'")
    action: str
    who: str
    message_template: str

class ActionPlan(BaseModel):
    """Step 6 output: Concrete action plan to maximize application chances."""
    resume_edits: List[ResumeEdit] = Field(..., description="Specific resume changes based on JD keywords")
    portfolio_updates: List[str] = Field(default_factory=list)
    quick_gap_closers: List[str] = Field(default_factory=list, description="Quick things to close critical gaps")
    cover_letter_plan: CoverLetterPlan
    interview_prep: List[InterviewTopic] = Field(..., description="Top 5 technical topics with questions")
    follow_up_strategy: List[FollowUpStep]
    prep_days_needed: int = Field(..., description="Realistic days of prep needed")
    ai_verdict: str = Field(..., description="Executive summary of the action plan with prioritized timeline")
