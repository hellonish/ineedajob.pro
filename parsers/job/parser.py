"""Job posting parser: raw text or file path to JobListing.

Accepts a string (pasted job text) or a file path (e.g. .txt, .md, .html).
Use parse(source) for raw text; use parse_with_skill(source, llm, ...) for
full JobListing via the extract-job skill.
"""

from pathlib import Path
from typing import Any, Union

from models.models import Company, JobListing
from skills.extract_job import extract_job

Source = Union[str, Path]


def _read_source(source: Source) -> str:
    """Return job posting text from a string or file path."""
    if isinstance(source, Path):
        if not source.exists():
            raise FileNotFoundError(f"Job file not found: {source}")
        return source.read_text(encoding="utf-8", errors="replace").strip()
    if isinstance(source, str):
        s = source.strip()
        if "\n" in s or len(s) > 512:
            return s
        path = Path(source)
        if path.exists() and path.is_file():
            return path.read_text(encoding="utf-8", errors="replace").strip()
        return s
    raise TypeError("source must be str or Path")


class JobParser:
    """Parses job postings from raw text or a file into a JobListing."""

    def parse(self, source: Source) -> str:
        """Return the raw job posting text from a string or file.

        Args:
            source: Job text (str) or path to a file containing the job post (.txt, .md, .html).

        Returns:
            Raw job posting text for further use or for passing to parse_with_skill.
        """
        return _read_source(source)

    def parse_with_skill(
        self,
        source: Source,
        llm: Any,
        model: str | None = None,
        **kwargs: Any,
    ) -> JobListing:
        """Extract job posting text, then run the extract-job skill to get a structured JobListing.

        Args:
            source: Job text (str) or path to a file containing the job post.
            llm: Any client implementing generate_structured (e.g. OpenAIClient, AnthropicClient).
            model: Optional model name.
            **kwargs: Passed to the skill (e.g. max_tokens, temperature).

        Returns:
            JobListing with structured data from the extract-job skill.
        """
        content = self.parse(source)
        if not content:
            return JobListing(
                job_title="",
                company=Company(name=""),
                location="",
            )
        return extract_job(content, llm, model=model, **kwargs)


if __name__ == "__main__":
    from dotenv import load_dotenv
    from llm import GeminiClient

    _root = Path(__file__).resolve().parent.parent.parent
    load_dotenv(_root / ".env")

    _sample_job = """
AI for Chip Design Intern - Summer 2026
position
Santa Clara, CA
time
Internship
remote
Onsite
seniority
Intern
workcard
Start in 2026 Summer
97%
STRONG MATCH
100%
Exp. Level
99%
Skill
72%
Industry Exp.
ftfMaximize your interview chances
NVIDIA has been a leader in computer graphics and accelerated computing for over 25 years, and they are seeking an AI for Chip Design Intern for Summer 2026. This role involves developing algorithms for AI applications in chip design and engaging with the latest advancements in machine learning and AI.
Artificial Intelligence (AI)
Semiconductor
Consumer Goods
Hardware
Software
Apps
AI Infrastructure
Consumer Electronics
Foundational AI
GPU
Virtual Reality
check
Growth Opportunities
check
H1B Sponsor Likelynote

Insider Connection @NVIDIA
5 email credits available today
note
Discover valuable connections within the company who might provide insights and potential referrals.
Get 3x more responses when you reach out via email instead of LinkedIn.
Beyond your network
Z
G
F
A
X
Zhenzhen Li & 4 connections
From your previous company
A
A
H
Z
S
Alessandro Morari & 4 connections
Previously@New York University and...
from your School
P
Z
H
N
S
Priyadarshani Jha & 4 connections
@Dr. A.P.J. Abdul Kalam Technical University and...
Find Any Email

Responsibilities
Develop and optimize retrieval and generation algorithms for enterprise data (text, code, and images) to build advanced AI applications that transform chip design
Drive impact by designing and deploying LLM-powered solutions for engineering assistants and multi-turn, multi-modal dialogue systems
Make a difference by leveraging AI technologies to solve complex problems in chip design, driving innovation and meaningful impact across the industry
Join a dynamic, collaborative team where creativity and fresh ideas are encouraged
Stay ahead by engaging with the latest advancements in machine learning and AI to create state-of-the-art solutions
Lead with purpose and maintain high-quality engineering practices that inspire others to achieve excellence

Qualification
check
Represents the skills you have
Find out how your skills align with this job's requirements. If anything seems off, you can easily click on the tags to select or unselect skills to reflect your actual expertise.

checkPython
checkLarge language models
checkData structures
checkAlgorithms
checkSoftware engineering principles
checkAnalytical skills
Required
Pursuing BS or MS in Electrical Engineering, Computer Science/Engineering, or a related subject area
Proficiency in rapid prototyping using languages like Python (preferred), with strong foundational knowledge of data structures, algorithms, and software engineering principles
Familiarity with large language models, advanced Retrieval-Augmented Generation (RAG) pipelines, vector databases and agentic frameworks
Strong analytical, communication, and interpersonal skills, with a proven track record to thrive in dynamic, product-focused, and distributed teams
A proactive approach to problem-solving and a willingness to acquire new skills and knowledge as needed to achieve results
Preferred
Proficiency in rapid prototyping using languages like Python

Benefits
Intern benefits

Company
NVIDIA
twitter
twitter
twitter
Glassdoor
4.6
company-logo
NVIDIA is a computing platform company operating at the intersection of graphics, HPC, and AI.
dateFounded in 1993
location
Santa Clara, California, USA
people-size10001+ employees
web-link
https://www.nvidia.com
H1B Sponsorship
NVIDIA has a track record of offering H1B sponsorships. Please note that this does not guarantee sponsorship for this specific role. Below presents additional info for your reference. (Data Powered by US Department of Labor)
Distribution of Different Job Fields Receiving Sponsorship
Represents job field similar to this job
Trends of Total Sponsorships
2025 (1877)
2024 (1355)
2023 (976)
2022 (835)
2021 (601)
2020 (529)
Funding
Current Stage
Public Company
Total Funding
$4.09B
Key Investors
ARPA-E
ARK Investment Management
SoftBank Vision Fund
2023-05-09
Grant· $5M
2022-08-09
Post Ipo Equity· $65M
2021-02-18
Post Ipo Equity
Leadership Team
leader-logo
Jensen Huang
Founder and CEO
linkedin
leader-logo
Michael Kagan
Chief Technology Officer
linkedin
Recent News
Investing.com
Nvidia sets $4 million target cash bonus for CEO Huang under fiscal 2027 plan
2026-03-07
    """

    llm = GeminiClient()
    job = JobParser().parse_with_skill(_sample_job, llm, model="gemini-2.0-flash")

    print("Job title:", job.job_title)
    print("Company:", job.company.name)
    print("Location:", job.location)
    print("Experience level:", job.experience_level)
    print("Qualifications required:", job.qualifications_required[:5] if job.qualifications_required else [])
    print("Skills tags:", job.skills_tags[:10] if job.skills_tags else [])
    print("Responsibilities:", len(job.responsibilities))

    _out_path = Path(__file__).resolve().parent / "output_job.json"
    _out_path.write_text(job.model_dump_json(indent=2), encoding="utf-8")
    print(f"Wrote full JobListing to {_out_path}")
