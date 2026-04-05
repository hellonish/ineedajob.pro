"""Portfolio parser: fetch a URL and return structured data or a Person via the extract-person skill.

Accepts a URL path. Use parse(url) for raw ParsedPortfolio; use
parse_with_skill(url, llm, ...) for full Person via the extract-person skill.
"""

from typing import Any
from urllib.parse import urljoin

from pydantic import BaseModel

from models.models import Person, SkillGroup
from skills.extract_person import extract_person


class ParsedPortfolio(BaseModel):
    """Raw result of portfolio fetch: URL, title, description, links, sections."""

    url: str
    title: str = ""
    description: str = ""
    links: list[str] = []
    sections: dict[str, str] = {}


def _normalize_link(base_url: str, href: str) -> str | None:
    href = (href or "").strip()
    if not href or href.startswith("#") or href.lower().startswith(
        ("mailto:", "tel:", "javascript:")
    ):
        return None
    try:
        return urljoin(base_url, href)
    except Exception:
        return None


def _portfolio_to_content(parsed: ParsedPortfolio) -> str:
    """Build a single text blob from portfolio parse for the extract-person skill."""
    parts = []
    if parsed.title:
        parts.append(f"Title: {parsed.title}")
    if parsed.description:
        parts.append(f"Description: {parsed.description}")
    for heading, body in parsed.sections.items():
        parts.append(f"\n## {heading}\n{body}")
    if parsed.links:
        parts.append("\nLinks: " + ", ".join(parsed.links[:50]))
    return "\n".join(parts) if parts else ""


class PortfolioParser:
    """Parses a portfolio or personal site from a URL; can return raw data or Person via skill."""

    def __init__(self, timeout_seconds: float = 15.0, max_links: int = 200) -> None:
        self._timeout = timeout_seconds
        self._max_links = max_links

    def parse(self, url: str) -> ParsedPortfolio:
        """Fetch URL and extract title, description, links, and sections.

        Args:
            url: Full portfolio or page URL (e.g. https://example.com).

        Returns:
            ParsedPortfolio with title, description, links, sections.
        """
        import httpx
        from bs4 import BeautifulSoup

        url = url.strip()
        if not url.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")

        with httpx.Client(timeout=self._timeout, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            html = response.text
            final_url = str(response.url)

        soup = BeautifulSoup(html, "html.parser")

        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()

        description = ""
        meta = soup.find("meta", attrs={"name": "description"}) or soup.find(
            "meta", attrs={"property": "og:description"}
        )
        if meta and meta.get("content"):
            description = (meta["content"] or "").strip()

        seen: set[str] = set()
        links: list[str] = []
        for a in soup.find_all("a", href=True):
            if len(links) >= self._max_links:
                break
            full = _normalize_link(final_url, a["href"])
            if not full or full in seen:
                continue
            seen.add(full)
            links.append(full)

        sections: dict[str, str] = {}
        current_heading = "intro"
        current_parts: list[str] = []
        for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]):
            name = tag.name
            text = (tag.get_text() or "").strip()
            if not text:
                continue
            if name and name[0] == "h":
                if current_parts and current_heading:
                    sections[current_heading] = "\n".join(current_parts).strip()
                current_heading = text[:80].replace("\n", " ")
                current_parts = []
            else:
                current_parts.append(text)
        if current_parts and current_heading:
            sections[current_heading] = "\n".join(current_parts).strip()

        return ParsedPortfolio(
            url=final_url,
            title=title,
            description=description,
            links=links,
            sections=sections,
        )

    def parse_with_skill(
        self,
        url: str,
        llm: Any,
        model: str | None = None,
        **kwargs: Any,
    ) -> Person:
        """Fetch URL, build content, then run the extract-person skill to get a full Person.

        Args:
            url: Portfolio or page URL.
            llm: Any client implementing generate_structured (e.g. OpenAIClient, AnthropicClient).
            model: Optional model name.
            **kwargs: Passed to the skill (e.g. max_tokens, temperature).

        Returns:
            Person with structured data from the extract-person skill.
        """
        parsed = self.parse(url)
        content = _portfolio_to_content(parsed)
        if not content.strip():
            return Person(
                name="",
                headline=parsed.title or "",
                summary=parsed.description or "",
                location="",
                company="",
                title="",
                email="",
                phone="",
                website=parsed.url,
                languages=[],
                extracurriculars=[],
                skills=SkillGroup(skills={}),
                social_media=parsed.links[:20] if parsed.links else [],
                educations=[],
                experiences=[],
                projects=[],
                certifications=[],
                awards=[],
            )
        return extract_person(content, llm, model=model, **kwargs)


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
    from pathlib import Path

    from dotenv import load_dotenv
    from llm import GeminiClient

    _root = Path(__file__).resolve().parent.parent.parent
    load_dotenv(_root / ".env")
    _url = "https://www.hellonish.dev"
    _out_path = Path(__file__).resolve().parent / "output_portfolio.md"
    llm = GeminiClient()
    person = PortfolioParser().parse_with_skill(_url, llm, model="gemini-2.0-flash")
    _out_path.write_text(_person_to_md(person), encoding="utf-8")
    print(f"Wrote {_out_path}")
