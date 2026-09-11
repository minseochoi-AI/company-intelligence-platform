from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .models import CandidateMatch, SearchProfile
from .query_contract import FilterVerdict, text_verdict


def validate_search_profile(profile: SearchProfile) -> SearchProfile:
    if not profile.countries:
        raise ValueError("countries must contain at least one ISO country code")
    if not profile.job_keywords:
        raise ValueError("job_keywords must contain at least one explicit search term")
    unknown = set(profile.country_allocation) - set(profile.countries)
    if unknown:
        raise ValueError("country_allocation contains countries outside countries")
    if any(value < 0 for value in profile.country_allocation.values()):
        raise ValueError("country_allocation values cannot be negative")
    return profile


def build_company_universe(profile: SearchProfile, candidates: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    validate_search_profile(profile)
    return [row for row in candidates if row.get("country_code") in profile.countries]


def rank_candidates(profile: SearchProfile, candidates: Iterable[dict[str, Any]]) -> list[CandidateMatch]:
    rows = build_company_universe(profile, candidates)
    matches: list[CandidateMatch] = []
    for row in rows:
        capabilities = row.get("capabilities") if isinstance(row.get("capabilities"), dict) else {}
        missing = tuple(capability for capability in profile.required_capabilities if capabilities.get(capability) != "available")
        identity_status = row.get("identity_status", "unresolved")
        if identity_status != "resolved":
            matches.append(CandidateMatch(str(row.get("entity_id", "")), str(row.get("name", "")), row.get("country_code"), "unknown", 0, (), "identity_unresolved"))
            continue
        if missing:
            matches.append(CandidateMatch(str(row.get("entity_id", "")), str(row.get("name", "")), row.get("country_code"), "excluded", 0, (), "missing_capability:" + ",".join(missing)))
            continue
        title = " ".join(str(row.get(key, "")) for key in ("name", "title", "occupation_label", "industry"))
        verdict = text_verdict(title, profile.job_keywords)
        if verdict == FilterVerdict.NO_MATCH:
            matches.append(CandidateMatch(str(row.get("entity_id", "")), str(row.get("name", "")), row.get("country_code"), "excluded", 0, (), "job_keyword_not_matched"))
            continue
        if verdict == FilterVerdict.UNKNOWN:
            matches.append(CandidateMatch(str(row.get("entity_id", "")), str(row.get("name", "")), row.get("country_code"), "unknown", 0, (), "job_keyword_unknown"))
            continue
        keyword_hits = sum(1 for keyword in profile.job_keywords if keyword.casefold() in title.casefold())
        score = len(profile.required_capabilities) * 100 + keyword_hits * 10 + (1 if row.get("evidence_urls") else 0)
        matches.append(CandidateMatch(
            str(row.get("entity_id", "")), str(row.get("name", "")), row.get("country_code"), "matched", score,
            tuple(sorted(profile.required_capabilities)), None, tuple(sorted(str(url) for url in row.get("evidence_urls", []) if url)),
        ))
    return sorted(matches, key=lambda item: (item.status != "matched", -item.score, item.entity_id))


def explain_candidate(match: CandidateMatch) -> dict[str, Any]:
    return {
        "entity_id": match.entity_id, "status": match.status, "score": match.score,
        "matched_capabilities": list(match.matched_capabilities), "exclusion_reason": match.exclusion_reason,
        "evidence": list(match.evidence),
    }


def candidate_verdict(match: CandidateMatch) -> FilterVerdict:
    if match.status == "matched":
        return FilterVerdict.MATCH
    if match.status == "unknown":
        return FilterVerdict.UNKNOWN
    return FilterVerdict.NO_MATCH
