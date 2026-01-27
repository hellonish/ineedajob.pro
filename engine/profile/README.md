# Profile Engine

The **Profile Engine** is responsible for extracting, parsing, and unifying candidate data from multiple sources (Resumes, LinkedIn, Portfolios).

## Architecture

The module follows a **"Core + Context"** architecture (Hybrid Model):
- **Core (Strict)**: Critical fields like Identity, Work Experience, Skills, and Education are strictly typed and enforced.
- **Context (Dynamic)**: All other sections (Awards, Certifications, etc.) are captured in a flexible `dynamic_sections` dictionary.

## Module Structure

### 1. `parsers.py`
Contains the specific parsers for each file type, inheriting from `BaseProfileParser`.
- **`ResumeParser`**: Extracts text from PDF resumes.
- **`LinkedInParser`**: Extracts text from PDF LinkedIn exports.
- **`PortfolioParser`**: Extracts text from HTML portfolios.

### 2. `unifier.py`
Implements the logic to merge multiple profile sources into a single **Unified Profile**.
- **Strategy**:
    - **Identity**: Resume > LinkedIn > Portfolio.
    - **Skills**: Union of all unique skills.
    - **Work/Education**: Aggregated and sorted by date.
    - **Context**: Merged dynamically.

### 3. `models.py`
Defines the Pydantic schemas shared across all parsers (`HybridResume`, `Basics`, `WorkExperienceItem`, etc.).

### 4. `prompts.py`
Centralized repository of System Prompts used by the LLM for extraction.

## Usage

```python
from engine.profile import parse_resume, parse_linkedin, create_unified_profile

# 1. Parse individual files
resume_data = parse_resume(resume_bytes)
linkedin_data = parse_linkedin(linkedin_bytes)

# 2. Unified Profile
unified = create_unified_profile({
    'resume': resume_data,
    'linkedin': linkedin_data
})
```
