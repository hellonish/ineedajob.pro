"""Reachout discovery orchestration."""

from typing import Any, Iterable, List, Optional, Sequence

from engine.utils import dedupe_warning_strings
from engine.xai_client import XAIStructuredClient

from .helpers import SearchFn, canonical_linkedin_profile_url, pre_gate_search_results, search_duckduckgo_html
from .models import (
    GatedSearchResult,
    ReachoutCandidate,
    ReachoutCandidateValidationLLMResponse,
    ReachoutInput,
    ReachoutPersona,
    ReachoutQueryPlanLLMResponse,
    ReachoutResult,
    ReachoutSearchPlan,
    ReachoutSearchQuery,
    ReachoutValidationResult,
    RejectedReachoutResult,
    SearchResult,
    SearchResultStatus,
)
from .prompts import build_candidate_validator_messages, build_query_planner_messages


class ReachoutService:
    """Plan searches, execute them, gate results, and validate contacts."""

    def __init__(
        self,
        llm: Any = None,
        search_fn: Optional[SearchFn] = None,
        timeout: int = 15,
    ):
        """Initialize dependencies."""

        self.llm = llm or XAIStructuredClient()
        self.timeout = timeout
        self.search_fn = search_fn or self._search

    def discover(self, reachout_input: ReachoutInput) -> ReachoutResult:
        """Run the full two-call reachout discovery pipeline."""

        search_plan, planner_warnings = self._plan_queries(reachout_input)
        raw_results = self._run_searches(search_plan.queries, reachout_input.target_contact_count)
        pre_gated_results, pre_gate_rejections = pre_gate_search_results(raw_results, reachout_input)
        if not pre_gated_results:
            return ReachoutResult(
                input=reachout_input,
                search_plan=search_plan,
                raw_results=raw_results,
                pre_gated_results=[],
                candidates=[],
                rejected_results=self._dedupe_rejections(pre_gate_rejections),
                warnings=dedupe_warning_strings(
                    [
                        *planner_warnings,
                        "No search results passed deterministic pre-gate; skipped LLM candidate validation.",
                    ]
                ),
            )

        validation = self._validate_candidates(reachout_input, search_plan, pre_gated_results)
        candidates, reconciliation_rejections, reconciliation_warnings = self._reconcile_candidates(
            validation.accepted_candidates,
            pre_gated_results,
            reachout_input.target_contact_count,
        )
        rejected_results = self._dedupe_rejections(
            [*pre_gate_rejections, *validation.rejected_results, *reconciliation_rejections]
        )
        warnings = dedupe_warning_strings([*planner_warnings, *validation.warnings, *reconciliation_warnings])
        return ReachoutResult(
            input=reachout_input,
            search_plan=search_plan,
            raw_results=raw_results,
            pre_gated_results=pre_gated_results,
            candidates=candidates,
            rejected_results=rejected_results,
            warnings=warnings,
        )

    def _search(self, query: str, limit: int) -> List[SearchResult]:
        """Run the default public search provider."""

        return search_duckduckgo_html(query, limit, timeout=self.timeout)

    def _plan_queries(self, reachout_input: ReachoutInput) -> tuple[ReachoutSearchPlan, List[str]]:
        """Create a targeted public-search plan with the structured LLM."""

        response = self.llm.complete(
            response_model=ReachoutQueryPlanLLMResponse,
            messages=build_query_planner_messages(reachout_input),
            temperature=0.0,
            max_tokens=12000,
        )
        return self._with_school_queries(reachout_input, response.search_plan), dedupe_warning_strings(response.warnings)

    def _with_school_queries(self, reachout_input: ReachoutInput, plan: ReachoutSearchPlan) -> ReachoutSearchPlan:
        """Add deterministic alumni queries from resume schools and job country."""

        if not reachout_input.include_school_alumni or not reachout_input.schools:
            return plan
        company = plan.company_name or reachout_input.company_name
        if not company:
            return plan

        existing = {query.query for query in plan.queries}
        queries = list(plan.queries)
        country = reachout_input.job_location_country or reachout_input.location
        role_terms = reachout_input.target_roles or ["software engineer"]
        next_priority = max((query.priority for query in queries), default=0) + 1
        added_deterministic_queries = False

        for school in reachout_input.schools:
            base_parts = [f'site:linkedin.com/in "{company}"', f'"{school}"']
            if country:
                base_parts.append(f'"{country}"')
            base_query = " ".join(base_parts)
            if base_query not in existing:
                existing.add(base_query)
                queries.append(
                    ReachoutSearchQuery(
                        query=base_query,
                        target_persona=ReachoutPersona.SCHOOL_ALUMNI,
                        intent=f"Find {school} alumni working at {company} in the target job country.",
                        priority=min(next_priority, 5),
                    )
                )
                added_deterministic_queries = True
                next_priority += 1

            for role in role_terms[:2]:
                role_parts = [f'site:linkedin.com/in "{company}"', f'"{school}"', f'"{role}"']
                if country:
                    role_parts.append(f'"{country}"')
                role_query = " ".join(role_parts)
                if role_query in existing:
                    continue
                existing.add(role_query)
                queries.append(
                    ReachoutSearchQuery(
                        query=role_query,
                        target_persona=ReachoutPersona.SCHOOL_ALUMNI,
                        intent=f"Find {school} alumni at {company} connected to {role} roles in the target job country.",
                        priority=min(next_priority, 5),
                    )
                )
                added_deterministic_queries = True
                next_priority += 1

        if not added_deterministic_queries:
            return plan

        personas = list(plan.target_personas)
        if ReachoutPersona.SCHOOL_ALUMNI not in personas:
            personas.append(ReachoutPersona.SCHOOL_ALUMNI)
        notes = [
            *plan.search_strategy_notes,
            "Added deterministic school-alumni search queries using resume schools and job-location country.",
        ]
        return plan.model_copy(
            update={
                "queries": queries,
                "target_personas": personas,
                "search_strategy_notes": dedupe_warning_strings(notes),
            }
        )

    def _run_searches(self, queries: Sequence[ReachoutSearchQuery], target_count: int) -> List[SearchResult]:
        """Execute generated queries."""

        results: List[SearchResult] = []
        per_query_limit = max(5, min(10, target_count))
        for query in sorted(queries, key=lambda item: item.priority):
            results.extend(self.search_fn(query.query, per_query_limit))
        return results

    def _validate_candidates(
        self,
        reachout_input: ReachoutInput,
        search_plan: ReachoutSearchPlan,
        gated_results: Sequence[GatedSearchResult],
    ) -> ReachoutValidationResult:
        """Validate and normalize pre-gated search results with the structured LLM."""

        response = self.llm.complete(
            response_model=ReachoutCandidateValidationLLMResponse,
            messages=build_candidate_validator_messages(reachout_input, search_plan, gated_results),
            temperature=0.0,
            max_tokens=18000,
        )
        warnings = dedupe_warning_strings([*response.validation.warnings, *response.warnings])
        return response.validation.model_copy(update={"warnings": warnings})

    def _reconcile_candidates(
        self,
        candidates: List[ReachoutCandidate],
        gated_results: List[GatedSearchResult],
        target_count: int,
    ) -> tuple[List[ReachoutCandidate], List[RejectedReachoutResult], List[str]]:
        """Copy final profile links from deterministic gated search results."""

        by_id, by_url = self._gated_result_indexes(gated_results)
        accepted: List[ReachoutCandidate] = []
        rejected: List[RejectedReachoutResult] = []
        warnings: List[str] = []
        seen_urls = set()

        for candidate in candidates:
            source = self._source_for_candidate(candidate, by_id, by_url)
            if source is None:
                rejected.append(self._unreconciled_candidate_rejection(candidate))
                warnings.append(
                    "Rejected an LLM candidate because its URL/source_result_id was not in pre-gated search results."
                )
                continue
            profile_url = (
                source.normalized_profile_url
                or canonical_linkedin_profile_url(source.result.url)
                or source.result.url
            )
            if profile_url in seen_urls:
                continue
            seen_urls.add(profile_url)
            accepted.append(self._candidate_with_source(candidate, source, profile_url))
            if len(accepted) >= target_count:
                break
        return accepted, rejected, warnings

    def _gated_result_indexes(
        self,
        gated_results: List[GatedSearchResult],
    ) -> tuple[dict[str, GatedSearchResult], dict[str, GatedSearchResult]]:
        """Index pre-gated results by source ID and canonical profile URL."""

        by_id = {result.source_result_id: result for result in gated_results}
        by_url = {}
        for result in gated_results:
            profile_url = result.normalized_profile_url or canonical_linkedin_profile_url(result.result.url)
            if profile_url:
                by_url[profile_url] = result
        return by_id, by_url

    def _source_for_candidate(
        self,
        candidate: ReachoutCandidate,
        by_id: dict[str, GatedSearchResult],
        by_url: dict[str, GatedSearchResult],
    ) -> GatedSearchResult | None:
        """Find the pre-gated source referenced by a candidate."""

        if candidate.source_result_id and candidate.source_result_id in by_id:
            return by_id[candidate.source_result_id]
        profile_url = canonical_linkedin_profile_url(candidate.profile_url)
        return by_url.get(profile_url or candidate.profile_url)

    def _unreconciled_candidate_rejection(self, candidate: ReachoutCandidate) -> RejectedReachoutResult:
        """Convert an unreconciled accepted candidate into a rejection."""

        return RejectedReachoutResult(
            title=candidate.source_title,
            url=candidate.profile_url,
            snippet=candidate.source_snippet,
            query=candidate.matched_query,
            status=SearchResultStatus.REJECTED_BY_LLM,
            rejection_reasons=["Accepted candidate could not be reconciled to a pre-gated search result."],
        )

    def _candidate_with_source(
        self,
        candidate: ReachoutCandidate,
        source: GatedSearchResult,
        profile_url: str,
    ) -> ReachoutCandidate:
        """Copy canonical source metadata onto an accepted candidate."""

        return candidate.model_copy(
            update={
                "source_result_id": source.source_result_id,
                "profile_url": profile_url,
                "matched_query": source.result.query,
                "source_title": source.result.title,
                "source_snippet": source.result.snippet,
            }
        )

    def _dedupe_rejections(self, values: Iterable[RejectedReachoutResult]) -> List[RejectedReachoutResult]:
        """Deduplicate rejected results by URL and reasons."""

        seen = set()
        result = []
        for value in values:
            key = (value.url.lower().rstrip("/"), tuple(value.rejection_reasons))
            if key in seen:
                continue
            seen.add(key)
            result.append(value)
        return result


def discover_reachout_contacts(
    company_name: Optional[str] = None,
    company_website: Optional[str] = None,
    target_contact_count: int = 10,
    target_roles: Optional[List[str]] = None,
    schools: Optional[List[str]] = None,
    job_location_country: Optional[str] = None,
    llm: Any = None,
    search_fn: Optional[SearchFn] = None,
) -> ReachoutResult:
    """Convenience function for reachout contact discovery."""

    reachout_input = ReachoutInput(
        company_name=company_name,
        company_website=company_website,
        target_contact_count=target_contact_count,
        target_roles=target_roles or [],
        schools=schools or [],
        job_location_country=job_location_country,
    )
    return ReachoutService(llm=llm, search_fn=search_fn).discover(reachout_input)
