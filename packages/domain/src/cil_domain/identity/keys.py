"""Canonical responsibility owner; migrated from src/company_intel/identity.py."""

from __future__ import annotations
from dataclasses import dataclass

SUPPORTED_IDENTIFIER_TYPES = {"CIK", "DART", "ICO", "LEI", "ISIN", "ALIO", "ATS"}


@dataclass(frozen=True)
class IdentifierLink:
    identifier_type: str
    identifier_value: str
    entity_id: str
    source: str
    confidence: float


@dataclass(frozen=True)
class ResolutionResult:
    status: str
    entity_id: str | None
    candidates: tuple[str, ...]
    reason: str | None = None


class CompanyIdentityResolver:
    def __init__(self) -> None:
        self._links: dict[tuple[str, str], list[IdentifierLink]] = {}

    def add(self, link: IdentifierLink) -> None:
        normalized_type = link.identifier_type.upper()
        if normalized_type not in SUPPORTED_IDENTIFIER_TYPES:
            raise ValueError(f"unsupported identifier type: {link.identifier_type}")
        if not link.identifier_value.strip() or not link.entity_id.strip():
            raise ValueError("identifier value and entity_id are required")
        self._links.setdefault(
            (normalized_type, link.identifier_value.strip()), []
        ).append(link)

    def resolve(self, identifier_type: str, identifier_value: str) -> ResolutionResult:
        links = self._links.get((identifier_type.upper(), identifier_value.strip()), [])
        entities = tuple(sorted({item.entity_id for item in links}))
        if not entities:
            return ResolutionResult("unresolved", None, (), "identifier_not_found")
        if len(entities) > 1:
            return ResolutionResult("ambiguous", None, entities, "multiple_entities")
        return ResolutionResult("resolved", entities[0], entities)

    def resolve_for_join(
        self, identifier_type: str, identifier_value: str
    ) -> ResolutionResult:
        """Only a unique, high-confidence identifier can attach other facts."""
        result = self.resolve(identifier_type, identifier_value)
        if result.status != "resolved":
            return result
        links = self._links[identifier_type.upper(), identifier_value.strip()]
        if max((link.confidence for link in links)) < 0.8:
            return ResolutionResult(
                "unresolved", None, result.candidates, "low_confidence_identifier"
            )
        return result


def resolve_candidate_company(
    resolver: CompanyIdentityResolver, identifier_type: str, identifier_value: str
) -> ResolutionResult:
    return resolver.resolve(identifier_type, identifier_value)


def explain_resolution(result: ResolutionResult) -> str:
    return result.reason or result.status
