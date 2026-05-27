"""Tests for profile service adapters."""

from engine.profile import (
    NormalizedProfileComponents,
    ParsedExperienceItem,
    ParsedProfileNote,
    ParsedRecommendationItem,
    ParsedVolunteerItem,
    ProfileExtractionResult,
    profile_extraction_to_unified_profile,
)


def test_experience_adapter_derives_current_status_and_avoids_redundant_achievements():
    """Adapt current roles without duplicating achievements in description."""

    extraction = ProfileExtractionResult(
        documents=[],
        components=NormalizedProfileComponents(
            experience=[
                ParsedExperienceItem(
                    job_title="AI Engineer",
                    company="Acme",
                    start_date="2024",
                    end_date="Present",
                    scope=["Platform engineering"],
                    responsibilities=["Owned profile ingestion", "Reduced duplicate parsing by 30%"],
                    achievements=["Reduced duplicate parsing by 30%", "Launched profile parser"],
                )
            ]
        )
    )

    profile = profile_extraction_to_unified_profile(extraction)
    experience = profile.work_experience[0]

    assert experience.is_current is True
    assert experience.description == ["Platform engineering", "Owned profile ingestion"]
    assert experience.achievements == ["Reduced duplicate parsing by 30%", "Launched profile parser"]


def test_dynamic_sections_include_all_non_empty_extracted_sections():
    """Carry extracted optional sections into the API profile payload."""

    extraction = ProfileExtractionResult(
        documents=[],
        components=NormalizedProfileComponents(
            volunteer_experience=[ParsedVolunteerItem(organization="Open Data", role="Volunteer")],
            recommendations=[ParsedRecommendationItem(recommender_name="Jane", quote="Great collaborator.")],
            notes=[
                ParsedProfileNote(category="availability", text="Immediate"),
                ParsedProfileNote(category="work_authorization", text="Authorized"),
                ParsedProfileNote(category="application_document", text="Portfolio PDF - portfolio"),
            ],
        ),
        warnings=["review manually"],
    )

    sections = profile_extraction_to_unified_profile(extraction).dynamic_sections

    assert sections["volunteer_experience"][0]["organization"] == "Open Data"
    assert sections["recommendations"][0]["quote"] == "Great collaborator."
    assert sections["notes"][0]["category"] == "availability"
    assert sections["notes"][0]["text"] == "Immediate"
    assert sections["notes"][1]["text"] == "Authorized"
    assert sections["notes"][2]["text"] == "Portfolio PDF - portfolio"
    assert sections["warnings"] == ["review manually"]
    assert "featured" not in sections
