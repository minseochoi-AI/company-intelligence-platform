from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pandas as pd

from .query_contract import FilterVerdict, UnknownPolicy, text_verdict

JOB_COLUMNS = (
    "provider", "job_id", "entity_id", "company_name", "company_type", "industry_raw",
    "title_raw", "occupation_label", "occupation_code", "occupation_system",
    "country_code", "location_raw", "city", "region", "workplace_type",
    "employment_type", "employment_type_raw", "posting_language", "salary_min",
    "salary_max", "salary_currency", "salary_period", "salary_period_raw", "salary_basis",
    "posted_at", "updated_at", "closing_at", "snapshot_at", "is_active", "source_url",
    "normalization_notes",
)
REQUIREMENT_COLUMNS = (
    "provider", "job_id", "company_name", "requirement_id", "requirement_kind",
    "normalized_key", "label", "necessity", "value", "proficiency", "evidence_scope",
    "source_url", "confidence",
)
EXCLUSION_COLUMNS = ("provider", "job_id", "company_name", "field", "reason", "observed_value")
SOURCE_COLUMNS = ("provider", "snapshot_at", "record_count", "source_url", "coverage", "limitations")
OVERLAP_COLUMNS = (
    "requirement_kind", "normalized_key", "label", "required_count", "preferred_count",
    "posting_count", "company_count", "country_count", "prevalence",
)


@dataclass(frozen=True)
class JobSearchProfile:
    countries: tuple[str, ...]
    job_keywords: tuple[str, ...]
    occupations: tuple[str, ...] = ()
    locations: tuple[str, ...] = ()
    workplace_types: tuple[str, ...] = ()
    employment_types: tuple[str, ...] = ()
    languages: tuple[str, ...] = ()
    industries: tuple[str, ...] = ()
    company_types: tuple[str, ...] = ()
    minimum_salary_floor: float | None = None
    maximum_salary_ceiling: float | None = None
    salary_currency: str | None = None
    salary_period: str | None = None
    salary_basis: str | None = None
    required_requirement_terms: tuple[str, ...] = ()
    preferred_requirement_terms: tuple[str, ...] = ()
    required_languages: tuple[str, ...] = ()
    active_only: bool = True
    country_allocation: dict[str, int] = field(default_factory=dict)
    unknown_policy: str = "exclude"
    keyword_scope: str = "title_or_occupation"


@dataclass(frozen=True)
class JobDataFrames:
    companies: pd.DataFrame
    jobs: pd.DataFrame
    requirements: pd.DataFrame
    career_overlap: pd.DataFrame
    exclusions: pd.DataFrame
    sources: pd.DataFrame
    metadata: dict[str, Any]

    def as_records(self) -> dict[str, Any]:
        tables = {
            "companies": self.companies,
            "jobs": self.jobs,
            "requirements": self.requirements,
            "career_overlap": self.career_overlap,
            "exclusions": self.exclusions,
            "sources": self.sources,
        }
        return {
            "tables": {
                name: {
                    "columns": list(frame.columns),
                    "rows": frame.astype(object).where(frame.notna(), None).to_dict("records"),
                }
                for name, frame in tables.items()
            },
            "metadata": self.metadata,
        }

    def write_csv(self, destination: Path) -> list[Path]:
        destination.mkdir(parents=True, exist_ok=True)
        outputs = []
        for name in ("companies", "jobs", "requirements", "career_overlap", "exclusions", "sources"):
            path = destination / f"{name}.csv"
            getattr(self, name).to_csv(path, index=False)
            outputs.append(path)
        return outputs


class _ListTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_li = False
        self._current: list[str] = []
        self.items: list[str] = []
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "li":
            self._in_li = True
            self._current = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "li" and self._in_li:
            value = " ".join(" ".join(self._current).split())
            if value:
                self.items.append(value)
            self._in_li = False
            self._current = []

    def handle_data(self, data: str) -> None:
        value = html.unescape(data).strip()
        if value:
            self.text.append(value)
            if self._in_li:
                self._current.append(value)


def _html_parts(value: Any) -> tuple[str, list[str]]:
    parser = _ListTextParser()
    parser.feed(html.unescape(str(value or "")))
    return " ".join(parser.text), parser.items


def _value(value: Any, key: str = "id") -> Any:
    return value.get(key) if isinstance(value, dict) else value


def _records(payload: Any, *keys: str) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    for key in keys:
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    data = payload.get("data")
    return _records(data, *keys) if isinstance(data, (dict, list)) else []


def _snapshot(payload: Any, fallback: str | None = None) -> str:
    if isinstance(payload, dict):
        return str(payload.get("collected_at") or fallback or datetime.now(UTC).isoformat())
    return fallback or datetime.now(UTC).isoformat()


def _active_at(closing_at: Any, snapshot_at: str, *, listed_as_live: bool) -> bool:
    if not closing_at:
        return listed_as_live
    closing = re.sub(r"[^0-9]", "", str(closing_at))[:8]
    snapshot = re.sub(r"[^0-9]", "", snapshot_at)[:8]
    return bool(len(closing) == 8 and len(snapshot) == 8 and closing >= snapshot)


def _country_from_location(location: str) -> tuple[str | None, str]:
    lowered = location.casefold()
    exact_hints = {
        "US": ("united states", "remote - us", "usa"),
        "KR": ("south korea", "republic of korea", "대한민국", "서울"),
        "CZ": ("czech republic", "czechia", "praha", "prague"),
    }
    matches = [code for code, hints in exact_hints.items() if any(hint in lowered for hint in hints)]
    return (matches[0], "location_text_hint") if len(matches) == 1 else (None, "country_unknown")


def _workplace(location: str, structured: Any = None) -> str:
    value = str(structured or "").casefold().replace("-", "")
    if value in {"remote", "hybrid", "onsite"}:
        return "on-site" if value == "onsite" else value
    lowered = location.casefold()
    if "hybrid" in lowered:
        return "hybrid"
    if "remote" in lowered:
        return "remote"
    return "unknown"


def _employment(value: Any) -> tuple[str, str | None]:
    raw = str(value).strip() if value not in (None, "") else None
    lowered = (raw or "").casefold().replace("-", " ")
    if "intern" in lowered:
        return "internship", raw
    if "part" in lowered and "time" in lowered:
        return "part-time", raw
    if "contract" in lowered or "short term" in lowered or "temporary" in lowered:
        return "contract", raw
    if "full" in lowered:
        return "full-time", raw
    return "unknown", raw


SKILLS = {
    "python", "sql", "kotlin", "swift", "java", "javascript", "typescript", "c++", "c#",
    "aws", "azure", "gcp", "excel", "tableau", "power bi", "docker", "kubernetes", "linux",
    "machine learning", "data engineering", "project management", "salesforce", "sap",
}
LANGUAGES = {"english", "korean", "czech", "german", "french", "spanish", "japanese", "mandarin"}


def _necessity(text: str, default: str = "unknown") -> str:
    lowered = text.casefold()
    if any(marker in lowered for marker in ("preferred", "nice to have", "bonus", "might have", "a plus")):
        return "preferred"
    if any(marker in lowered for marker in ("required", "must ", "you have", "minimum", "at least", "+ years", "years of")):
        return "required"
    return default


def _atomic_requirements(
    *, provider: str, job_id: str, company_name: str | None, texts: list[str],
    source_url: str | None, default_necessity: str = "unknown",
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for text in texts:
        clean = " ".join(str(text).split())
        if not clean:
            continue
        lowered = clean.casefold()
        necessity = _necessity(clean, default_necessity)
        atoms: list[tuple[str, str, str, str | None]] = []
        for skill in sorted(SKILLS):
            if re.search(r"(?<![\w+#])" + re.escape(skill) + r"(?![\w+#])", lowered):
                atoms.append(("skill", f"skill:{skill}", skill, None))
        for language in sorted(LANGUAGES):
            if re.search(r"\b" + re.escape(language) + r"\b", lowered):
                atoms.append(("language", f"language:{language}", language, None))
        years = re.search(r"(\d{1,2})\s*\+?\s*years?", lowered)
        if years:
            atoms.append(("experience", "experience:years", "years of experience", years.group(1)))
        if any(word in lowered for word in ("bachelor", "master's", "masters degree", "phd", "degree in")):
            atoms.append(("education", "education:degree", "degree", None))
        if any(word in lowered for word in ("certification", "certificate", "licensed", "licence")):
            atoms.append(("credential", "credential:specified-in-posting", clean[:120], None))
        if not atoms and necessity != "unknown":
            key = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")[:80]
            atoms.append(("other", f"posting:{key}", clean[:120], None))
        for kind, key, label, value in atoms:
            dedupe = (kind, key, necessity)
            if dedupe in seen:
                continue
            seen.add(dedupe)
            rows.append({
                "provider": provider, "job_id": job_id, "company_name": company_name,
                "requirement_id": f"{provider}:{job_id}:{len(rows) + 1}", "requirement_kind": kind,
                "normalized_key": key, "label": label, "necessity": necessity, "value": value,
                "proficiency": None, "evidence_scope": "current_job_posting", "source_url": source_url,
                "confidence": "explicit-text",
            })
    return rows


def normalize_greenhouse_jobs(payload: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    jobs, requirements = [], []
    snapshot_at = _snapshot(payload)
    records = _records(payload, "jobs")
    for record in records:
        job_id = str(record.get("job_id") or record.get("id") or "")
        company = record.get("company_name")
        location_obj = record.get("location")
        location = str(location_obj.get("name") if isinstance(location_obj, dict) else location_obj or "")
        country, note = _country_from_location(location)
        office_locations = [
            str(_value(office, "location") or "")
            for office in (record.get("offices") or [])
            if isinstance(office, dict)
        ]
        office_countries = {
            code for value in office_locations if (code := _country_from_location(value)[0])
        }
        if country is None and len(office_countries) == 1:
            country, note = office_countries.pop(), "office_location_hint"
        content_text, bullets = _html_parts(record.get("content") or record.get("description"))
        departments = record.get("departments") or []
        department_names = [str(_value(item, "name")) for item in departments]
        pay_ranges = record.get("pay_input_ranges") or []
        pay = pay_ranges[0] if len(pay_ranges) == 1 and isinstance(pay_ranges[0], dict) else {}
        salary_min = pay.get("min_cents") / 100 if isinstance(pay.get("min_cents"), (int, float)) else None
        salary_max = pay.get("max_cents") / 100 if isinstance(pay.get("max_cents"), (int, float)) else None
        source_url = record.get("absolute_url") or record.get("hosted_url")
        job = {
            "provider": "greenhouse", "job_id": job_id, "entity_id": record.get("entity_id"),
            "company_name": company, "company_type": record.get("company_type", "unknown"),
            "industry_raw": record.get("industry"), "title_raw": record.get("title"),
            "occupation_label": record.get("title"), "occupation_code": None, "occupation_system": "title-only",
            "country_code": record.get("country") or country, "location_raw": location, "city": None, "region": None,
            "workplace_type": _workplace(location, record.get("workplace_type")), "employment_type": "unknown",
            "employment_type_raw": None, "posting_language": record.get("language"), "salary_min": salary_min,
            "salary_max": salary_max, "salary_currency": pay.get("currency"), "salary_period": pay.get("interval"),
            "salary_period_raw": pay.get("interval"), "salary_basis": "unspecified", "posted_at": record.get("first_published"),
            "updated_at": record.get("updated_at"), "closing_at": record.get("application_deadline"),
            "snapshot_at": snapshot_at,
            "is_active": _active_at(record.get("application_deadline"), snapshot_at, listed_as_live=True),
            "source_url": source_url,
            "normalization_notes": ";".join(filter(None, (note, "department:" + ",".join(department_names) if department_names else None, "multiple_salary_tiers" if len(pay_ranges) > 1 else None))),
            "_title_text": str(record.get("title") or ""), "_description_text": content_text,
            "_location_text": " ".join((location, *office_locations)), "_department_text": " ".join(department_names),
        }
        jobs.append(job)
        requirements.extend(_atomic_requirements(provider="greenhouse", job_id=job_id, company_name=company, texts=bullets, source_url=source_url))
    return jobs, requirements, {"provider": "greenhouse", "snapshot_at": snapshot_at, "record_count": len(jobs), "source_url": "https://boards-api.greenhouse.io", "coverage": "title, location, language, department, description; salary only when structured", "limitations": "board-specific; location country may be text-derived; prose pay tiers are not collapsed"}


def normalize_lever_jobs(payload: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    jobs, requirements = [], []
    snapshot_at = _snapshot(payload)
    for record in _records(payload, "jobs"):
        job_id = str(record.get("job_id") or record.get("id") or "")
        categories = record.get("categories") if isinstance(record.get("categories"), dict) else {}
        location = str(record.get("location") or categories.get("location") or "")
        country = record.get("country")
        country_note = "provider_country" if country else _country_from_location(location)[1]
        if not country:
            country = _country_from_location(location)[0]
        commitment = record.get("commitment") or categories.get("commitment")
        employment, employment_raw = _employment(commitment)
        salary = record.get("salaryRange") or record.get("salary_range") or {}
        source_url = record.get("hostedUrl") or record.get("hosted_url")
        board_slug = None
        if source_url:
            path_parts = [part for part in urlparse(str(source_url)).path.split("/") if part]
            board_slug = path_parts[0] if path_parts else None
        company_name = record.get("company_name") or board_slug
        plain = record.get("descriptionPlain") or record.get("description") or ""
        list_rows = record.get("lists") or []
        requirement_texts: list[str] = []
        for item in list_rows:
            if not isinstance(item, dict):
                continue
            heading = str(item.get("text") or "").casefold()
            if not any(marker in heading for marker in ("who you", "require", "qualif", "skill", "preferred", "nice")):
                continue
            _, bullets = _html_parts(item.get("content"))
            requirement_texts.extend(bullets)
        job = {
            "provider": "lever", "job_id": job_id,
            "entity_id": record.get("entity_id") or (f"ATS:LEVER:{board_slug.upper()}" if board_slug else None),
            "company_name": company_name, "company_type": record.get("company_type", "unknown"),
            "industry_raw": record.get("industry"), "title_raw": record.get("title") or record.get("text"),
            "occupation_label": record.get("title") or record.get("text"), "occupation_code": None, "occupation_system": "title-only",
            "country_code": country, "location_raw": location, "city": None, "region": None,
            "workplace_type": _workplace(location, record.get("workplaceType") or record.get("workplace_type")),
            "employment_type": employment, "employment_type_raw": employment_raw,
            "posting_language": record.get("language"), "salary_min": salary.get("min"), "salary_max": salary.get("max"),
            "salary_currency": salary.get("currency"), "salary_period": salary.get("interval"),
            "salary_period_raw": salary.get("interval"), "salary_basis": "unspecified", "posted_at": record.get("createdAt") or record.get("created_at"),
            "updated_at": None, "closing_at": None, "snapshot_at": snapshot_at, "is_active": True,
            "source_url": source_url,
            "normalization_notes": ";".join(filter(None, (country_note, "company_from_board_slug" if not record.get("company_name") and board_slug else None))),
            "_title_text": str(record.get("text") or record.get("title") or ""), "_description_text": str(plain),
            "_location_text": location, "_department_text": " ".join((str(categories.get("team") or ""), str(categories.get("department") or ""))),
        }
        jobs.append(job)
        requirements.extend(_atomic_requirements(provider="lever", job_id=job_id, company_name=company_name, texts=requirement_texts, source_url=source_url, default_necessity="required"))
    return jobs, requirements, {"provider": "lever", "snapshot_at": snapshot_at, "record_count": len(jobs), "source_url": "https://api.lever.co/v0/postings", "coverage": "country, workplace, commitment, location, descriptions; salaryRange optional", "limitations": "site-specific; no global full-text search; posting language usually absent"}


def normalize_mpm_jobs(payload: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    snapshot_at = _snapshot(payload)
    jobs = []
    for record in _records(payload, "jobs", "postings"):
        job_id = str(record.get("posting_id") or record.get("idx") or "")
        jobs.append({
            "provider": "mpm_public_employment", "job_id": job_id, "entity_id": None,
            "company_name": record.get("institution_name") or record.get("insttname"), "company_type": "public-sector-employer",
            "industry_raw": None, "title_raw": record.get("title"), "occupation_label": record.get("title"),
            "occupation_code": None, "occupation_system": "title-only", "country_code": "KR", "location_raw": None,
            "city": None, "region": None, "workplace_type": "unknown", "employment_type": "unknown",
            "employment_type_raw": record.get("posting_type") or record.get("type02"), "posting_language": "ko",
            "salary_min": None, "salary_max": None, "salary_currency": None, "salary_period": None,
            "salary_period_raw": None, "salary_basis": None, "posted_at": record.get("registered_at") or record.get("regdate"),
            "updated_at": None, "closing_at": record.get("closing_at") or record.get("enddate"), "snapshot_at": snapshot_at,
            "is_active": _active_at(
                record.get("closing_at") or record.get("enddate"), snapshot_at, listed_as_live=False
            ),
            "source_url": record.get("source_url"),
            "normalization_notes": "list_metadata_only;requirements_unavailable;location_unavailable;salary_unavailable",
            "_title_text": str(record.get("title") or ""), "_description_text": "", "_location_text": "", "_department_text": "",
        })
    return jobs, [], {"provider": "mpm_public_employment", "snapshot_at": snapshot_at, "record_count": len(jobs), "source_url": "https://www.gojobs.go.kr", "coverage": "institution, title, posting type, registered/closing date", "limitations": "list metadata only; no verified location, salary, or qualification fields"}


def _mpsv_location(record: dict[str, Any]) -> tuple[str | None, str | None, str | None]:
    place = record.get("mistoVykonuPrace") if isinstance(record.get("mistoVykonuPrace"), dict) else {}
    raw = place.get("adresaText")
    municipality = _value(place.get("obec"))
    districts = place.get("okresy") or []
    district = ",".join(str(_value(item)) for item in districts) or None
    return str(raw or municipality or "") or None, str(municipality) if municipality else None, district


def _mpsv_salary_period(value: Any) -> tuple[str | None, str | None]:
    raw = str(_value(value) or "") or None
    lowered = (raw or "").casefold()
    if "hodin" in lowered or "hour" in lowered:
        return "hour", raw
    if "mesic" in lowered or "měsíc" in lowered or "month" in lowered:
        return "month", raw
    return None, raw


def normalize_mpsv_jobs(payload: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    snapshot_at = _snapshot(payload)
    jobs, requirements = [], []
    for record in _records(payload, "polozky"):
        job_id = str(record.get("portalId") or record.get("id") or record.get("referencniCislo") or "")
        employer = record.get("zamestnavatel") if isinstance(record.get("zamestnavatel"), dict) else {}
        company = employer.get("nazev")
        location, city, region = _mpsv_location(record)
        period, period_raw = _mpsv_salary_period(record.get("typMzdy"))
        title = _value(record.get("pozadovanaProfese"), "cs") or record.get("pozadovanaProfese")
        occupation = _value(record.get("profeseCzIsco"))
        employment_raw = ",".join(str(_value(item)) for item in (record.get("pracovnePravniVztahy") or [])) or None
        employment, employment_raw = _employment(employment_raw)
        source_url = record.get("urlAdresa")
        job = {
            "provider": "mpsv_cz", "job_id": job_id, "entity_id": f"ICO:{employer.get('ico')}" if employer.get("ico") else None,
            "company_name": company, "company_type": "public-sector-employer" if record.get("statniSpravaSamosprava") else "unknown",
            "industry_raw": None, "title_raw": title, "occupation_label": title, "occupation_code": occupation,
            "occupation_system": "CZ-ISCO", "country_code": "CZ", "location_raw": location, "city": city, "region": region,
            "workplace_type": "unknown", "employment_type": employment, "employment_type_raw": employment_raw,
            "posting_language": "cs", "salary_min": record.get("mesicniMzdaOd"), "salary_max": record.get("mesicniMzdaDo"),
            "salary_currency": "CZK", "salary_period": period, "salary_period_raw": period_raw,
            "salary_basis": "unspecified", "posted_at": record.get("datumVlozeni"), "updated_at": record.get("datumZmeny"),
            "closing_at": record.get("expirace"), "snapshot_at": snapshot_at,
            "is_active": _active_at(record.get("expirace"), snapshot_at, listed_as_live=True),
            "source_url": source_url,
            "normalization_notes": "official_open_data;salary_not_annualized;codebook_ids_preserved",
            "_title_text": str(title or ""), "_description_text": str(_value(record.get("upresnujiciInformace"), "cs") or ""),
            "_location_text": str(location or ""), "_department_text": "",
        }
        jobs.append(job)
        structured = [
            ("education", record.get("minPozadovaneVzdelani"), None),
            *(('education', item, None) for item in (record.get("pozadovaneVzdelani") or [])),
            *(('experience', item, None) for item in (record.get("pozadovanePovolani") or [])),
            *(('skill', item.get("dovednost"), item.get("popis")) for item in (record.get("pozadovanaDovednost") or []) if isinstance(item, dict)),
        ]
        for kind, item, label in structured:
            code = _value(item)
            if not code:
                continue
            requirements.append({
                "provider": "mpsv_cz", "job_id": job_id, "company_name": company,
                "requirement_id": f"mpsv_cz:{job_id}:{len(requirements) + 1}", "requirement_kind": kind,
                "normalized_key": f"mpsv:{kind}:{code}", "label": label or str(code), "necessity": "required",
                "value": str(code), "proficiency": None, "evidence_scope": "official_structured_job_field",
                "source_url": source_url, "confidence": "provider-structured",
            })
        for item in record.get("pozadovanaJazykovaZnalost") or []:
            if not isinstance(item, dict) or not _value(item.get("jazyk")):
                continue
            code = str(_value(item["jazyk"]))
            requirements.append({
                "provider": "mpsv_cz", "job_id": job_id, "company_name": company,
                "requirement_id": f"mpsv_cz:{job_id}:{len(requirements) + 1}", "requirement_kind": "language",
                "normalized_key": f"mpsv:language:{code}", "label": item.get("popis") or code,
                "necessity": "required", "value": code, "proficiency": _value(item.get("urovenZnalosti")),
                "evidence_scope": "official_structured_job_field", "source_url": source_url,
                "confidence": "provider-structured",
            })
    return jobs, requirements, {"provider": "mpsv_cz", "snapshot_at": snapshot_at, "record_count": len(jobs), "source_url": "https://data.mpsv.cz/od/soubory/volna-mista/", "coverage": "CZ-ISCO, CZK pay, education, language, skill, employer IČO, work location", "limitations": "codebook IDs require lookup; pay period must be resolved before salary comparison; contact PII is intentionally dropped"}


NORMALIZERS = {
    "greenhouse": normalize_greenhouse_jobs,
    "lever": normalize_lever_jobs,
    "mpm_public_employment": normalize_mpm_jobs,
    "mpsv_cz": normalize_mpsv_jobs,
}


def normalize_provider_payloads(payloads: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    jobs: list[dict[str, Any]] = []
    requirements: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    for provider, payload in payloads.items():
        if provider not in NORMALIZERS:
            raise ValueError(f"unsupported provider: {provider}")
        provider_jobs, provider_requirements, source = NORMALIZERS[provider](payload)
        jobs.extend(provider_jobs)
        requirements.extend(provider_requirements)
        sources.append(source)
    return jobs, requirements, sources


def _contains(value: Any, terms: tuple[str, ...]) -> bool:
    lowered = str(value or "").casefold()
    return any(term.casefold() in lowered for term in terms)


def _requirement_matches(rows: list[dict[str, Any]], term: str, *, required_only: bool) -> bool:
    for row in rows:
        if required_only and row.get("necessity") != "required":
            continue
        haystack = " ".join(str(row.get(key) or "") for key in ("normalized_key", "label", "value"))
        if term.casefold() in haystack.casefold():
            return True
    return False


def _requirement_verdict(rows: list[dict[str, Any]], term: str, *, required_only: bool) -> FilterVerdict:
    if not rows:
        return FilterVerdict.UNKNOWN
    return FilterVerdict.MATCH if _requirement_matches(rows, term, required_only=required_only) else FilterVerdict.NO_MATCH


def _record_verdict(reasons: list[tuple[str, str, Any]], field: str, verdict: FilterVerdict, observed: Any) -> None:
    if verdict == FilterVerdict.NO_MATCH:
        reasons.append((field, f"{field}_not_matched", observed))
    elif verdict == FilterVerdict.UNKNOWN:
        reasons.append((field, f"{field}_unverifiable", observed))
    elif verdict == FilterVerdict.CONFLICT:
        reasons.append((field, f"{field}_conflict", observed))


def _validate_profile(profile: JobSearchProfile) -> None:
    if not profile.countries:
        raise ValueError("countries must contain at least one ISO code")
    if not profile.job_keywords and not profile.occupations:
        raise ValueError("job_keywords or occupations must contain an explicit term")
    unknown = set(profile.country_allocation) - set(profile.countries)
    if unknown:
        raise ValueError("country_allocation contains out-of-scope countries")
    if profile.minimum_salary_floor is not None and (not profile.salary_currency or not profile.salary_period):
        raise ValueError("salary_currency and salary_period are required with a salary floor")
    if profile.unknown_policy not in {item.value for item in UnknownPolicy}:
        raise ValueError("unknown_policy must be exclude, report, or include")
    if profile.keyword_scope not in {"title_or_occupation", "title_or_description"}:
        raise ValueError("keyword_scope must be title_or_occupation or title_or_description")


def search_job_dataframes(payloads: dict[str, Any], profile: JobSearchProfile) -> JobDataFrames:
    _validate_profile(profile)
    jobs, requirements, sources = normalize_provider_payloads(payloads)
    requirements_by_job: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in requirements:
        requirements_by_job.setdefault((str(row["provider"]), str(row["job_id"])), []).append(row)

    matched: list[dict[str, Any]] = []
    exclusions: list[dict[str, Any]] = []
    for row in jobs:
        reasons: list[tuple[str, str, Any]] = []
        if row.get("country_code") not in profile.countries:
            reasons.append(("country", "country_not_matched_or_unknown", row.get("country_code")))
        keyword_text = " ".join((str(row.get("_title_text") or ""), str(row.get("occupation_label") or "")))
        if profile.keyword_scope == "title_or_description":
            keyword_text = " ".join((keyword_text, str(row.get("_description_text") or "")))
        _record_verdict(reasons, "job_keywords", text_verdict(keyword_text, profile.job_keywords), keyword_text or None)
        occupation_text = " ".join(str(row.get(key) or "") for key in ("occupation_label", "occupation_code"))
        if profile.occupations and not _contains(occupation_text, profile.occupations):
            reasons.append(("occupations", "occupation_not_matched", occupation_text))
        if profile.locations and not _contains(row.get("location_raw"), profile.locations):
            reasons.append(("locations", "location_not_matched_or_unknown", row.get("location_raw")))
        if profile.workplace_types and row.get("workplace_type") not in profile.workplace_types:
            reasons.append(("workplace_types", "workplace_type_not_matched_or_unknown", row.get("workplace_type")))
        if profile.employment_types and row.get("employment_type") not in profile.employment_types:
            reasons.append(("employment_types", "employment_type_not_matched_or_unknown", row.get("employment_type")))
        # Display language is not proof that an applicant must know that language.
        if profile.industries and not _contains(row.get("industry_raw"), profile.industries):
            reasons.append(("industries", "industry_not_matched_or_unknown", row.get("industry_raw")))
        if profile.company_types and row.get("company_type") not in profile.company_types:
            reasons.append(("company_types", "company_type_not_matched_or_unknown", row.get("company_type")))
        if profile.active_only and row.get("is_active") is not True:
            reasons.append(("is_active", "inactive_posting", row.get("is_active")))
        if profile.minimum_salary_floor is not None:
            if (row.get("salary_currency") != profile.salary_currency or row.get("salary_period") != profile.salary_period
                    or (profile.salary_basis is not None and row.get("salary_basis") != profile.salary_basis)):
                reasons.append(("salary", "salary_comparability_unverifiable", f"{row.get('salary_currency')}/{row.get('salary_period')}/{row.get('salary_basis')}"))
            elif row.get("salary_min") is None or float(row["salary_min"]) < profile.minimum_salary_floor:
                reasons.append(("salary_min", "salary_floor_not_met_or_unknown", row.get("salary_min")))
        if profile.maximum_salary_ceiling is not None and (row.get("salary_max") is None or float(row["salary_max"]) > profile.maximum_salary_ceiling):
            reasons.append(("salary_max", "salary_ceiling_not_met_or_unknown", row.get("salary_max")))
        job_requirements = requirements_by_job.get((str(row["provider"]), str(row["job_id"])), [])
        for term in profile.required_requirement_terms:
            _record_verdict(reasons, "required_requirements", _requirement_verdict(job_requirements, term, required_only=True), term)
        for language in profile.required_languages:
            language_rows = [item for item in job_requirements if item.get("requirement_kind") == "language"]
            _record_verdict(reasons, "required_languages", _requirement_verdict(language_rows, language, required_only=True), language)
        if reasons:
            exclusions.extend({"provider": row["provider"], "job_id": row["job_id"], "company_name": row.get("company_name"), "field": field, "reason": reason, "observed_value": value} for field, reason, value in reasons)
            only_unknown = all(reason.endswith(("_unverifiable", "_conflict")) for _, reason, _ in reasons)
            if not (only_unknown and profile.unknown_policy == UnknownPolicy.INCLUDE.value):
                continue
        preference_hits = sum(_requirement_matches(job_requirements, term, required_only=False) for term in profile.preferred_requirement_terms)
        matched.append({**row, "preference_hits": preference_hits})

    matched_keys = {(str(row["provider"]), str(row["job_id"])) for row in matched}
    matched_requirements = [row for row in requirements if (str(row["provider"]), str(row["job_id"])) in matched_keys]
    matched.sort(key=lambda row: (-int(row.get("preference_hits", 0)), str(row.get("country_code")), str(row.get("company_name")), str(row.get("job_id"))))
    job_output = [{key: row.get(key) for key in JOB_COLUMNS} | {"preference_hits": row.get("preference_hits", 0)} for row in matched]

    company_groups: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in matched:
        key = (str(row.get("entity_id") or ""), str(row.get("company_name") or ""), str(row.get("country_code") or ""))
        current = company_groups.setdefault(key, {"entity_id": row.get("entity_id"), "company_name": row.get("company_name"), "country_code": row.get("country_code"), "company_type": row.get("company_type"), "industry_raw": row.get("industry_raw"), "matched_job_count": 0})
        current["matched_job_count"] += 1

    overlap_groups: dict[tuple[str, str, str], dict[str, Any]] = {}
    for requirement in matched_requirements:
        if requirement.get("necessity") not in {"required", "preferred"}:
            continue
        key = (str(requirement["requirement_kind"]), str(requirement["normalized_key"]), str(requirement["label"]))
        group = overlap_groups.setdefault(key, {"requirement_kind": key[0], "normalized_key": key[1], "label": key[2], "required_count": 0, "preferred_count": 0, "jobs": set(), "companies": set(), "countries": set()})
        if requirement["necessity"] == "required":
            group["required_count"] += 1
        elif requirement["necessity"] == "preferred":
            group["preferred_count"] += 1
        group["jobs"].add((requirement["provider"], requirement["job_id"]))
        group["companies"].add(requirement.get("company_name"))
        job = next((item for item in matched if item["provider"] == requirement["provider"] and item["job_id"] == requirement["job_id"]), None)
        if job and job.get("country_code"):
            group["countries"].add(job["country_code"])
    overlap = []
    denominator = len(matched) or 1
    for group in overlap_groups.values():
        overlap.append({key: group[key] for key in ("requirement_kind", "normalized_key", "label", "required_count", "preferred_count")} | {"posting_count": len(group["jobs"]), "company_count": len(group["companies"]), "country_count": len(group["countries"]), "prevalence": len(group["jobs"]) / denominator})
    overlap.sort(key=lambda row: (-row["posting_count"], row["requirement_kind"], row["normalized_key"]))

    shortages = {country: max(profile.country_allocation.get(country, 0) - sum(row.get("country_code") == country for row in matched), 0) for country in profile.countries}
    limitations = [
        "A job posting is evidence of advertised demand, not a completed hire.",
        "Unknown fields are reported separately and do not satisfy a hard filter unless unknown_policy=include is explicit.",
        "Salary is compared only when currency, pay period, and requested salary basis match; no FX or annualization is inferred.",
        "Greenhouse and Lever are company-board scoped, not global job search APIs.",
        "MPM list results cannot satisfy location, salary, employment-type, or requirement filters.",
    ]
    return JobDataFrames(
        companies=pd.DataFrame(list(company_groups.values()), columns=("entity_id", "company_name", "country_code", "company_type", "industry_raw", "matched_job_count")),
        jobs=pd.DataFrame(job_output, columns=(*JOB_COLUMNS, "preference_hits")),
        requirements=pd.DataFrame(matched_requirements, columns=REQUIREMENT_COLUMNS),
        career_overlap=pd.DataFrame(overlap, columns=OVERLAP_COLUMNS),
        exclusions=pd.DataFrame(exclusions, columns=EXCLUSION_COLUMNS),
        sources=pd.DataFrame(sources, columns=SOURCE_COLUMNS),
        metadata={"matched_jobs": len(matched), "total_jobs": len(jobs), "country_shortages": shortages, "limitations": limitations},
    )
