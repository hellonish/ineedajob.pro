"""Entry point to run the resume parser and write Person to output_resume.md.

Run from project root: python -m parsers.run_resume
Uses Gemini 2.0 Flash; load .env for GEMINI_API_KEY or GOOGLE_API_KEY.
"""

from pathlib import Path

from dotenv import load_dotenv
from llm import GeminiClient

from parsers.resume.parser import ResumeParser, _person_to_md

if __name__ == "__main__":
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    _root = Path(__file__).resolve().parent.parent
    _resume_path = _root / "profiles" / "sharma_nishant.pdf"
    _out_path = Path(__file__).resolve().parent / "resume" / "output_resume.md"
    if not _resume_path.exists():
        print(f"Resume not found: {_resume_path}")
        raise SystemExit(1)
    llm = GeminiClient()
    person = ResumeParser().parse_with_skill(_resume_path, llm, model="gemini-2.0-flash")
    _out_path.write_text(_person_to_md(person), encoding="utf-8")
    print(f"Wrote {_out_path}")
