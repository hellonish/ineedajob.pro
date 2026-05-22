"""
LinkedIn-style resume field catalog.

This file is intentionally simple and readable. It answers:

1. What sections can exist in a modern resume/profile?
2. What fields/items belong inside each section?
3. Which sections matter most for the role groups we discussed?

The structure takes inspiration from LinkedIn profile sections:
- Intro / headline
- About
- Featured
- Experience
- Education
- Licenses & certifications
- Skills
- Projects
- Publications
- Honors & awards
- Volunteer experience
- Languages
- Recommendations

It also adds resume/application-only fields that LinkedIn does not handle well:
- Work authorization
- Availability
- Target role preferences
- Hard requirements
- Application documents
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class RoleGroup(str, Enum):
    """The practical job-search groups from the research."""

    SOFTWARE_IT_DATA = "software_it_data"
    BUSINESS_FINANCE_OPERATIONS = "business_finance_operations"
    CUSTOMER_SERVICE_ADMIN = "customer_service_admin"
    GOVERNMENT_PUBLIC_ADMIN = "government_public_admin"
    EDUCATION_NONPROFIT = "education_nonprofit"
    HEALTHCARE_NURSING = "healthcare_nursing"
    RETAIL_HOSPITALITY_FRONTLINE = "retail_hospitality_frontline"
    SALES = "sales"
    LOGISTICS_WAREHOUSE_TRUCKING = "logistics_warehouse_trucking"
    CONSTRUCTION_TRADES_MANUFACTURING = "construction_trades_manufacturing"


class HiringPattern(str, Enum):
    """How hiring usually works for a role."""

    ATS_HEAVY = "ats_heavy"
    PORTFOLIO_PROOF_HEAVY = "portfolio_proof_heavy"
    CREDENTIAL_GATED = "credential_gated"
    HIGH_VOLUME_FRONTLINE = "high_volume_frontline"
    REFERRAL_RELATIONSHIP_HEAVY = "referral_relationship_heavy"


@dataclass(frozen=True)
class FieldItem:
    """One item inside a resume/profile section."""

    name: str
    meaning: str
    examples: List[str] = field(default_factory=list)
    tailoring_note: str = ""


@dataclass(frozen=True)
class ResumeSection:
    """A LinkedIn-inspired resume/profile section."""

    section_id: str
    display_name: str
    linkedin_equivalent: str
    purpose: str
    items: List[FieldItem]
    best_for: List[RoleGroup] = field(default_factory=list)
    hiring_patterns: List[HiringPattern] = field(default_factory=list)


@dataclass(frozen=True)
class JobDescriptionPattern:
    """How a role's job descriptions usually look inside the current umbrella."""

    role_title: str
    role_group: RoleGroup
    jd_shape: str
    common_responsibilities: List[str]
    common_requirements: List[str]
    common_keywords: List[str]
    resume_fields_to_match: List[str]
    proof_to_show: List[str]


# ============================================================================
# CORE LINKEDIN-LIKE PROFILE SECTIONS
# These are the sections almost every professional profile/resume system needs.
# ============================================================================

CORE_PROFILE_SECTIONS: List[ResumeSection] = [
    ResumeSection(
        section_id="intro",
        display_name="Intro / Header",
        linkedin_equivalent="Intro section",
        purpose="Tell the reader who the candidate is, what role they fit, and how to contact them.",
        items=[
            FieldItem(
                name="Full name",
                meaning="The candidate's professional display name.",
                examples=["Nishant Sharma"],
            ),
            FieldItem(
                name="Target headline",
                meaning="The role identity the resume is positioning for.",
                examples=["Data Analyst", "Backend Software Engineer", "FP&A Analyst"],
                tailoring_note="Mirror the target job title when it is truthful.",
            ),
            FieldItem(
                name="Location",
                meaning="City, state, country, or remote-work location signal.",
                examples=["New York, NY", "Remote - United States"],
            ),
            FieldItem(
                name="Email",
                meaning="Primary professional email address.",
            ),
            FieldItem(
                name="Phone",
                meaning="Recruiter-safe phone number.",
            ),
            FieldItem(
                name="LinkedIn URL",
                meaning="Public LinkedIn profile link.",
            ),
            FieldItem(
                name="Portfolio / website URL",
                meaning="Personal site, GitHub, dashboard, writing portfolio, or case-study hub.",
                tailoring_note="Most useful for software, data, design, analytics, and strategy roles.",
            ),
        ],
        hiring_patterns=[HiringPattern.ATS_HEAVY, HiringPattern.PORTFOLIO_PROOF_HEAVY],
    ),
    ResumeSection(
        section_id="about",
        display_name="About / Professional Summary",
        linkedin_equivalent="About",
        purpose="Summarize the candidate's fit in a few lines before the reader reaches experience.",
        items=[
            FieldItem(
                name="Role identity",
                meaning="The professional category the candidate belongs to.",
                examples=["Data analyst focused on revenue operations"],
            ),
            FieldItem(
                name="Years or depth of experience",
                meaning="A quick seniority signal.",
                examples=["5+ years in SaaS operations", "3 years in backend systems"],
            ),
            FieldItem(
                name="Domain context",
                meaning="Industry or function where the candidate has useful experience.",
                examples=["fintech", "healthcare", "B2B SaaS", "supply chain"],
            ),
            FieldItem(
                name="Top skills/tools",
                meaning="The 3-6 most relevant skills for the target role.",
                examples=["SQL", "Python", "Tableau", "forecasting", "Salesforce"],
                tailoring_note="Use exact job-description language, but only for skills the candidate can defend.",
            ),
            FieldItem(
                name="Signature outcome",
                meaning="The strongest proof point or measurable result.",
                examples=["Reduced reporting time by 60%", "Managed $12M operating budget"],
            ),
        ],
        hiring_patterns=[HiringPattern.ATS_HEAVY],
    ),
    ResumeSection(
        section_id="featured",
        display_name="Featured Work",
        linkedin_equivalent="Featured",
        purpose="Pin proof artifacts that make the candidate's claims inspectable.",
        items=[
            FieldItem(
                name="GitHub repository",
                meaning="Code sample or open-source work.",
                examples=["API service", "data pipeline", "frontend app"],
            ),
            FieldItem(
                name="Live demo",
                meaning="A working product, app, dashboard, or prototype.",
            ),
            FieldItem(
                name="Case study",
                meaning="Problem, action, result, and business context.",
                examples=["Forecasting model case study", "Ops automation case study"],
            ),
            FieldItem(
                name="Dashboard / analysis sample",
                meaning="BI, analytics, reporting, or visualization proof.",
            ),
            FieldItem(
                name="Writing sample / publication",
                meaning="Article, policy memo, research paper, strategy brief, or technical explanation.",
            ),
            FieldItem(
                name="Certificate or credential file",
                meaning="A shareable credential when the role is credential-gated.",
            ),
        ],
        best_for=[
            RoleGroup.SOFTWARE_IT_DATA,
            RoleGroup.BUSINESS_FINANCE_OPERATIONS,
            RoleGroup.EDUCATION_NONPROFIT,
        ],
        hiring_patterns=[HiringPattern.PORTFOLIO_PROOF_HEAVY],
    ),
    ResumeSection(
        section_id="experience",
        display_name="Experience",
        linkedin_equivalent="Experience",
        purpose="Show where the candidate worked, what they owned, and what changed because of their work.",
        items=[
            FieldItem(name="Job title", meaning="Official or recruiter-readable title."),
            FieldItem(name="Company", meaning="Employer or client organization."),
            FieldItem(name="Location", meaning="Role location or remote marker."),
            FieldItem(name="Start date", meaning="When the role began."),
            FieldItem(name="End date", meaning="When the role ended, or Present."),
            FieldItem(
                name="Scope",
                meaning="Scale of work: team, budget, users, systems, revenue, territory, volume.",
                examples=["Supported 200 users", "Owned $8M budget", "Handled 60 tickets/day"],
            ),
            FieldItem(
                name="Responsibilities",
                meaning="The core work performed.",
                tailoring_note="Match responsibilities from the job description when they are true.",
            ),
            FieldItem(
                name="Achievements",
                meaning="Measurable outcomes and improvements.",
                examples=["Cut processing time 40%", "Improved forecast accuracy 15%"],
            ),
            FieldItem(
                name="Tools used",
                meaning="Systems, software, equipment, or methods used in the role.",
                examples=["SQL", "Excel", "Salesforce", "NetSuite", "AWS", "Zendesk"],
            ),
        ],
        hiring_patterns=[
            HiringPattern.ATS_HEAVY,
            HiringPattern.CREDENTIAL_GATED,
            HiringPattern.REFERRAL_RELATIONSHIP_HEAVY,
        ],
    ),
    ResumeSection(
        section_id="education",
        display_name="Education",
        linkedin_equivalent="Education",
        purpose="Show degrees, institutions, academic credentials, and relevant training.",
        items=[
            FieldItem(name="School / institution", meaning="College, university, bootcamp, or training provider."),
            FieldItem(name="Degree / program", meaning="Degree, diploma, certificate program, or training path."),
            FieldItem(name="Field of study", meaning="Major, concentration, or specialization."),
            FieldItem(name="Graduation date", meaning="Graduation year or expected completion date."),
            FieldItem(name="Honors", meaning="Academic distinction if relevant."),
            FieldItem(
                name="Relevant coursework",
                meaning="Target-role coursework, mainly for early-career or career-switching candidates.",
                examples=["Data Structures", "Financial Modeling", "Operations Research"],
            ),
        ],
        hiring_patterns=[HiringPattern.ATS_HEAVY, HiringPattern.CREDENTIAL_GATED],
    ),
    ResumeSection(
        section_id="skills",
        display_name="Skills",
        linkedin_equivalent="Skills",
        purpose="Expose searchable skills and make the candidate easy to match to the job.",
        items=[
            FieldItem(
                name="Technical skills",
                meaning="Programming, analytics, systems, tools, machinery, or job-specific methods.",
                examples=["Python", "SQL", "Power BI", "CNC", "Salesforce"],
            ),
            FieldItem(
                name="Functional skills",
                meaning="Role activities and business capabilities.",
                examples=["forecasting", "account management", "customer support", "process improvement"],
            ),
            FieldItem(
                name="Domain skills",
                meaning="Industry-specific or regulated knowledge.",
                examples=["HIPAA", "SOX", "DOT", "grant reporting", "revenue operations"],
            ),
            FieldItem(
                name="Soft skills",
                meaning="Human skills that matter when backed by evidence.",
                examples=["stakeholder management", "training", "conflict resolution"],
                tailoring_note="Avoid long generic soft-skill lists; prove them in experience bullets.",
            ),
        ],
        hiring_patterns=[HiringPattern.ATS_HEAVY, HiringPattern.HIGH_VOLUME_FRONTLINE],
    ),
]


# ============================================================================
# CREDENTIAL, PROOF, AND ACCOMPLISHMENT SECTIONS
# These are optional globally, but essential in specific domains.
# ============================================================================

PROOF_AND_CREDENTIAL_SECTIONS: List[ResumeSection] = [
    ResumeSection(
        section_id="licenses_certifications",
        display_name="Licenses & Certifications",
        linkedin_equivalent="Licenses & certifications",
        purpose="Show hard credentials, renewals, issuing bodies, and eligibility.",
        items=[
            FieldItem(name="Credential name", meaning="Name of license or certification."),
            FieldItem(name="Issuing organization", meaning="Who granted the credential."),
            FieldItem(name="License number", meaning="Credential ID when safe and appropriate."),
            FieldItem(name="State / jurisdiction", meaning="Where the license is valid."),
            FieldItem(name="Issue date", meaning="When it was granted."),
            FieldItem(name="Expiration date", meaning="When it must be renewed."),
            FieldItem(
                name="Credential status",
                meaning="Active, pending, expired, eligible, or in progress.",
                tailoring_note="For credential-gated jobs, place active required credentials near the top.",
            ),
        ],
        best_for=[
            RoleGroup.HEALTHCARE_NURSING,
            RoleGroup.GOVERNMENT_PUBLIC_ADMIN,
            RoleGroup.EDUCATION_NONPROFIT,
            RoleGroup.LOGISTICS_WAREHOUSE_TRUCKING,
            RoleGroup.CONSTRUCTION_TRADES_MANUFACTURING,
        ],
        hiring_patterns=[HiringPattern.CREDENTIAL_GATED],
    ),
    ResumeSection(
        section_id="projects",
        display_name="Projects",
        linkedin_equivalent="Projects",
        purpose="Show relevant work that may not fit cleanly into formal employment history.",
        items=[
            FieldItem(name="Project name", meaning="Short recognizable title."),
            FieldItem(name="Role", meaning="What the candidate personally owned."),
            FieldItem(name="Problem", meaning="What the project was trying to solve."),
            FieldItem(name="Tools / methods", meaning="Technology, framework, analysis, or process used."),
            FieldItem(name="Outcome", meaning="Result, metric, demo, adoption, or lesson."),
            FieldItem(name="Project URL", meaning="GitHub, demo, dashboard, write-up, or portfolio link."),
        ],
        best_for=[RoleGroup.SOFTWARE_IT_DATA, RoleGroup.BUSINESS_FINANCE_OPERATIONS],
        hiring_patterns=[HiringPattern.PORTFOLIO_PROOF_HEAVY],
    ),
    ResumeSection(
        section_id="publications",
        display_name="Publications",
        linkedin_equivalent="Publications",
        purpose="Show published work, research, writing, thought leadership, or policy work.",
        items=[
            FieldItem(name="Title", meaning="Publication title."),
            FieldItem(name="Publisher", meaning="Publication venue, journal, website, or organization."),
            FieldItem(name="Date", meaning="Publication date."),
            FieldItem(name="Coauthors", meaning="Other authors when relevant."),
            FieldItem(name="URL", meaning="Link to the publication."),
            FieldItem(name="Relevance", meaning="Why it matters for the target role."),
        ],
        best_for=[RoleGroup.EDUCATION_NONPROFIT, RoleGroup.SOFTWARE_IT_DATA],
        hiring_patterns=[HiringPattern.PORTFOLIO_PROOF_HEAVY],
    ),
    ResumeSection(
        section_id="patents",
        display_name="Patents",
        linkedin_equivalent="Patents",
        purpose="Show invention, R&D, technical originality, or product contribution.",
        items=[
            FieldItem(name="Patent title", meaning="Name of patent."),
            FieldItem(name="Patent number", meaning="Patent or application number."),
            FieldItem(name="Status", meaning="Filed, pending, granted, provisional."),
            FieldItem(name="Date", meaning="Filing or grant date."),
            FieldItem(name="Co-inventors", meaning="Other named inventors."),
        ],
        best_for=[RoleGroup.SOFTWARE_IT_DATA, RoleGroup.CONSTRUCTION_TRADES_MANUFACTURING],
        hiring_patterns=[HiringPattern.PORTFOLIO_PROOF_HEAVY],
    ),
    ResumeSection(
        section_id="honors_awards",
        display_name="Honors & Awards",
        linkedin_equivalent="Honors & awards",
        purpose="Show external recognition, performance distinction, or academic/professional awards.",
        items=[
            FieldItem(name="Award name", meaning="Name of recognition."),
            FieldItem(name="Issuer", meaning="Organization that gave the award."),
            FieldItem(name="Date", meaning="When it was awarded."),
            FieldItem(name="Reason", meaning="What achievement the award recognized."),
        ],
        hiring_patterns=[HiringPattern.REFERRAL_RELATIONSHIP_HEAVY],
    ),
]


# ============================================================================
# COMMUNITY, LANGUAGE, AND SOCIAL-PROOF SECTIONS
# These help when mission, trust, communication, or relationships matter.
# ============================================================================

RELATIONSHIP_AND_CONTEXT_SECTIONS: List[ResumeSection] = [
    ResumeSection(
        section_id="volunteer_experience",
        display_name="Volunteer Experience",
        linkedin_equivalent="Volunteer experience",
        purpose="Show mission fit, community work, leadership, or transferable experience.",
        items=[
            FieldItem(name="Organization", meaning="Volunteer organization."),
            FieldItem(name="Role", meaning="Volunteer title or function."),
            FieldItem(name="Cause / mission", meaning="Community, population, or issue served."),
            FieldItem(name="Dates", meaning="When the work happened."),
            FieldItem(name="Impact", meaning="Outcome, service volume, program result, or responsibility."),
        ],
        best_for=[RoleGroup.EDUCATION_NONPROFIT, RoleGroup.GOVERNMENT_PUBLIC_ADMIN],
    ),
    ResumeSection(
        section_id="organizations",
        display_name="Organizations",
        linkedin_equivalent="Organizations",
        purpose="Show professional associations, unions, student groups, or industry communities.",
        items=[
            FieldItem(name="Organization name", meaning="Association, union, community, or group."),
            FieldItem(name="Membership type", meaning="Member, board member, officer, apprentice, union member."),
            FieldItem(name="Role", meaning="Leadership or participation role."),
            FieldItem(name="Dates", meaning="Membership period."),
        ],
        best_for=[
            RoleGroup.CONSTRUCTION_TRADES_MANUFACTURING,
            RoleGroup.GOVERNMENT_PUBLIC_ADMIN,
            RoleGroup.BUSINESS_FINANCE_OPERATIONS,
        ],
        hiring_patterns=[HiringPattern.REFERRAL_RELATIONSHIP_HEAVY],
    ),
    ResumeSection(
        section_id="languages",
        display_name="Languages",
        linkedin_equivalent="Languages",
        purpose="Show language ability when it helps serve customers, patients, students, teams, or communities.",
        items=[
            FieldItem(name="Language", meaning="Language spoken, read, or written."),
            FieldItem(name="Proficiency", meaning="Beginner, conversational, professional, fluent, native."),
            FieldItem(name="Use context", meaning="How the language has been used professionally."),
        ],
        best_for=[
            RoleGroup.CUSTOMER_SERVICE_ADMIN,
            RoleGroup.HEALTHCARE_NURSING,
            RoleGroup.EDUCATION_NONPROFIT,
            RoleGroup.RETAIL_HOSPITALITY_FRONTLINE,
        ],
    ),
    ResumeSection(
        section_id="recommendations",
        display_name="Recommendations",
        linkedin_equivalent="Recommendations",
        purpose="Capture third-party proof from managers, peers, clients, teachers, or collaborators.",
        items=[
            FieldItem(name="Recommender name", meaning="Person giving the recommendation."),
            FieldItem(name="Relationship", meaning="Manager, client, peer, professor, mentor, coworker."),
            FieldItem(name="Quote", meaning="Short proof statement."),
            FieldItem(name="Permission", meaning="Whether the quote can be used publicly."),
        ],
        hiring_patterns=[HiringPattern.REFERRAL_RELATIONSHIP_HEAVY],
    ),
]


# ============================================================================
# APPLICATION-ONLY SECTIONS
# These usually belong in a master profile or application tracker.
# They are not always printed on the resume.
# ============================================================================

APPLICATION_ONLY_SECTIONS: List[ResumeSection] = [
    ResumeSection(
        section_id="job_preferences",
        display_name="Job Preferences",
        linkedin_equivalent="Open to work / Job preferences",
        purpose="Track what the candidate is actually looking for.",
        items=[
            FieldItem(name="Target titles", meaning="Desired job titles."),
            FieldItem(name="Target industries", meaning="Industries the candidate wants."),
            FieldItem(name="Work mode", meaning="Remote, hybrid, onsite."),
            FieldItem(name="Employment type", meaning="Full-time, part-time, contract, internship, temporary."),
            FieldItem(name="Seniority", meaning="Entry, junior, mid, senior, manager, director."),
        ],
    ),
    ResumeSection(
        section_id="availability",
        display_name="Availability",
        linkedin_equivalent="Job preferences",
        purpose="Resolve practical hiring constraints.",
        items=[
            FieldItem(name="Start date", meaning="Earliest available start date."),
            FieldItem(name="Schedule", meaning="Preferred or possible schedule."),
            FieldItem(name="Shift", meaning="Day, evening, night, rotating, weekend."),
            FieldItem(name="Hours", meaning="Full-time, part-time, specific weekly hours."),
            FieldItem(name="Travel", meaning="Travel availability or limits."),
        ],
        best_for=[
            RoleGroup.RETAIL_HOSPITALITY_FRONTLINE,
            RoleGroup.HEALTHCARE_NURSING,
            RoleGroup.LOGISTICS_WAREHOUSE_TRUCKING,
        ],
        hiring_patterns=[HiringPattern.HIGH_VOLUME_FRONTLINE],
    ),
    ResumeSection(
        section_id="work_authorization",
        display_name="Work Authorization",
        linkedin_equivalent="Not a strong LinkedIn resume section",
        purpose="Track legal work eligibility and sponsorship constraints.",
        items=[
            FieldItem(name="Authorization status", meaning="Eligible to work, visa status, or permit status."),
            FieldItem(name="Sponsorship need", meaning="Whether sponsorship is needed now or later."),
            FieldItem(name="Expiration date", meaning="Permit or visa expiration when relevant."),
            FieldItem(name="Citizenship requirement", meaning="Only when required for government/security roles."),
        ],
        hiring_patterns=[HiringPattern.CREDENTIAL_GATED],
    ),
    ResumeSection(
        section_id="hard_requirements",
        display_name="Hard Requirements",
        linkedin_equivalent="Licenses & certifications / Skills",
        purpose="Track must-have requirements from job postings.",
        items=[
            FieldItem(name="Required credential", meaning="License, certification, degree, clearance, or endorsement."),
            FieldItem(name="Required tool", meaning="Tool or system explicitly required."),
            FieldItem(name="Required experience", meaning="Years, setting, specialty, or scope."),
            FieldItem(name="Required location", meaning="Onsite, region, travel, or relocation requirement."),
            FieldItem(name="Required document", meaning="Transcript, portfolio, writing sample, license copy, clearance proof."),
        ],
        hiring_patterns=[HiringPattern.ATS_HEAVY, HiringPattern.CREDENTIAL_GATED],
    ),
    ResumeSection(
        section_id="application_documents",
        display_name="Application Documents",
        linkedin_equivalent="Featured / Licenses & certifications",
        purpose="Track required files for formal applications.",
        items=[
            FieldItem(name="Resume version", meaning="Which tailored resume was used."),
            FieldItem(name="Cover letter", meaning="Role-specific letter or note."),
            FieldItem(name="Portfolio", meaning="Proof artifact bundle or link."),
            FieldItem(name="Transcript", meaning="Academic transcript when required."),
            FieldItem(name="License copy", meaning="Credential attachment when required."),
            FieldItem(name="Writing sample", meaning="Sample requested by employer."),
            FieldItem(name="Government forms", meaning="Required public-sector forms or preference documents."),
        ],
        best_for=[
            RoleGroup.GOVERNMENT_PUBLIC_ADMIN,
            RoleGroup.EDUCATION_NONPROFIT,
            RoleGroup.HEALTHCARE_NURSING,
        ],
        hiring_patterns=[HiringPattern.CREDENTIAL_GATED],
    ),
]


# ============================================================================
# ONE COMPLETE SECTION LIST
# Use this if the product needs the full catalog.
# ============================================================================

ALL_RESUME_SECTIONS: List[ResumeSection] = (
    CORE_PROFILE_SECTIONS
    + PROOF_AND_CREDENTIAL_SECTIONS
    + RELATIONSHIP_AND_CONTEXT_SECTIONS
    + APPLICATION_ONLY_SECTIONS
)


# ============================================================================
# ROLE-GROUP SECTION MAP
# This says which sections matter most for each profession group.
# ============================================================================

ROLE_GROUP_SECTION_MAP: Dict[RoleGroup, List[str]] = {
    RoleGroup.SOFTWARE_IT_DATA: [
        "intro",
        "about",
        "skills",
        "experience",
        "projects",
        "featured",
        "education",
        "licenses_certifications",
    ],
    RoleGroup.BUSINESS_FINANCE_OPERATIONS: [
        "intro",
        "about",
        "skills",
        "experience",
        "featured",
        "projects",
        "licenses_certifications",
        "education",
    ],
    RoleGroup.CUSTOMER_SERVICE_ADMIN: [
        "intro",
        "about",
        "skills",
        "experience",
        "availability",
        "languages",
        "education",
    ],
    RoleGroup.GOVERNMENT_PUBLIC_ADMIN: [
        "intro",
        "about",
        "experience",
        "skills",
        "hard_requirements",
        "work_authorization",
        "licenses_certifications",
        "application_documents",
        "education",
    ],
    RoleGroup.EDUCATION_NONPROFIT: [
        "intro",
        "about",
        "experience",
        "education",
        "licenses_certifications",
        "volunteer_experience",
        "publications",
        "application_documents",
    ],
    RoleGroup.HEALTHCARE_NURSING: [
        "intro",
        "licenses_certifications",
        "experience",
        "skills",
        "availability",
        "hard_requirements",
        "education",
        "application_documents",
    ],
    RoleGroup.RETAIL_HOSPITALITY_FRONTLINE: [
        "intro",
        "availability",
        "experience",
        "skills",
        "languages",
        "education",
    ],
    RoleGroup.SALES: [
        "intro",
        "about",
        "experience",
        "skills",
        "featured",
        "recommendations",
        "education",
    ],
    RoleGroup.LOGISTICS_WAREHOUSE_TRUCKING: [
        "intro",
        "licenses_certifications",
        "availability",
        "experience",
        "skills",
        "hard_requirements",
        "education",
    ],
    RoleGroup.CONSTRUCTION_TRADES_MANUFACTURING: [
        "intro",
        "licenses_certifications",
        "experience",
        "skills",
        "projects",
        "organizations",
        "hard_requirements",
        "education",
    ],
}


# ============================================================================
# HIRING-PATTERN MAP
# This is the simpler version of the strategy logic:
# which sections matter based on how hiring works.
# ============================================================================

HIRING_PATTERN_SECTION_MAP: Dict[HiringPattern, List[str]] = {
    HiringPattern.ATS_HEAVY: [
        "intro",
        "about",
        "skills",
        "experience",
        "education",
        "hard_requirements",
    ],
    HiringPattern.PORTFOLIO_PROOF_HEAVY: [
        "featured",
        "projects",
        "publications",
        "patents",
        "recommendations",
    ],
    HiringPattern.CREDENTIAL_GATED: [
        "licenses_certifications",
        "education",
        "work_authorization",
        "hard_requirements",
        "application_documents",
    ],
    HiringPattern.HIGH_VOLUME_FRONTLINE: [
        "intro",
        "availability",
        "experience",
        "skills",
        "languages",
    ],
    HiringPattern.REFERRAL_RELATIONSHIP_HEAVY: [
        "experience",
        "featured",
        "organizations",
        "recommendations",
        "honors_awards",
    ],
}


# ============================================================================
# EXACT FIELD MAP FOR THE CURRENT UMBRELLA
# Umbrella:
# - ATS-heavy professional roles
# - Portfolio/proof-heavy roles
# - Software / IT / Data
# - Business / Finance / Operations
#
# Use this when generating a focused resume for roles like:
# software engineer, data analyst, data engineer, BI analyst, product analyst,
# FP&A analyst, business analyst, operations analyst, strategy associate,
# revops analyst, risk analyst, procurement analyst, or systems analyst.
# ============================================================================

ATS_PORTFOLIO_PROFESSIONAL_FIELD_MAP: Dict[str, object] = {
    "umbrella_name": "ATS-heavy and portfolio/proof-heavy professional roles",
    "role_groups": [
        RoleGroup.SOFTWARE_IT_DATA.value,
        RoleGroup.BUSINESS_FINANCE_OPERATIONS.value,
    ],
    "hiring_patterns": [
        HiringPattern.ATS_HEAVY.value,
        HiringPattern.PORTFOLIO_PROOF_HEAVY.value,
    ],
    # ------------------------------------------------------------------------
    # Fields to include on the resume/profile for nearly every role in this
    # umbrella. These fields support ATS matching and human review.
    # ------------------------------------------------------------------------
    "included_fields": {
        "intro": [
            "Full name",
            "Target headline",
            "Location",
            "Email",
            "Phone",
            "LinkedIn URL",
            "Portfolio / website URL",
        ],
        "about": [
            "Role identity",
            "Years or depth of experience",
            "Domain context",
            "Top skills/tools",
            "Signature outcome",
        ],
        "skills": [
            "Technical skills",
            "Functional skills",
            "Domain skills",
        ],
        "experience": [
            "Job title",
            "Company",
            "Location",
            "Start date",
            "End date",
            "Scope",
            "Responsibilities",
            "Achievements",
            "Tools used",
        ],
        "projects": [
            "Project name",
            "Role",
            "Problem",
            "Tools / methods",
            "Outcome",
            "Project URL",
        ],
        "featured": [
            "Case study",
            "Dashboard / analysis sample",
        ],
        "education": [
            "School / institution",
            "Degree / program",
            "Field of study",
            "Graduation date",
        ],
        "hard_requirements": [
            "Required tool",
            "Required experience",
        ],
        "application_documents": [
            "Resume version",
            "Cover letter",
            "Portfolio",
            "Writing sample",
        ],
    },
    # ------------------------------------------------------------------------
    # Fields to include only when they directly support the target role.
    # These are useful but should not be forced into every resume.
    # ------------------------------------------------------------------------
    "conditional_fields": {
        "featured": [
            "GitHub repository",
            "Live demo",
            "Writing sample / publication",
            "Certificate or credential file",
        ],
        "education": [
            "Honors",
            "Relevant coursework",
        ],
        "skills": [
            "Soft skills",
        ],
        "licenses_certifications": [
            "Credential name",
            "Issuing organization",
            "Issue date",
            "Expiration date",
            "Credential status",
        ],
        "publications": [
            "Title",
            "Publisher",
            "Date",
            "URL",
            "Relevance",
        ],
        "patents": [
            "Patent title",
            "Patent number",
            "Status",
            "Date",
        ],
        "honors_awards": [
            "Award name",
            "Issuer",
            "Date",
            "Reason",
        ],
        "organizations": [
            "Organization name",
            "Membership type",
            "Role",
            "Dates",
        ],
        "recommendations": [
            "Recommender name",
            "Relationship",
            "Quote",
            "Permission",
        ],
        "job_preferences": [
            "Target titles",
            "Target industries",
            "Work mode",
            "Employment type",
            "Seniority",
        ],
        "work_authorization": [
            "Authorization status",
            "Sponsorship need",
        ],
    },
    # ------------------------------------------------------------------------
    # Fields not used for this umbrella by default.
    # These belong to frontline, credential-gated, government, healthcare,
    # logistics, education/nonprofit, or local relationship-heavy searches.
    # ------------------------------------------------------------------------
    "not_used_fields": {
        "licenses_certifications": [
            "License number",
            "State / jurisdiction",
        ],
        "publications": [
            "Coauthors",
        ],
        "patents": [
            "Co-inventors",
        ],
        "volunteer_experience": [
            "Organization",
            "Role",
            "Cause / mission",
            "Dates",
            "Impact",
        ],
        "languages": [
            "Language",
            "Proficiency",
            "Use context",
        ],
        "availability": [
            "Start date",
            "Schedule",
            "Shift",
            "Hours",
            "Travel",
        ],
        "work_authorization": [
            "Expiration date",
            "Citizenship requirement",
        ],
        "hard_requirements": [
            "Required credential",
            "Required location",
            "Required document",
        ],
        "application_documents": [
            "Transcript",
            "License copy",
            "Government forms",
        ],
    },
    # ------------------------------------------------------------------------
    # Role-specific deltas inside the umbrella.
    # These make the same umbrella work for both technical and business roles.
    # ------------------------------------------------------------------------
    "role_specific_emphasis": {
        RoleGroup.SOFTWARE_IT_DATA.value: {
            "most_important_fields": [
                "Target headline",
                "Top skills/tools",
                "Technical skills",
                "Tools used",
                "Achievements",
                "GitHub repository",
                "Live demo",
                "Project URL",
            ],
            "usually_skip": [
                "Certificate or credential file",
                "Organizations",
                "Recommendations",
            ],
        },
        RoleGroup.BUSINESS_FINANCE_OPERATIONS.value: {
            "most_important_fields": [
                "Target headline",
                "Domain context",
                "Signature outcome",
                "Functional skills",
                "Scope",
                "Achievements",
                "Tools used",
                "Case study",
                "Dashboard / analysis sample",
            ],
            "usually_skip": [
                "GitHub repository",
                "Live demo",
                "Patents",
            ],
        },
    },
}


# ============================================================================
# JD PATTERNS INSIDE THE CURRENT UMBRELLA
# These patterns summarize how job descriptions tend to look for diverse roles
# inside Software / IT / Data and Business / Finance / Operations.
# ============================================================================

JD_PATTERNS_FOR_ATS_PORTFOLIO_UMBRELLA: List[JobDescriptionPattern] = [
    # ------------------------------------------------------------------------
    # Software / IT / Data roles
    # ------------------------------------------------------------------------
    JobDescriptionPattern(
        role_title="Backend Software Engineer",
        role_group=RoleGroup.SOFTWARE_IT_DATA,
        jd_shape="Build and maintain server-side systems, APIs, services, data models, integrations, and production reliability.",
        common_responsibilities=[
            "Design, build, test, and maintain backend services or APIs.",
            "Create data models, database queries, and integrations.",
            "Improve performance, scalability, reliability, and security.",
            "Collaborate with product, frontend, QA, DevOps, and stakeholders.",
            "Debug production issues and improve engineering quality.",
        ],
        common_requirements=[
            "Experience with one or more backend languages.",
            "Database and API design experience.",
            "Version control, testing, and production debugging.",
            "Cloud, container, or distributed-system experience for many roles.",
        ],
        common_keywords=[
            "Python",
            "Java",
            "Node.js",
            "Go",
            "REST",
            "GraphQL",
            "SQL",
            "PostgreSQL",
            "AWS",
            "microservices",
            "scalability",
        ],
        resume_fields_to_match=[
            "Target headline",
            "Top skills/tools",
            "Technical skills",
            "Tools used",
            "Achievements",
            "Project URL",
        ],
        proof_to_show=[
            "API or service project",
            "system design explanation",
            "performance or reliability metric",
            "GitHub repository",
        ],
    ),
    JobDescriptionPattern(
        role_title="Frontend / Full-Stack Engineer",
        role_group=RoleGroup.SOFTWARE_IT_DATA,
        jd_shape="Build user-facing features, frontend architecture, browser performance, component systems, and full-stack product workflows.",
        common_responsibilities=[
            "Develop responsive, accessible, user-facing features.",
            "Integrate frontend applications with APIs and backend services.",
            "Improve performance, testing, maintainability, and user experience.",
            "Collaborate with product, design, backend, and QA teams.",
        ],
        common_requirements=[
            "Strong JavaScript or TypeScript experience.",
            "Experience with frontend frameworks and state management.",
            "Understanding of accessibility, testing, performance, and browser behavior.",
            "Backend familiarity for full-stack roles.",
        ],
        common_keywords=[
            "JavaScript",
            "TypeScript",
            "React",
            "Next.js",
            "HTML",
            "CSS",
            "accessibility",
            "frontend testing",
            "performance",
            "APIs",
        ],
        resume_fields_to_match=[
            "Target headline",
            "Technical skills",
            "Projects",
            "Live demo",
            "Tools used",
            "Achievements",
        ],
        proof_to_show=[
            "live demo",
            "component or app repository",
            "performance/accessibility improvement",
            "product UI shipped to users",
        ],
    ),
    JobDescriptionPattern(
        role_title="Data Analyst / BI Analyst",
        role_group=RoleGroup.SOFTWARE_IT_DATA,
        jd_shape="Turn business questions into SQL analysis, dashboards, KPI definitions, and decision-ready insights.",
        common_responsibilities=[
            "Build dashboards and recurring reports.",
            "Write SQL queries and analyze business data.",
            "Define KPIs and metric logic with stakeholders.",
            "Perform ad hoc analysis and explain insights.",
            "Monitor data quality and reporting consistency.",
        ],
        common_requirements=[
            "SQL and spreadsheet proficiency.",
            "Experience with BI tools.",
            "Ability to communicate insights to non-technical stakeholders.",
            "Understanding of business metrics and data quality.",
        ],
        common_keywords=[
            "SQL",
            "Tableau",
            "Power BI",
            "Looker",
            "Excel",
            "KPI",
            "dashboard",
            "ad hoc analysis",
            "data quality",
            "stakeholders",
        ],
        resume_fields_to_match=[
            "Target headline",
            "Domain context",
            "Top skills/tools",
            "Dashboard / analysis sample",
            "Achievements",
            "Tools used",
        ],
        proof_to_show=[
            "dashboard sample",
            "SQL analysis project",
            "metric definition example",
            "business decision influenced by analysis",
        ],
    ),
    JobDescriptionPattern(
        role_title="Data Engineer",
        role_group=RoleGroup.SOFTWARE_IT_DATA,
        jd_shape="Build data pipelines, warehouses, models, and infrastructure that make analytics and ML reliable.",
        common_responsibilities=[
            "Design and maintain ETL or ELT pipelines.",
            "Model, transform, and validate data for analytics users.",
            "Improve reliability, quality, observability, and performance of data systems.",
            "Collaborate with analysts, data scientists, engineers, and business teams.",
        ],
        common_requirements=[
            "Strong SQL and programming experience.",
            "Data warehouse, orchestration, and pipeline tooling.",
            "Cloud data platform experience.",
            "Understanding of data quality, governance, and scalability.",
        ],
        common_keywords=[
            "SQL",
            "Python",
            "ETL",
            "ELT",
            "Airflow",
            "dbt",
            "Snowflake",
            "BigQuery",
            "Spark",
            "AWS",
            "data quality",
        ],
        resume_fields_to_match=[
            "Technical skills",
            "Tools used",
            "Projects",
            "Scope",
            "Achievements",
            "Project URL",
        ],
        proof_to_show=[
            "pipeline project",
            "data model example",
            "reliability or runtime improvement",
            "cloud/data warehouse architecture",
        ],
    ),
    JobDescriptionPattern(
        role_title="Data Scientist / ML Analyst",
        role_group=RoleGroup.SOFTWARE_IT_DATA,
        jd_shape="Use statistics, modeling, experimentation, and machine learning to solve business or product problems.",
        common_responsibilities=[
            "Build predictive, statistical, or machine-learning models.",
            "Analyze experiments, cohorts, segments, and user/customer behavior.",
            "Translate model or analysis results into business recommendations.",
            "Partner with product, engineering, operations, or leadership teams.",
        ],
        common_requirements=[
            "Python or R, SQL, statistics, and experimentation knowledge.",
            "Experience with ML libraries or modeling techniques.",
            "Ability to explain assumptions, tradeoffs, and business impact.",
        ],
        common_keywords=[
            "Python",
            "R",
            "SQL",
            "machine learning",
            "statistics",
            "experimentation",
            "A/B testing",
            "scikit-learn",
            "forecasting",
            "classification",
        ],
        resume_fields_to_match=[
            "Technical skills",
            "Projects",
            "Case study",
            "Tools used",
            "Outcome",
            "Signature outcome",
        ],
        proof_to_show=[
            "modeling project",
            "experiment analysis",
            "forecasting case study",
            "business result from model or analysis",
        ],
    ),
    JobDescriptionPattern(
        role_title="DevOps / SRE / Cloud Engineer",
        role_group=RoleGroup.SOFTWARE_IT_DATA,
        jd_shape="Own deployment, infrastructure, automation, observability, incident response, and cloud reliability.",
        common_responsibilities=[
            "Build and maintain CI/CD pipelines.",
            "Automate infrastructure provisioning and configuration.",
            "Manage cloud services, containers, and deployment environments.",
            "Monitor systems, troubleshoot incidents, and improve reliability.",
            "Collaborate with engineering teams on secure, scalable delivery.",
        ],
        common_requirements=[
            "Linux, networking, scripting, cloud, CI/CD, and infrastructure-as-code experience.",
            "Containerization and orchestration experience.",
            "Monitoring, logging, incident response, and reliability knowledge.",
        ],
        common_keywords=[
            "AWS",
            "Azure",
            "GCP",
            "Docker",
            "Kubernetes",
            "Terraform",
            "Ansible",
            "CI/CD",
            "Jenkins",
            "GitHub Actions",
            "Prometheus",
            "Grafana",
        ],
        resume_fields_to_match=[
            "Technical skills",
            "Tools used",
            "Scope",
            "Responsibilities",
            "Achievements",
            "Project URL",
        ],
        proof_to_show=[
            "IaC repository",
            "deployment pipeline example",
            "uptime/reliability improvement",
            "incident reduction or automation metric",
        ],
    ),
    JobDescriptionPattern(
        role_title="Cybersecurity Analyst / Security Analyst",
        role_group=RoleGroup.SOFTWARE_IT_DATA,
        jd_shape="Monitor, assess, and reduce security risk through detection, controls, investigation, governance, or compliance.",
        common_responsibilities=[
            "Monitor security events and investigate incidents.",
            "Assess vulnerabilities, risks, controls, and compliance gaps.",
            "Maintain dashboards, reports, documentation, and response procedures.",
            "Partner with IT, engineering, risk, compliance, and leadership teams.",
        ],
        common_requirements=[
            "Security tools, risk frameworks, incident response, and analytical skills.",
            "Knowledge of networks, systems, cloud, identity, or compliance.",
            "Certifications may be preferred or required depending on level.",
        ],
        common_keywords=[
            "SIEM",
            "SOC",
            "incident response",
            "vulnerability management",
            "risk assessment",
            "NIST",
            "ISO 27001",
            "SOC 2",
            "IAM",
            "cloud security",
        ],
        resume_fields_to_match=[
            "Target headline",
            "Technical skills",
            "Domain skills",
            "Tools used",
            "Licenses & Certifications",
            "Achievements",
        ],
        proof_to_show=[
            "security project",
            "risk/control assessment example",
            "incident or vulnerability reduction metric",
            "certification if relevant",
        ],
    ),
    JobDescriptionPattern(
        role_title="Systems Analyst / Business Systems Analyst",
        role_group=RoleGroup.SOFTWARE_IT_DATA,
        jd_shape="Translate business needs into system requirements, workflows, specifications, testing, and implementation support.",
        common_responsibilities=[
            "Gather user and business requirements.",
            "Analyze systems, workflows, data, and integration needs.",
            "Document functional and technical specifications.",
            "Support UAT, implementation, training, and issue resolution.",
        ],
        common_requirements=[
            "Requirements gathering, documentation, testing, and stakeholder communication.",
            "Experience with enterprise systems, databases, or business applications.",
            "Ability to bridge business users and technical teams.",
        ],
        common_keywords=[
            "requirements",
            "functional specifications",
            "UAT",
            "systems analysis",
            "process documentation",
            "SQL",
            "ERP",
            "CRM",
            "stakeholders",
        ],
        resume_fields_to_match=[
            "Role identity",
            "Domain context",
            "Responsibilities",
            "Tools used",
            "Achievements",
            "Case study",
        ],
        proof_to_show=[
            "requirements document example",
            "process map",
            "system implementation result",
            "UAT or adoption metric",
        ],
    ),
    # ------------------------------------------------------------------------
    # Business / Finance / Operations roles
    # ------------------------------------------------------------------------
    JobDescriptionPattern(
        role_title="Business Analyst",
        role_group=RoleGroup.BUSINESS_FINANCE_OPERATIONS,
        jd_shape="Bridge business goals and technical/process solutions through requirements, analysis, documentation, and testing.",
        common_responsibilities=[
            "Gather, define, and document business requirements.",
            "Analyze processes, issues, and opportunities for improvement.",
            "Support reporting, alerting, QA, UAT, and implementation.",
            "Communicate insights and recommendations to product, IT, or business stakeholders.",
        ],
        common_requirements=[
            "Business/systems analysis or QA experience.",
            "Requirements elicitation and documentation.",
            "SQL, data analysis, visualization, or process documentation.",
            "Strong written and verbal communication.",
        ],
        common_keywords=[
            "requirements gathering",
            "business analysis",
            "process improvement",
            "UAT",
            "QA",
            "SQL",
            "reporting",
            "stakeholder management",
            "documentation",
        ],
        resume_fields_to_match=[
            "Target headline",
            "Domain context",
            "Functional skills",
            "Responsibilities",
            "Achievements",
            "Tools used",
        ],
        proof_to_show=[
            "requirements or process case study",
            "reporting/dashboard example",
            "process improvement metric",
            "stakeholder-facing deliverable",
        ],
    ),
    JobDescriptionPattern(
        role_title="FP&A / Financial Analyst",
        role_group=RoleGroup.BUSINESS_FINANCE_OPERATIONS,
        jd_shape="Own budgeting, forecasting, variance analysis, reporting packages, financial models, and decision support.",
        common_responsibilities=[
            "Build and maintain budgets, forecasts, and financial models.",
            "Analyze actuals vs budget/forecast and explain variances.",
            "Prepare monthly, quarterly, board, or executive reporting.",
            "Partner with business leaders on planning, cost, revenue, and performance decisions.",
        ],
        common_requirements=[
            "Excel and financial modeling proficiency.",
            "Understanding of financial statements, budgeting, forecasting, and variance analysis.",
            "ERP, planning, BI, or accounting-system experience often preferred.",
            "Strong communication and business partnering.",
        ],
        common_keywords=[
            "budgeting",
            "forecasting",
            "variance analysis",
            "financial modeling",
            "P&L",
            "OpEx",
            "CapEx",
            "Excel",
            "Anaplan",
            "Adaptive Planning",
            "ERP",
        ],
        resume_fields_to_match=[
            "Target headline",
            "Signature outcome",
            "Scope",
            "Achievements",
            "Tools used",
            "Case study",
        ],
        proof_to_show=[
            "financial model description",
            "forecasting or variance analysis result",
            "budget size owned",
            "executive reporting example",
        ],
    ),
    JobDescriptionPattern(
        role_title="Operations Analyst",
        role_group=RoleGroup.BUSINESS_FINANCE_OPERATIONS,
        jd_shape="Analyze policies, procedures, workflows, and performance data to improve operating metrics.",
        common_responsibilities=[
            "Review operational data, policies, processes, and procedures.",
            "Build reports and dashboards on performance metrics.",
            "Identify inefficiencies and recommend process improvements.",
            "Partner with cross-functional teams to execute operational changes.",
        ],
        common_requirements=[
            "Data analysis, reporting, and process improvement experience.",
            "Excel, SQL, BI, or workflow tool proficiency.",
            "Strong problem-solving and communication skills.",
        ],
        common_keywords=[
            "operations",
            "process improvement",
            "KPI",
            "reporting",
            "workflow",
            "Excel",
            "SQL",
            "Power BI",
            "Tableau",
            "cross-functional",
        ],
        resume_fields_to_match=[
            "Domain context",
            "Functional skills",
            "Scope",
            "Achievements",
            "Tools used",
            "Dashboard / analysis sample",
        ],
        proof_to_show=[
            "process improvement case",
            "operations dashboard",
            "cycle-time/cost/productivity metric",
            "cross-functional project result",
        ],
    ),
    JobDescriptionPattern(
        role_title="Revenue Operations / Sales Operations Analyst",
        role_group=RoleGroup.BUSINESS_FINANCE_OPERATIONS,
        jd_shape="Own GTM data, CRM quality, revenue reporting, forecasting, sales process, and funnel performance.",
        common_responsibilities=[
            "Build revenue dashboards and KPI reporting.",
            "Maintain CRM data quality and sales process logic.",
            "Analyze pipeline health, conversion, retention, CAC, LTV, and forecasting.",
            "Automate reporting and support sales, marketing, finance, and leadership.",
        ],
        common_requirements=[
            "CRM and sales/revenue analytics experience.",
            "Excel, SQL, BI, and dashboarding skills.",
            "Understanding of sales processes and revenue metrics.",
            "Ability to explain insights to GTM and executive stakeholders.",
        ],
        common_keywords=[
            "Salesforce",
            "HubSpot",
            "CRM",
            "pipeline",
            "forecasting",
            "conversion rate",
            "CAC",
            "LTV",
            "ARR",
            "MRR",
            "SQL",
            "dashboard",
        ],
        resume_fields_to_match=[
            "Domain context",
            "Top skills/tools",
            "Functional skills",
            "Achievements",
            "Tools used",
            "Dashboard / analysis sample",
        ],
        proof_to_show=[
            "revenue dashboard",
            "forecasting model",
            "CRM cleanup or automation result",
            "pipeline/conversion improvement metric",
        ],
    ),
    JobDescriptionPattern(
        role_title="Product Analyst",
        role_group=RoleGroup.BUSINESS_FINANCE_OPERATIONS,
        jd_shape="Analyze product, customer, market, funnel, and usage data to guide product decisions and product strategy.",
        common_responsibilities=[
            "Analyze product performance, customer behavior, and market trends.",
            "Build dashboards and product health metrics.",
            "Gather feedback and translate findings into product recommendations.",
            "Work with product, engineering, marketing, sales, support, and finance.",
        ],
        common_requirements=[
            "SQL, analytics, dashboarding, experimentation, or market research.",
            "Understanding of product metrics and customer behavior.",
            "Ability to communicate recommendations to product and business teams.",
        ],
        common_keywords=[
            "product analytics",
            "user behavior",
            "funnel",
            "retention",
            "cohort analysis",
            "A/B testing",
            "SQL",
            "Tableau",
            "Amplitude",
            "Mixpanel",
            "market research",
        ],
        resume_fields_to_match=[
            "Role identity",
            "Top skills/tools",
            "Domain context",
            "Case study",
            "Dashboard / analysis sample",
            "Achievements",
        ],
        proof_to_show=[
            "product metrics dashboard",
            "funnel or cohort analysis",
            "experiment analysis",
            "product recommendation with impact",
        ],
    ),
    JobDescriptionPattern(
        role_title="Strategy Analyst",
        role_group=RoleGroup.BUSINESS_FINANCE_OPERATIONS,
        jd_shape="Use analysis, research, modeling, and executive communication to support growth, pricing, market, or strategic decisions.",
        common_responsibilities=[
            "Analyze markets, competitors, customers, financials, or operations.",
            "Build models, dashboards, executive summaries, and strategic recommendations.",
            "Support pricing, growth initiatives, proposals, partnerships, or planning.",
            "Present findings to internal or external stakeholders.",
        ],
        common_requirements=[
            "Analytical modeling, research, communication, and business judgment.",
            "Excel, presentation, dashboard, or data analysis skills.",
            "Ability to structure ambiguous problems and recommend actions.",
        ],
        common_keywords=[
            "strategy",
            "market analysis",
            "pricing",
            "growth",
            "business case",
            "executive presentation",
            "KPI",
            "modeling",
            "competitive analysis",
            "ROI",
        ],
        resume_fields_to_match=[
            "Domain context",
            "Signature outcome",
            "Functional skills",
            "Case study",
            "Achievements",
            "Writing sample / publication",
        ],
        proof_to_show=[
            "strategy case study",
            "market sizing or pricing model",
            "executive presentation example",
            "decision influenced by analysis",
        ],
    ),
    JobDescriptionPattern(
        role_title="Procurement / Supply Chain Analyst",
        role_group=RoleGroup.BUSINESS_FINANCE_OPERATIONS,
        jd_shape="Analyze suppliers, spend, contracts, inventory, and supply-chain performance to reduce cost and improve reliability.",
        common_responsibilities=[
            "Analyze vendors, pricing, contracts, spend, and supplier performance.",
            "Prepare supply cost reports and procurement recommendations.",
            "Negotiate or support procurement contracts.",
            "Partner with operations, finance, suppliers, and internal stakeholders.",
        ],
        common_requirements=[
            "Procurement, supply chain, vendor, or contract analysis experience.",
            "Excel, ERP, reporting, and negotiation or stakeholder skills.",
            "Understanding of cost, quality, delivery, and supplier risk.",
        ],
        common_keywords=[
            "procurement",
            "supplier",
            "vendor management",
            "contracts",
            "spend analysis",
            "ERP",
            "inventory",
            "cost savings",
            "supply chain",
            "negotiation",
        ],
        resume_fields_to_match=[
            "Domain context",
            "Functional skills",
            "Scope",
            "Achievements",
            "Tools used",
            "Case study",
        ],
        proof_to_show=[
            "cost-savings metric",
            "supplier analysis",
            "contract/process improvement",
            "inventory or delivery performance improvement",
        ],
    ),
    JobDescriptionPattern(
        role_title="Risk / Compliance Analyst",
        role_group=RoleGroup.BUSINESS_FINANCE_OPERATIONS,
        jd_shape="Identify, measure, report, and mitigate financial, operational, regulatory, or control risks.",
        common_responsibilities=[
            "Analyze exposures, controls, incidents, and risk indicators.",
            "Prepare risk dashboards, reports, and mitigation recommendations.",
            "Support governance, compliance, audit, or regulatory processes.",
            "Collaborate with business, finance, legal, compliance, or technology teams.",
        ],
        common_requirements=[
            "Risk analysis, controls, reporting, governance, or compliance experience.",
            "Quantitative, Excel, SQL, BI, or risk-system skills.",
            "Knowledge of relevant regulations or frameworks when applicable.",
        ],
        common_keywords=[
            "risk assessment",
            "controls",
            "governance",
            "compliance",
            "audit",
            "risk dashboard",
            "VaR",
            "KRI",
            "regulatory",
            "mitigation",
        ],
        resume_fields_to_match=[
            "Domain skills",
            "Functional skills",
            "Responsibilities",
            "Achievements",
            "Tools used",
            "Licenses & Certifications",
        ],
        proof_to_show=[
            "risk dashboard",
            "control improvement",
            "audit/compliance result",
            "risk reduction or issue-resolution metric",
        ],
    ),
]


# ============================================================================
# EXACT APPLICATION STRATEGY MAP FOR THE CURRENT UMBRELLA
# Strategy is split into:
# 1. Profile-dependent: what must already be true or visible in the candidate.
# 2. JD-matching-dependent: what changes for each job description.
# 3. Other/application-process: channel, timing, networking, and tracking.
# ============================================================================

APPLICATION_STRATEGY_MAP_FOR_ATS_PORTFOLIO_UMBRELLA: Dict[str, object] = {
    "umbrella_name": "ATS-heavy and portfolio/proof-heavy professional roles",
    "core_principle": (
        "Use a stable, credible profile foundation; tailor summary, skills, "
        "top bullets, and proof artifacts to the JD; then improve conversion "
        "with channel choice, referrals, early applications, and tracking."
    ),
    "global_strategy": {
        "profile_dependent": [
            "Clear target role identity, not a broad generic profile.",
            "Relevant work history or projects that prove the target work.",
            "Tools and methods the candidate can actually defend in interviews.",
            "Measurable achievements: time saved, revenue, cost, quality, reliability, adoption, scale.",
            "A LinkedIn profile consistent with the resume.",
            "A portfolio, GitHub, dashboard, case study, or writing sample when proof matters.",
            "Seniority signal: scope, ownership, ambiguity handled, stakeholders, systems, or budget.",
        ],
        "jd_matching_dependent": [
            "Mirror the target title when truthful.",
            "Extract required tools, methods, domain terms, and outcomes from the JD.",
            "Rewrite the summary around the employer's problem.",
            "Reorder skills so the JD's strongest requirements appear first.",
            "Swap in the 3-6 most relevant experience bullets.",
            "Map each required responsibility to an experience bullet, project, or proof artifact.",
            "Use exact language naturally; do not add unsupported skills.",
            "If the JD is too far from the profile, skip or use a different resume variant.",
        ],
        "other_application_process": [
            "Prefer company career site for high-priority applications.",
            "Use LinkedIn, Indeed, Google Jobs, Wellfound, Built In, and niche boards for discovery.",
            "Apply early to fresh postings when fit is strong.",
            "Use referrals or warm outreach for roles where the candidate is a close match.",
            "Track source, resume version, date, contact, follow-up, interview result, and rejection pattern.",
            "Keep 3-5 base resume variants instead of rewriting from scratch.",
            "Optimize for interview conversion, not raw application count.",
        ],
    },
    "by_role": {
        "software_engineer_backend_frontend_fullstack": {
            "profile_dependent": [
                "Production or project experience building software, not just listing languages.",
                "Clear stack identity: backend, frontend, full-stack, mobile, platform, or systems.",
                "GitHub or demo helps most for junior/career-switch candidates; production impact matters more for experienced candidates.",
                "Evidence of code quality, debugging, testing, collaboration, and shipping.",
            ],
            "jd_matching_dependent": [
                "Match the primary language/framework from the JD.",
                "Match system type: APIs, frontend UI, distributed systems, integrations, performance, security.",
                "Use bullets showing ownership of similar systems and outcomes.",
                "Feature the most relevant project or repo, not every project.",
            ],
            "other_application_process": [
                "Referral and recruiter outreach matter when the resume is one of many similar profiles.",
                "Interview prep must match role type: coding, system design, frontend, backend, or behavioral.",
            ],
        },
        "data_analyst_bi_product_analyst": {
            "profile_dependent": [
                "SQL, spreadsheet, and BI ability must be visible.",
                "Portfolio is useful when experience is thin, but hiring managers value business thinking over polished charts.",
                "Projects should show business question, data cleaning, analysis, insight, and decision.",
                "Domain context is a differentiator: SaaS, finance, healthcare, ecommerce, operations, product.",
            ],
            "jd_matching_dependent": [
                "Match the BI tool and SQL/data stack when truthful.",
                "Match metric language: KPI, funnel, cohort, retention, revenue, cost, operations, product usage.",
                "Rewrite bullets to show decisions enabled, not just dashboards built.",
                "Choose portfolio pieces that resemble the employer's data problem.",
            ],
            "other_application_process": [
                "Apply to adjacent titles too: BI analyst, reporting analyst, operations analyst, product analyst, revenue analyst.",
                "Use portfolio links selectively; some reviewers will not click, so the resume must stand alone.",
            ],
        },
        "data_engineer_devops_sre_cloud": {
            "profile_dependent": [
                "Infrastructure, pipelines, reliability, automation, and production ownership are more important than generic projects.",
                "For DevOps/SRE, production work often beats portfolio work; for juniors, demos must be realistic, not tutorial copies.",
                "Metrics should show reliability, runtime, cost, deployment speed, incident reduction, or data quality.",
            ],
            "jd_matching_dependent": [
                "Match the required platform: AWS, Azure, GCP, Snowflake, BigQuery, Kubernetes, Terraform, Airflow, dbt.",
                "Lead with the most relevant platform bullets for that JD.",
                "Connect technical work to business outcomes: faster deploys, lower cloud cost, fewer incidents, better data quality.",
            ],
            "other_application_process": [
                "Technical credibility comes from interview discussion; be ready to explain architecture and tradeoffs.",
                "LinkedIn visibility can matter because recruiters search specific platform keywords.",
            ],
        },
        "cybersecurity_risk_compliance": {
            "profile_dependent": [
                "Credibility depends on security/risk context, frameworks, tools, incidents, controls, or audits.",
                "Certifications help when the role asks for them, but they do not replace hands-on evidence.",
                "Trust and precision matter; vague security claims are weak.",
            ],
            "jd_matching_dependent": [
                "Match framework and domain terms: NIST, SOC 2, ISO 27001, IAM, SIEM, vulnerability management, audit.",
                "Show control/risk outcomes, not only tool exposure.",
                "Align bullets to the JD's risk type: technical, operational, regulatory, financial, or third-party.",
            ],
            "other_application_process": [
                "Referrals and internal credibility help because risk/security teams screen for trust.",
                "Be ready with examples that do not expose confidential incidents or systems.",
            ],
        },
        "business_finance_operations_analyst": {
            "profile_dependent": [
                "Business impact must be visible: cost, revenue, margin, forecast accuracy, cycle time, adoption, productivity.",
                "Tools matter, but outcomes matter more than tool lists.",
                "Domain focus prevents the profile from looking scattered.",
                "Stakeholder and decision-support experience is a major signal.",
            ],
            "jd_matching_dependent": [
                "Match function: FP&A, operations, RevOps, procurement, strategy, product, risk, business systems.",
                "Translate existing bullets into the JD's business language.",
                "Use the same metric family as the JD: budget, forecast, pipeline, supplier, risk, process, KPI.",
                "Feature a case study or dashboard only if it supports the target function.",
            ],
            "other_application_process": [
                "Networking is especially important in finance and strategy-adjacent roles.",
                "Apply to domain-aligned companies where past industry context makes the profile more credible.",
            ],
        },
    },
    "anti_patterns": [
        "Applying with one generic resume to every role.",
        "Optimizing for a scanner score while the resume becomes unreadable.",
        "Listing every tool ever touched instead of the tools relevant to the JD.",
        "Portfolio projects that are copied tutorials or do not answer a business/technical problem.",
        "A profile that tries to be software, data, product, finance, and strategy all at once.",
        "Using referrals as a substitute for fit; referrals help but do not fix a mismatched profile.",
        "Hiding the strongest proof below weaker or unrelated experience.",
    ],
}


def get_section(section_id: str) -> ResumeSection:
    """Return one section by ID."""

    section_lookup = {section.section_id: section for section in ALL_RESUME_SECTIONS}
    return section_lookup[section_id]


def get_sections_for_role_group(role_group: RoleGroup) -> List[ResumeSection]:
    """Return the most useful sections for a role group."""

    return [get_section(section_id) for section_id in ROLE_GROUP_SECTION_MAP[role_group]]


def get_sections_for_hiring_pattern(hiring_pattern: HiringPattern) -> List[ResumeSection]:
    """Return the most useful sections for a hiring pattern."""

    return [get_section(section_id) for section_id in HIRING_PATTERN_SECTION_MAP[hiring_pattern]]


def get_field_names_for_section(section_id: str) -> List[str]:
    """Return just the field/item names for a section."""

    return [item.name for item in get_section(section_id).items]


def get_ats_portfolio_professional_field_map() -> Dict[str, object]:
    """Return the exact include/conditional/not-used field map for this umbrella."""

    return ATS_PORTFOLIO_PROFESSIONAL_FIELD_MAP


def get_jd_patterns_for_current_umbrella() -> List[JobDescriptionPattern]:
    """Return diverse job-description patterns for the current umbrella."""

    return JD_PATTERNS_FOR_ATS_PORTFOLIO_UMBRELLA


def get_application_strategy_for_current_umbrella() -> Dict[str, object]:
    """Return the exact application strategy map for the current umbrella."""

    return APPLICATION_STRATEGY_MAP_FOR_ATS_PORTFOLIO_UMBRELLA
