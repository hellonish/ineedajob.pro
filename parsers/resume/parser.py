"""Resume parser: extract text from PDF or DOCX (file path or stream) and return a Person.

Accepts a file path for local testing or a binary stream/bytes for API upload.
Supports PDF and DOCX. Use parse() for raw text in Person.summary; use
parse_with_skill(source, llm, ...) for full Person via the extract-person skill.
"""

from io import BytesIO
from pathlib import Path
from typing import Any, BinaryIO, Union

from models.models import Person, SkillGroup
from skills.extract_person import extract_person

Source = Union[str, Path, BinaryIO, bytes]

PDF_MAGIC = b"%PDF"
ZIP_MAGIC = b"PK\x03\x04"


def _detect_type(data: bytes) -> str:
    if data.startswith(PDF_MAGIC):
        return "pdf"
    if data.startswith(ZIP_MAGIC):
        return "docx"
    return "unknown"


def _read_source(source: Source) -> tuple[bytes, str]:
    """Read bytes from path, stream, or raw bytes; return (bytes, detected type)."""
    if isinstance(source, bytes):
        return source, _detect_type(source)
    if isinstance(source, (str, Path)):
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"Resume file not found: {path}")
        data = path.read_bytes()
        return data, _detect_type(data)
    data = source.read()
    if isinstance(data, str):
        data = data.encode("utf-8", errors="replace")
    return data, _detect_type(data)


def _extract_pdf(data: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(BytesIO(data))
    parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            parts.append(text)
    return "\n\n".join(parts)


def _extract_docx(data: bytes) -> str:
    from docx import Document

    doc = Document(BytesIO(data))
    parts = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(parts)


def _person_from_raw_text(raw_text: str) -> Person:
    """Build a Person with summary set to raw resume text; other fields empty."""
    return Person(
        name="",
        headline="",
        summary=raw_text.strip(),
        location="",
        company="",
        title="",
        email="",
        phone="",
        website="",
        languages=[],
        extracurriculars=[],
        skills=SkillGroup(skills={}),
        social_media=[],
        educations=[],
        experiences=[],
        projects=[],
        certifications=[],
        awards=[],
    )


class ResumeParser:
    """Parses resume files (PDF or DOCX) from file path or binary stream into a Person."""

    def parse(self, source: Source) -> Person:
        """Extract text from a resume file or stream; return Person with summary only.

        Args:
            source: File path (str or Path), binary stream (e.g. UploadFile), or bytes.

        Returns:
            Person with summary=extracted text; other fields empty.
        """
        data, kind = _read_source(source)
        if kind == "pdf":
            raw_text = _extract_pdf(data)
        elif kind == "docx":
            raw_text = _extract_docx(data)
        else:
            raise ValueError(
                f"Unsupported resume format (detected: {kind or 'unknown'}). Use PDF or DOCX."
            )
        return _person_from_raw_text(raw_text)

    def parse_with_skill(
        self,
        source: Source,
        llm: Any,
        model: str | None = None,
        **kwargs: Any,
    ) -> Person:
        """Extract text from the resume, then run the extract-person skill to get a full Person.

        Args:
            source: File path (str or Path), binary stream, or bytes (for API).
            llm: Any client implementing generate_structured (e.g. OpenAIClient, AnthropicClient).
            model: Optional model name.
            **kwargs: Passed to the skill (e.g. max_tokens, temperature).

        Returns:
            Person with structured data from the extract-person skill.
        """
        person_raw = self.parse(source)
        if not person_raw.summary.strip():
            return person_raw
        return extract_person(person_raw.summary, llm, model=model, **kwargs)


def _person_to_md(person: Person) -> str:
    """Format a Person as Markdown for writing to an MD file. No truncation; full content."""
    lines: list[str] = ["# " + (person.name or "Profile"), ""]
    if (person.headline or "").strip():
        lines.append(f"**{person.headline}**")
        lines.append("")
    if (person.title or "").strip() and (person.company or "").strip():
        lines.append(f"{person.title} at {person.company}")
    if (person.location or "").strip():
        lines.append(f"Location: {person.location}")
    for label, val in [("Email", person.email), ("Phone", person.phone), ("Website", person.website)]:
        if (val or "").strip():
            lines.append(f"{label}: {val}")
    if person.languages:
        lines.append(f"Languages: {', '.join(person.languages)}")
    if person.social_media:
        lines.append(f"Social: {', '.join(person.social_media)}")
    lines.extend(["", "## Summary", "", person.summary or "", ""])
    if person.experiences:
        lines.extend(["## Experience", ""])
        for e in person.experiences:
            lines.append(f"### {e.title} at {e.company}")
            lines.append(f"- Location: {e.location} | {e.start_date} – {e.end_date or 'present'}")
            if e.description:
                lines.append(e.description)
            if e.urls:
                lines.append("URLs: " + ", ".join(e.urls))
            if e.skills:
                lines.append("Skills: " + ", ".join(e.skills))
            lines.append("")
        lines.append("")
    if person.educations:
        lines.extend(["## Education", ""])
        for e in person.educations:
            lines.append(f"### {e.degree} in {e.field_of_study}, {e.school}")
            lines.append(f"- {e.start_date} – {e.end_date or 'present'}")
            if e.description:
                lines.append(e.description)
            if e.subjects:
                lines.append("Subjects: " + ", ".join(e.subjects))
            lines.append("")
        lines.append("")
    if person.skills and person.skills.skills:
        lines.extend(["## Skills", ""])
        for group, skills in person.skills.skills.items():
            if skills:
                lines.append(f"### {group}")
                lines.append(", ".join(skills))
                lines.append("")
        lines.append("")
    if person.projects:
        lines.extend(["## Projects", ""])
        for p in person.projects:
            lines.append(f"### {p.name}")
            lines.append(p.description or "")
            if p.urls:
                lines.append("URLs: " + ", ".join(p.urls))
            if p.skills:
                lines.append("Skills: " + ", ".join(p.skills))
            lines.append("")
        lines.append("")
    if person.extracurriculars:
        lines.extend(["## Extracurriculars", ""])
        for x in person.extracurriculars:
            lines.append(f"### {x.name}")
            lines.append(x.description or "")
            if x.urls:
                lines.append("URLs: " + ", ".join(x.urls))
            if x.skills:
                lines.append("Skills: " + ", ".join(x.skills))
            lines.append("")
        lines.append("")
    if person.certifications:
        lines.extend(["## Certifications", ""])
        for c in person.certifications:
            lines.append(f"### {c.name} ({c.datetime})")
            lines.append(c.description or "")
            if c.urls:
                lines.append("URLs: " + ", ".join(c.urls))
            if c.skills:
                lines.append("Skills: " + ", ".join(c.skills))
            lines.append("")
        lines.append("")
    if person.awards:
        lines.extend(["## Awards", ""])
        for a in person.awards:
            lines.append(f"### {a.name} ({a.datetime})")
            lines.append(a.description or "")
            if a.urls:
                lines.append("URLs: " + ", ".join(a.urls))
            if a.skills:
                lines.append("Skills: " + ", ".join(a.skills))
            lines.append("")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    from dotenv import load_dotenv
    from llm import GeminiClient

    _root = Path(__file__).resolve().parent.parent.parent
    load_dotenv(_root / ".env")
    _resume_path = _root / "profiles" / "sharma_nishant.pdf"
    _out_path = Path(__file__).resolve().parent / "output_resume.md"
    if not _resume_path.exists():
        print(f"Resume not found: {_resume_path}")
        raise SystemExit(1)
    llm = GeminiClient()
    person = ResumeParser().parse_with_skill(_resume_path, llm, model="gemini-2.0-flash")
    _out_path.write_text(_person_to_md(person), encoding="utf-8")
    print(f"Wrote {_out_path}")
