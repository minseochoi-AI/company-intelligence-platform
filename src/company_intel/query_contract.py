"""Meaning-level contracts shared by job, company, and analysis search paths.

The providers intentionally retain different raw fields.  This module is the
small common layer used to state whether a filter matched, failed, or simply
cannot be evaluated from a provider response.  It must not turn absence into a
negative fact.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum


class FilterVerdict(StrEnum):
    MATCH = "match"
    NO_MATCH = "no_match"
    UNKNOWN = "unknown"
    CONFLICT = "conflict"
    NOT_APPLICABLE = "not_applicable"


class UnknownPolicy(StrEnum):
    EXCLUDE = "exclude"
    REPORT = "report"
    INCLUDE = "include"


@dataclass(frozen=True)
class AtomicSearchProfile:
    """A provider-neutral search request.

    ``required_languages`` means a language demanded from the applicant.  It
    is deliberately distinct from a posting's display language.
    """

    countries: tuple[str, ...]
    job_terms: tuple[str, ...]
    occupations: tuple[str, ...] = ()
    locations: tuple[str, ...] = ()
    workplace_types: tuple[str, ...] = ()
    employment_types: tuple[str, ...] = ()
    required_languages: tuple[str, ...] = ()
    unknown_policy: UnknownPolicy = UnknownPolicy.EXCLUDE
    keyword_scope: str = "title_or_occupation"
    salary_currency: str | None = None
    salary_period: str | None = None
    salary_basis: str | None = None
    required_terms: tuple[str, ...] = ()
    preferred_terms: tuple[str, ...] = ()


@dataclass(frozen=True)
class ComparabilityPolicy:
    require_same_country: bool = True
    require_same_currency: bool = True
    require_same_period: bool = True
    require_same_unit: bool = True
    require_same_concept: bool = True


def combine_verdicts(verdicts: Iterable[FilterVerdict]) -> FilterVerdict:
    values = set(verdicts)
    if FilterVerdict.CONFLICT in values:
        return FilterVerdict.CONFLICT
    if FilterVerdict.NO_MATCH in values:
        return FilterVerdict.NO_MATCH
    if FilterVerdict.UNKNOWN in values:
        return FilterVerdict.UNKNOWN
    if values and values <= {FilterVerdict.MATCH, FilterVerdict.NOT_APPLICABLE}:
        return FilterVerdict.MATCH
    return FilterVerdict.NOT_APPLICABLE


def text_verdict(value: object, terms: tuple[str, ...]) -> FilterVerdict:
    if not terms:
        return FilterVerdict.NOT_APPLICABLE
    if value is None or not str(value).strip():
        return FilterVerdict.UNKNOWN
    lowered = str(value).casefold()
    return FilterVerdict.MATCH if any(term.casefold() in lowered for term in terms) else FilterVerdict.NO_MATCH
