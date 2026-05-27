"""Tests for reachout contact discovery."""

from pathlib import Path

from engine.joblens.reachout import (
    ConfidenceBand,
    ProfileSource,
    ReachoutCandidate,
    ReachoutCandidateValidationLLMResponse,
    ReachoutInput,
    ReachoutPersona,
    ReachoutQueryPlanLLMResponse,
    ReachoutResult,
    ReachoutSearchPlan,
    ReachoutSearchQuery,
    ReachoutService,
    ReachoutValidationResult,
    SearchResult,
    build_static_search_fn,
    canonical_linkedin_profile_url,
    pre_gate_search_results,
    search_ddgs,
    search_duckduckgo_html,
)


class FakeLLM:
    """Minimal fake LLM client returning queued responses."""

    def __init__(self, responses):
        """Initialize with one or more responses."""

        self.responses = list(responses)
        self.calls = []

    def complete(self, **kwargs):
        """Return the next queued response and record the call."""

        self.calls.append(kwargs)
        return self.responses.pop(0)


def _input():
    """Create a reachout input fixture."""

    return ReachoutInput(
        company_name="Atom Investors",
        company_website="https://atominvestors.com",
        target_contact_count=2,
        target_roles=["Application Engineer"],
    )


def _plan():
    """Create a search plan fixture."""

    query = ReachoutSearchQuery(
        query='site:linkedin.com/in "Atom Investors" "technical recruiter"',
        target_persona=ReachoutPersona.TECHNICAL_RECRUITER,
        intent="Find technical recruiters.",
        priority=1,
    )
    return ReachoutSearchPlan(
        company_name="Atom Investors",
        company_website="https://atominvestors.com",
        target_personas=[ReachoutPersona.TECHNICAL_RECRUITER],
        queries=[query],
        negative_filters=["jobs pages", "company pages"],
    )


def _search_results():
    """Create search result fixtures."""

    query = 'site:linkedin.com/in "Atom Investors" "technical recruiter"'
    return [
        SearchResult(
            title="Jane Carter - Technical Recruiter - Atom Investors | LinkedIn",
            url="https://www.linkedin.com/in/jane-carter-123456?trk=public_profile",
            snippet="Technical Recruiter at Atom Investors.",
            query=query,
            rank=1,
            source="static",
        ),
        SearchResult(
            title="Atom Investors Jobs | LinkedIn",
            url="https://www.linkedin.com/jobs/atom-investors-jobs",
            snippet="View jobs at Atom Investors.",
            query=query,
            rank=2,
            source="static",
        ),
    ]


def test_pre_gate_keeps_linkedin_people_and_rejects_jobs_pages():
    """Deterministically gate obvious non-person results before LLM validation."""

    passed, rejected = pre_gate_search_results(_search_results(), _input())

    assert len(passed) == 1
    assert passed[0].inferred_name == "Jane Carter"
    assert passed[0].normalized_profile_url == "https://www.linkedin.com/in/jane-carter-123456"
    assert len(rejected) == 1
    assert "URL is not a LinkedIn /in/ person profile." in rejected[0].rejection_reasons
    assert canonical_linkedin_profile_url("https://linkedin.com/in/jane-carter-123456?x=1") == "https://www.linkedin.com/in/jane-carter-123456"


def test_service_runs_two_llm_calls_search_and_validation():
    """Run full orchestration with fake query planner, static search, and fake validator."""

    reachout_input = _input()
    plan = _plan()
    planner_response = ReachoutQueryPlanLLMResponse(search_plan=plan, warnings=["Planner warning"])
    validation_response = ReachoutCandidateValidationLLMResponse(
        validation=ReachoutValidationResult(
            accepted_candidates=[
                ReachoutCandidate(
                    full_name="Jane Carter",
                    source_result_id="gated_1",
                    current_title="Technical Recruiter",
                    company="Atom Investors",
                    profile_url="https://www.linkedin.com/in/fake-llm-mutated-url",
                    profile_source=ProfileSource.LINKEDIN,
                    likely_persona=ReachoutPersona.TECHNICAL_RECRUITER,
                    confidence=0.94,
                    confidence_band=ConfidenceBand.HIGH,
                    confidence_reasons=["LinkedIn /in/ profile", "Snippet mentions Atom Investors"],
                    matched_query=plan.queries[0].query,
                    source_title="Jane Carter - Technical Recruiter - Atom Investors | LinkedIn",
                    source_snippet="Technical Recruiter at Atom Investors.",
                )
            ],
            warnings=["Validator warning"],
        )
    )
    llm = FakeLLM([planner_response, validation_response])
    search_fn = build_static_search_fn({plan.queries[0].query: _search_results()})

    result = ReachoutService(llm=llm, search_fn=search_fn).discover(reachout_input)

    assert result.candidates[0].full_name == "Jane Carter"
    assert result.candidates[0].profile_url == "https://www.linkedin.com/in/jane-carter-123456"
    assert len(result.raw_results) == 2
    assert len(result.pre_gated_results) == 1
    assert len(result.rejected_results) == 1
    assert result.warnings == ["Planner warning", "Validator warning"]
    assert llm.calls[0]["response_model"] is ReachoutQueryPlanLLMResponse
    assert llm.calls[1]["response_model"] is ReachoutCandidateValidationLLMResponse
    assert "two-call public reachout discovery pipeline" in llm.calls[0]["messages"][0]["content"]
    assert "Hard acceptance gates" in llm.calls[1]["messages"][0]["content"]


def test_service_skips_validator_when_no_results_pass_pre_gate():
    """Return a valid result without validator LLM work when pre-gate rejects everything."""

    reachout_input = _input()
    plan = _plan()
    llm = FakeLLM([ReachoutQueryPlanLLMResponse(search_plan=plan, warnings=["Planner warning"])])
    search_fn = build_static_search_fn({plan.queries[0].query: [_search_results()[1]]})

    result = ReachoutService(llm=llm, search_fn=search_fn).discover(reachout_input)

    assert result.candidates == []
    assert result.pre_gated_results == []
    assert len(result.raw_results) == 1
    assert len(result.rejected_results) == 1
    assert len(llm.calls) == 1
    assert result.warnings == [
        "Planner warning",
        "No search results passed deterministic pre-gate; skipped LLM candidate validation.",
    ]


def test_unreconciled_llm_candidate_is_rejected():
    """Reject candidates whose link cannot be traced back to pre-gated search results."""

    reachout_input = _input()
    plan = _plan()
    llm = FakeLLM(
        [
            ReachoutQueryPlanLLMResponse(search_plan=plan),
            ReachoutCandidateValidationLLMResponse(
                validation=ReachoutValidationResult(
                    accepted_candidates=[
                        ReachoutCandidate(
                            full_name="Invented Person",
                            source_result_id="missing_source",
                            current_title="Technical Recruiter",
                            company="Atom Investors",
                            profile_url="https://www.linkedin.com/in/invented-person",
                            profile_source=ProfileSource.LINKEDIN,
                            likely_persona=ReachoutPersona.TECHNICAL_RECRUITER,
                            confidence=0.95,
                            confidence_band=ConfidenceBand.HIGH,
                            matched_query=plan.queries[0].query,
                            source_title="Invented Person - Technical Recruiter - Atom Investors | LinkedIn",
                        )
                    ]
                )
            )
        ]
    )
    search_fn = build_static_search_fn({plan.queries[0].query: _search_results()})

    result = ReachoutService(llm=llm, search_fn=search_fn).discover(reachout_input)

    assert result.candidates == []
    assert any("could not be reconciled" in reason for rejected in result.rejected_results for reason in rejected.rejection_reasons)


def test_reconciliation_uses_canonical_profile_url_fallback():
    """Trace candidates back to gated results even when the LLM only returns a canonicalizable URL."""

    reachout_input = _input()
    plan = _plan()
    llm = FakeLLM(
        [
            ReachoutQueryPlanLLMResponse(search_plan=plan),
            ReachoutCandidateValidationLLMResponse(
                validation=ReachoutValidationResult(
                    accepted_candidates=[
                        ReachoutCandidate(
                            full_name="Jane Carter",
                            current_title="Technical Recruiter",
                            company="Atom Investors",
                            profile_url="https://linkedin.com/in/jane-carter-123456?trk=public_profile",
                            profile_source=ProfileSource.LINKEDIN,
                            likely_persona=ReachoutPersona.TECHNICAL_RECRUITER,
                            confidence=0.95,
                            confidence_band=ConfidenceBand.HIGH,
                            matched_query=plan.queries[0].query,
                            source_title="Jane Carter - Technical Recruiter - Atom Investors | LinkedIn",
                        )
                    ]
                )
            )
        ]
    )
    search_fn = build_static_search_fn({plan.queries[0].query: _search_results()})

    result = ReachoutService(llm=llm, search_fn=search_fn).discover(reachout_input)

    assert len(result.candidates) == 1
    assert result.candidates[0].source_result_id == "gated_1"
    assert result.candidates[0].profile_url == "https://www.linkedin.com/in/jane-carter-123456"


def test_missing_company_input_is_rejected():
    """Require company name or website."""

    try:
        ReachoutInput()
    except ValueError as error:
        assert "company_name or company_website" in str(error)
    else:
        raise AssertionError("Expected missing company input to fail")


def test_query_planner_adds_school_country_queries():
    """Generate school alumni searches from resume schools and target country."""

    reachout_input = ReachoutInput(
        company_name="Atom Investors",
        target_contact_count=5,
        target_roles=["Application Engineer"],
        schools=["Arizona State University"],
        job_location_country="United States",
    )
    llm = FakeLLM([ReachoutQueryPlanLLMResponse(search_plan=ReachoutSearchPlan(company_name="Atom Investors"))])

    plan, warnings = ReachoutService(llm=llm, search_fn=lambda query, limit: [])._plan_queries(reachout_input)

    assert warnings == []
    assert ReachoutPersona.SCHOOL_ALUMNI in plan.target_personas
    assert any(
        query.target_persona == ReachoutPersona.SCHOOL_ALUMNI
        and '"Arizona State University"' in query.query
        and '"United States"' in query.query
        for query in plan.queries
    )
    assert any('"Application Engineer"' in query.query for query in plan.queries)
    assert plan.search_strategy_notes == [
        "Added deterministic school-alumni search queries using resume schools and job-location country."
    ]


def test_query_planner_does_not_claim_school_queries_when_none_added():
    """Leave strategy notes unchanged when deterministic school queries already exist."""

    reachout_input = ReachoutInput(
        company_name="Atom Investors",
        target_contact_count=5,
        target_roles=["Application Engineer"],
        schools=["Arizona State University"],
        job_location_country="United States",
    )
    base_query = 'site:linkedin.com/in "Atom Investors" "Arizona State University" "United States"'
    role_query = 'site:linkedin.com/in "Atom Investors" "Arizona State University" "Application Engineer" "United States"'
    existing_plan = ReachoutSearchPlan(
        company_name="Atom Investors",
        queries=[
            ReachoutSearchQuery(
                query=base_query,
                target_persona=ReachoutPersona.SCHOOL_ALUMNI,
                intent="Find school alumni.",
                priority=1,
            ),
            ReachoutSearchQuery(
                query=role_query,
                target_persona=ReachoutPersona.SCHOOL_ALUMNI,
                intent="Find school alumni in target roles.",
                priority=2,
            ),
        ],
    )
    llm = FakeLLM([ReachoutQueryPlanLLMResponse(search_plan=existing_plan)])

    plan, warnings = ReachoutService(llm=llm, search_fn=lambda query, limit: [])._plan_queries(reachout_input)

    assert warnings == []
    assert plan.queries == existing_plan.queries
    assert plan.search_strategy_notes == []


def test_ddgs_provider_maps_results_without_credentials():
    """Map DDGS response dictionaries into SearchResult records."""

    class FakeDDGS:
        def text(self, query, **kwargs):
            assert kwargs["max_results"] == 2
            return [
                {
                    "title": "Jane Carter - Technical Recruiter - Atom Investors | LinkedIn",
                    "href": "https://www.linkedin.com/in/jane-carter-123456",
                    "body": "Technical Recruiter at Atom Investors.",
                }
            ]

    results = search_ddgs("site:linkedin.com/in Atom", 2, client=FakeDDGS())

    assert len(results) == 1
    assert results[0].source == "ddgs"
    assert results[0].url == "https://www.linkedin.com/in/jane-carter-123456"


def test_duckduckgo_html_provider_maps_results_without_credentials():
    """Map DuckDuckGo HTML result markup into SearchResult records."""

    class FakeResponse:
        text = """
        <html><body>
          <div class="result">
            <a class="result__a" href="/l/?kh=-1&uddg=https%3A%2F%2Fwww.linkedin.com%2Fin%2Fjane-carter-123456">
              Jane Carter - Technical Recruiter - Atom Investors | LinkedIn
            </a>
            <a class="result__snippet">Technical Recruiter at Atom Investors.</a>
          </div>
        </body></html>
        """

        def raise_for_status(self):
            return None

    class FakeSession:
        def post(self, *args, **kwargs):
            return FakeResponse()

    results = search_duckduckgo_html("site:linkedin.com/in Atom", 2, session=FakeSession())

    assert len(results) == 1
    assert results[0].source == "duckduckgo_html"
    assert results[0].url == "https://www.linkedin.com/in/jane-carter-123456"
    assert results[0].snippet == "Technical Recruiter at Atom Investors."


def test_sample_outputs_validate_against_schema():
    """Keep checked-in manual review outputs aligned with the reachout schema."""

    output_dir = Path(__file__).resolve().parent / "test_outputs"
    paths = sorted(output_dir.glob("*.reachout_fixture.json"))

    assert paths
    for path in paths:
        ReachoutResult.model_validate_json(path.read_text(encoding="utf-8"))
