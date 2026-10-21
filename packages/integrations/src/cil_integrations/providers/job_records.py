"""Canonical responsibility owner; migrated from src/company_intel/classification.py, src/company_intel/job_search.py."""

from __future__ import annotations
from cil_application.jobs.search import LANGUAGES
from cil_application.jobs.search import NORMALIZERS
from cil_application.jobs.search import SKILLS
from cil_contracts.jobs import CanonicalJobRecord
from cil_domain.clusters.signature import ClusterSignature
from cil_domain.jobs.filters import _active_at
from cil_domain.taxonomy.facts import resolve_title_to_isco
from cil_integrations.providers.job_schema import JobSchemaContract
from datetime import UTC, datetime
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urlparse
import html
import re


def _strict_bool(value: Any) -> bool | None:
    if type(value) is bool:
        return value
    if isinstance(value, str):
        if value.strip().lower() in {"true", "1", "yes", "y"}:
            return True
        if value.strip().lower() in {"false", "0", "no", "n"}:
            return False
    if type(value) is int and value in (0, 1):
        return value == 1
    return None


def from_kr_public_job(
    instt_se: str | None = None,
    pblanc_ty: str | None = None,
    work_type: str | None = None,
) -> ClusterSignature:
    """Map Korean Insa Public Job API attributes (Instt_se, Pblanc_ty) to ClusterSignature."""
    sector_map = {
        "g01": ("GOVERNMENT", "CENTRAL_GOV"),
        "g02": ("GOVERNMENT", "LOCAL_GOV"),
        "p01": ("STATE_OWNED", "MARKET_SOE"),
        "p02": ("PUBLIC_INSTITUTION", "QUASI_GOV"),
        "p03": ("PUBLIC_INSTITUTION", "OTHER_PUBLIC"),
        "p04": ("STATE_OWNED", "LOCAL_SOE"),
    }
    contract_map = {
        "e01": "REGULAR",
        "e02": "NON_REGULAR",
        "e03": "INTERN",
        "e04": "INDEFINITE",
    }
    sector, tier = sector_map.get(
        str(instt_se or "").lower(), ("PUBLIC_INSTITUTION", "ALL")
    )
    contract = contract_map.get(str(pblanc_ty or "").lower(), "ALL")
    workplace = (
        "REMOTE"
        if work_type == "remote"
        else "HYBRID"
        if work_type == "hybrid"
        else "UNKNOWN"
    )
    return ClusterSignature(
        region="KR", sector=sector, tier=tier, contract=contract, workplace=workplace
    )


def from_kr_worknet(
    coclcd: str | None = None, emptype: str | None = None, work_type: str | None = None
) -> ClusterSignature:
    """Map Korean WorkNet API attributes (coClcd, empType) to ClusterSignature."""
    sector_tier_map = {
        "01": ("UNKNOWN", "LARGE_CONGLOMERATE"),
        "02": ("UNKNOWN", "MID_SIZED"),
        "03": ("UNKNOWN", "SME"),
        "04": ("UNKNOWN", "VENTURE"),
        "05": ("STATE_OWNED", "PUBLIC_CORP"),
        "06": ("UNKNOWN", "FOREIGN_INVESTED"),
    }
    contract_map = {"10": "REGULAR", "20": "NON_REGULAR", "40": "DISPATCHED"}
    sector, tier = sector_tier_map.get(str(coclcd or ""), ("UNKNOWN", "ALL"))
    contract = contract_map.get(str(emptype or ""), "ALL")
    workplace = "REMOTE" if work_type == "remote" else "UNKNOWN"
    return ClusterSignature(
        region="KR", sector=sector, tier=tier, contract=contract, workplace=workplace
    )


def from_kr_opendart(
    corp_cls: str | None = None, induty_code: str | None = None
) -> ClusterSignature:
    """Map Korean OpenDART API attributes (corp_cls) to ClusterSignature."""
    tier_map = {"Y": "KOSPI", "K": "KOSDAQ", "N": "KONEX", "E": "EXTERNAL_AUDIT"}
    tier = tier_map.get(str(corp_cls or "").upper(), "ALL")
    return ClusterSignature(
        region="KR", sector="UNKNOWN", tier=tier, contract="ALL", workplace="ALL"
    )


def from_cz_ares(
    pravni_forma: str | None = None, cz_nace: str | None = None
) -> ClusterSignature:
    """Map Czech ARES Register attributes (pravniForma) to ClusterSignature."""
    form_map = {
        "101": ("UNKNOWN", "CZ_OSVC"),
        "112": ("UNKNOWN", "CZ_SRO"),
        "121": ("UNKNOWN", "CZ_AS"),
        "301": ("STATE_OWNED", "CZ_STATNI_PODNIK"),
        "331": ("PUBLIC_INSTITUTION", "CZ_PRISPEVKOVA_ORG"),
        "325": ("GOVERNMENT", "CZ_ORGANIZACNI_SLOZKA"),
        "701": ("UNKNOWN", "CZ_DRUZSTVO"),
        "421": ("UNKNOWN", "CZ_FOREIGN_BRANCH"),
    }
    sector, tier = form_map.get(str(pravni_forma or ""), ("UNKNOWN", "ALL"))
    return ClusterSignature(
        region="CZ", sector=sector, tier=tier, contract="ALL", workplace="ALL"
    )


def from_cz_mpsv(
    statni_sprava: bool | None = None, typ_mzdy: str | None = None
) -> ClusterSignature:
    """Map Czech MPSV Job Portal attributes (statniSpravaSamosprava) to ClusterSignature."""
    sector = "UNKNOWN"
    return ClusterSignature(
        region="CZ", sector=sector, tier="ALL", contract="UNKNOWN", workplace="UNKNOWN"
    )


def from_us_sec_or_usaspending(
    recipient_type: str | None = None, entity_type: str | None = None
) -> ClusterSignature:
    """Map US SEC / USAspending attributes to ClusterSignature."""
    if recipient_type == "for_profit_organization":
        return ClusterSignature(
            region="US",
            sector="UNKNOWN",
            tier="US_FOR_PROFIT",
            contract="ALL",
            workplace="ALL",
        )
    if recipient_type == "nonprofit_organization":
        return ClusterSignature(
            region="US",
            sector="UNKNOWN",
            tier="US_NONPROFIT",
            contract="ALL",
            workplace="ALL",
        )
    if recipient_type in ("state_government", "local_government"):
        return ClusterSignature(
            region="US",
            sector="GOVERNMENT",
            tier="US_LOCAL_GOV",
            contract="ALL",
            workplace="ALL",
        )
    if recipient_type == "higher_education":
        return ClusterSignature(
            region="US",
            sector="UNKNOWN",
            tier="US_HIGHER_ED",
            contract="ALL",
            workplace="ALL",
        )
    return ClusterSignature(
        region="US", sector="UNKNOWN", tier="ALL", contract="ALL", workplace="ALL"
    )


def from_cz_mpsv_job_record(
    raw: dict[str, Any], entity_meta: dict[str, Any] | None = None
) -> CanonicalJobRecord:
    """Normalize raw Czech MPSV vacancy record into CanonicalJobRecord with ClusterSignature."""
    clean = JobSchemaContract.validate_and_normalize(raw, provider="CZ_MPSV")
    meta = entity_meta or {}
    flag = raw.get("public_administration_flag", raw.get("statni_sprava"))
    statni_sprava = _strict_bool(flag)
    legal_form = meta.get("legal_form") or raw.get("legal_form") or ""
    # An administrative-context flag cannot establish employer ownership.
    sig = from_cz_mpsv(statni_sprava=statni_sprava)
    ownership = meta.get("ownership_sector") or raw.get("ownership_sector") or "UNKNOWN"
    tier = meta.get("entity_type") or "UNKNOWN"
    sig = ClusterSignature(
        region="CZ",
        sector=ownership,
        tier=tier,
        contract=str(raw.get("contract_classification") or "UNKNOWN"),
        workplace=str(raw.get("workplace_type") or "UNKNOWN"),
    )
    edu = (
        str(raw.get("minimum_education_code", ""))
        .replace("VzdelaniDetailniKategorie/", "")
        .strip()
    )
    isco = str(raw.get("cz_isco", "")).replace("CzIsco/", "").strip()
    weekly_hours = str(raw.get("weekly_hours") or "").strip()
    places = str(raw.get("vacancy_places") or "").strip()
    hours_hc = (
        f"{weekly_hours}h/주 ({places}명 모집)"
        if weekly_hours and places
        else f"{weekly_hours}h/주"
        if weekly_hours
        else f"{places}명 모집"
        if places
        else "-"
    )
    return CanonicalJobRecord(
        job_id=clean["job_id"],
        job_url=clean["job_url"],
        employer_name=clean["employer_name"],
        org_id=str(raw.get("employer_ico", "")).strip(),
        job_title=clean["job_title"],
        occupation_code=isco,
        education_level=edu or "unknown",
        contract_type=str(raw.get("employment_relationship_codes", "unknown")).replace(
            "PracovnepravniVztah/", ""
        ),
        salary_min=raw.get("salary_from_czk"),
        salary_max=raw.get("salary_to_czk"),
        currency=str(raw.get("salary_currency") or "CZK").strip(),
        location=str(
            raw.get("workplace_municipality_code")
            or raw.get("workplace_address")
            or "unknown"
        ),
        deadline=str(raw.get("expiry_date") or "").strip(),
        description=str(
            raw.get("job_description_cz") or raw.get("requirement_narrative") or ""
        ),
        source_api="MPSV_CZ_JOB_VACANCY_API",
        cluster_signature=sig,
        legal_form=legal_form or "unknown",
        entity_type=tier,
        hours_or_headcount=hours_hc,
        raw_attributes=raw,
        normalized_attributes=clean,
        salary_period=raw.get("salary_period"),
        requirement_text=raw.get("requirement_narrative")
        or raw.get("eligibility_summary"),
        preferred_text=raw.get("preferred_requirements"),
        source_kind=raw.get("source_kind", "unknown"),
    )


def from_kr_public_job_record(raw: dict[str, Any]) -> CanonicalJobRecord:
    """Normalize raw Korean JOB-ALIO vacancy record into CanonicalJobRecord with ClusterSignature."""
    clean = JobSchemaContract.validate_and_normalize(raw, provider="JOB_ALIO")
    instt_type = (
        str(raw.get("institution_type_filter") or raw.get("instt_se") or "")
        .strip()
        .lower()
    )
    emp_type = str(raw.get("employment_type") or raw.get("pblanc_ty") or "").strip()
    kr_inst_map = {
        "a2001": ("STATE_OWNED", "MARKET_SOE"),
        "a2002": ("STATE_OWNED", "QUASI_MARKET_SOE"),
        "a2003": ("PUBLIC_INSTITUTION", "FUND_QUASI_GOV"),
        "a2004": ("PUBLIC_INSTITUTION", "COMMISSIONED_QUASI_GOV"),
        "a2005": ("PUBLIC_INSTITUTION", "OTHER_PUBLIC"),
        "g01": ("GOVERNMENT", "CENTRAL_GOV"),
        "g02": ("GOVERNMENT", "LOCAL_GOV"),
        "p01": ("STATE_OWNED", "MARKET_SOE"),
        "p02": ("PUBLIC_INSTITUTION", "QUASI_GOV"),
        "p03": ("PUBLIC_INSTITUTION", "OTHER_PUBLIC"),
        "p04": ("STATE_OWNED", "LOCAL_SOE"),
    }
    sector, tier = kr_inst_map.get(instt_type, ("PUBLIC_INSTITUTION", "ALL"))
    kr_entity_type_names = {
        "a2001": "공기업(시장형)",
        "a2002": "공기업(준시장형)",
        "a2003": "준정부기관(기금관리형)",
        "a2004": "준정부기관(위탁집행형)",
        "a2005": "기타공공기관",
    }
    entity_name = kr_entity_type_names.get(instt_type, "공공기관")
    headcount = str(raw.get("headcount") or "").strip()
    career = str(raw.get("career") or "").strip()
    hours_hc = (
        f"{career} ({headcount}명)"
        if career and headcount
        else headcount or career or "-"
    )
    if emp_type in {"정규직", "일반정규직"} or emp_type.lower() == "e01":
        contract = "REGULAR"
    elif "무기계약" in emp_type or emp_type.lower() == "e04":
        contract = "INDEFINITE"
    elif "인턴" in emp_type or emp_type.lower() == "e03":
        contract = "INTERN"
    elif "비정규직" in emp_type or emp_type.lower() == "e02":
        contract = "NON_REGULAR"
    else:
        contract = "ALL"
    sig = ClusterSignature(
        region="KR",
        sector=sector,
        tier=tier,
        contract=contract,
        workplace=str(raw.get("workplace_type") or "UNKNOWN"),
    )
    return CanonicalJobRecord(
        job_id=clean["job_id"],
        job_url=clean["job_url"],
        employer_name=clean["employer_name"],
        org_id=str(
            raw.get("org_id")
            or raw.get("institution_type_filter")
            or raw.get("instt_code")
            or ""
        ).strip(),
        job_title=clean["job_title"],
        occupation_code=str(raw.get("ncs_job") or "").strip(),
        education_level=str(raw.get("education") or "unknown").strip(),
        contract_type=str(
            raw.get("employment_type") or raw.get("pblanc_ty") or "unknown"
        ).strip(),
        salary_min=raw.get("salary_min"),
        salary_max=raw.get("salary_max"),
        currency="KRW",
        location=str(
            raw.get("location")
            or raw.get("region")
            or raw.get("workRgnNm")
            or "unknown"
        ).strip(),
        deadline=str(
            raw.get("closeDate")
            or raw.get("closing_at")
            or raw.get("posting_period")
            or ""
        ).strip(),
        description=str(raw.get("eligibility_summary") or raw.get("description") or ""),
        source_api="JOB_ALIO_RECRUIT_API",
        cluster_signature=sig,
        legal_form=str(raw.get("legal_form") or "unknown"),
        entity_type=entity_name,
        hours_or_headcount=hours_hc,
        raw_attributes=raw,
        normalized_attributes=clean,
        salary_period=raw.get("salary_period"),
        requirement_text=raw.get("requirement_narrative")
        or raw.get("eligibility_summary"),
        preferred_text=raw.get("preferred_requirements"),
        source_kind=raw.get("source_kind", "unknown"),
    )


def from_sk_upsvar_record(raw: dict[str, Any]) -> CanonicalJobRecord:
    """Normalize raw Slovak ÚPSVaR vacancy record into CanonicalJobRecord with ClusterSignature."""
    clean = JobSchemaContract.validate_and_normalize(raw, provider="SK_UPSVAR")
    sig = ClusterSignature(
        region="SK",
        sector="STATE_OWNED"
        if "Štátny" in str(raw.get("legal_form", ""))
        else "UNKNOWN",
        tier=str(raw.get("entity_type", "PUBLIC")),
        contract="REGULAR",
        workplace=str(raw.get("workplace_type") or "UNKNOWN"),
    )
    return CanonicalJobRecord(
        job_id=clean["job_id"],
        job_url=clean["job_url"],
        employer_name=clean["employer_name"],
        org_id=str(raw.get("ico", "")).strip(),
        job_title=clean["job_title"],
        occupation_code=str(raw.get("isco", "")).strip(),
        education_level=str(raw.get("edu", "unknown")).strip(),
        contract_type="REGULAR",
        salary_min=raw.get("sal_min"),
        salary_max=raw.get("sal_max"),
        currency=str(raw.get("curr", "EUR")).strip(),
        location=str(raw.get("loc", "unknown")).strip(),
        deadline=str(raw.get("closing_at", "")).strip(),
        description=str(raw.get("desc", "")),
        source_api="UPSVAR_SK_JOB_API",
        cluster_signature=sig,
        legal_form=str(raw.get("legal_form", "unknown")),
        entity_type=str(raw.get("entity_type", "unknown")),
        hours_or_headcount=str(raw.get("hours_or_headcount") or "unknown"),
        raw_attributes=raw,
        normalized_attributes=clean,
        salary_period=raw.get("salary_period"),
        requirement_text=raw.get("requirement_narrative")
        or raw.get("eligibility_summary"),
        preferred_text=raw.get("preferred_requirements"),
        source_kind=raw.get("source_kind", "unknown"),
    )


def from_us_usajobs_record(raw: dict[str, Any]) -> CanonicalJobRecord:
    """Normalize raw US USAJOBS vacancy record into CanonicalJobRecord with ClusterSignature."""
    clean = JobSchemaContract.validate_and_normalize(raw, provider="US_USAJOBS")
    sig = ClusterSignature(
        region="US",
        sector="GOVERNMENT",
        tier="FEDERAL_SCOPE",
        contract="REGULAR"
        if "Permanent" in str(raw.get("PositionOfferingType", ""))
        else "ALL",
        workplace="REMOTE"
        if raw.get("UserArea", {}).get("Details", {}).get("TeleworkEligible")
        else "UNKNOWN",
    )
    remun = raw.get("PositionRemuneration", [{}])
    min_sal = (
        remun[0].get("MinimumRange") if isinstance(remun, list) and remun else None
    )
    max_sal = (
        remun[0].get("MaximumRange") if isinstance(remun, list) and remun else None
    )
    return CanonicalJobRecord(
        job_id=clean["job_id"],
        job_url=clean["job_url"],
        employer_name=clean["employer_name"],
        org_id=str(raw.get("DepartmentName", "")).strip(),
        job_title=clean["job_title"],
        occupation_code=str(raw.get("JobCode", "")).strip(),
        education_level=str(raw.get("EducationRequirement", "unknown")).strip(),
        contract_type=str(raw.get("PositionOfferingType", "unknown")).strip(),
        salary_min=min_sal,
        salary_max=max_sal,
        currency=str(
            raw.get("CurrencyCode")
            or (
                remun[0].get("CurrencyCode")
                if isinstance(remun, list) and remun
                else None
            )
            or "unknown"
        ),
        location=str(raw.get("PositionLocationDisplay", "unknown")).strip(),
        deadline=str(raw.get("ApplicationCloseDate", "")).strip(),
        description=str(
            raw.get("UserArea", {}).get("Details", {}).get("JobSummary", "")
        ),
        source_api="USAJOBS_SEARCH_API",
        cluster_signature=sig,
        legal_form="Federal Executive Branch",
        entity_type="연방정부 공공기구",
        hours_or_headcount=str(raw.get("PositionOfferingType", "Permanent Full-Time")),
        raw_attributes=raw,
        normalized_attributes=clean,
        salary_period=raw.get("salary_period"),
        requirement_text=raw.get("requirement_narrative")
        or raw.get("eligibility_summary"),
        preferred_text=raw.get("preferred_requirements"),
        source_kind=raw.get("source_kind", "unknown"),
    )


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
    return (" ".join(parser.text), parser.items)


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
        return str(
            payload.get("collected_at") or fallback or datetime.now(UTC).isoformat()
        )
    return fallback or datetime.now(UTC).isoformat()


def _country_from_location(location: str) -> tuple[str | None, str]:
    lowered = location.casefold()
    exact_hints = {
        "US": ("united states", "remote - us", "usa"),
        "KR": ("south korea", "republic of korea", "대한민국", "서울"),
        "CZ": ("czech republic", "czechia", "praha", "prague"),
    }
    matches = [
        code
        for code, hints in exact_hints.items()
        if any((hint in lowered for hint in hints))
    ]
    return (
        (matches[0], "location_text_hint")
        if len(matches) == 1
        else (None, "country_unknown")
    )


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
        return ("internship", raw)
    if "part" in lowered and "time" in lowered:
        return ("part-time", raw)
    if "contract" in lowered or "short term" in lowered or "temporary" in lowered:
        return ("contract", raw)
    if "full" in lowered:
        return ("full-time", raw)
    return ("unknown", raw)


def _necessity(text: str, default: str = "unknown") -> str:
    lowered = text.casefold()
    if any(
        (
            marker in lowered
            for marker in ("preferred", "nice to have", "bonus", "might have", "a plus")
        )
    ):
        return "preferred"
    if any(
        (
            marker in lowered
            for marker in (
                "required",
                "must ",
                "you have",
                "minimum",
                "at least",
                "+ years",
                "years of",
            )
        )
    ):
        return "required"
    return default


def _atomic_requirements(
    *,
    provider: str,
    job_id: str,
    company_name: str | None,
    texts: list[str],
    source_url: str | None,
    default_necessity: str = "unknown",
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
            if re.search("(?<![\\w+#])" + re.escape(skill) + "(?![\\w+#])", lowered):
                atoms.append(("skill", f"skill:{skill}", skill, None))
        for language in sorted(LANGUAGES):
            if re.search("\\b" + re.escape(language) + "\\b", lowered):
                atoms.append(("language", f"language:{language}", language, None))
        years = re.search("(\\d{1,2})\\s*\\+?\\s*years?", lowered)
        if years:
            atoms.append(
                (
                    "experience",
                    "experience:years",
                    "years of experience",
                    years.group(1),
                )
            )
        if any(
            (
                word in lowered
                for word in (
                    "bachelor",
                    "master's",
                    "masters degree",
                    "phd",
                    "degree in",
                )
            )
        ):
            atoms.append(("education", "education:degree", "degree", None))
        if any(
            (
                word in lowered
                for word in ("certification", "certificate", "licensed", "licence")
            )
        ):
            atoms.append(
                ("credential", "credential:specified-in-posting", clean[:120], None)
            )
        if not atoms and necessity != "unknown":
            key = re.sub("[^a-z0-9]+", "-", lowered).strip("-")[:80]
            atoms.append(("other", f"posting:{key}", clean[:120], None))
        for kind, key, label, value in atoms:
            dedupe = (kind, key, necessity)
            if dedupe in seen:
                continue
            seen.add(dedupe)
            rows.append(
                {
                    "provider": provider,
                    "job_id": job_id,
                    "company_name": company_name,
                    "requirement_id": f"{provider}:{job_id}:{len(rows) + 1}",
                    "requirement_kind": kind,
                    "normalized_key": key,
                    "label": label,
                    "necessity": necessity,
                    "value": value,
                    "proficiency": None,
                    "evidence_scope": "current_job_posting",
                    "source_url": source_url,
                    "confidence": "explicit-text",
                }
            )
    return rows


def normalize_greenhouse_jobs(
    payload: Any,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    jobs, requirements = ([], [])
    snapshot_at = _snapshot(payload)
    records = _records(payload, "jobs")
    for record in records:
        job_id = str(record.get("job_id") or record.get("id") or "")
        company = record.get("company_name")
        location_obj = record.get("location")
        location = str(
            location_obj.get("name")
            if isinstance(location_obj, dict)
            else location_obj or ""
        )
        country, note = _country_from_location(location)
        office_locations = [
            str(_value(office, "location") or _value(office, "name") or "")
            for office in record.get("offices") or []
            if isinstance(office, dict)
        ]
        office_countries = {
            code
            for value in office_locations
            if (code := _country_from_location(value)[0])
        }
        if country is None and len(office_countries) == 1:
            country, note = (office_countries.pop(), "office_location_hint")
        content_text, bullets = _html_parts(
            record.get("content") or record.get("description")
        )
        departments = record.get("departments") or []
        department_names = [str(_value(item, "name")) for item in departments]
        pay_ranges = record.get("pay_input_ranges") or []
        pay = (
            pay_ranges[0]
            if len(pay_ranges) == 1 and isinstance(pay_ranges[0], dict)
            else {}
        )
        salary_min = (
            pay.get("min_cents") / 100
            if isinstance(pay.get("min_cents"), (int, float))
            else None
        )
        salary_max = (
            pay.get("max_cents") / 100
            if isinstance(pay.get("max_cents"), (int, float))
            else None
        )
        source_url = record.get("absolute_url") or record.get("hosted_url")
        job = {
            "provider": "greenhouse",
            "job_id": job_id,
            "entity_id": record.get("entity_id"),
            "company_name": company,
            "company_type": record.get("company_type", "unknown"),
            "industry_raw": record.get("industry"),
            "business_unit": "; ".join(department_names) or None,
            "institution_type_code": None,
            "institution_type_raw": None,
            "identity_link_status": "unresolved",
            "public_context": None,
            "public_institution_type": None,
            "legal_form": None,
            "ownership_sector": None,
            "title_raw": record.get("title"),
            "occupation_label": record.get("title"),
            "occupation_code": None,
            "occupation_system": "title-only",
            "occupation_pivot": resolve_title_to_isco(record.get("title")),
            "ncs_code": None,
            "country_code": record.get("country") or country,
            "location_raw": location,
            "city": None,
            "region": None,
            "workplace_type": _workplace(location, record.get("workplace_type")),
            "employment_type": "unknown",
            "employment_type_raw": None,
            "posting_language": record.get("language"),
            "salary_min": salary_min,
            "salary_max": salary_max,
            "salary_currency": pay.get("currency"),
            "salary_period": pay.get("interval"),
            "salary_period_raw": pay.get("interval"),
            "salary_basis": "unspecified",
            "posted_at": record.get("first_published"),
            "updated_at": record.get("updated_at"),
            "closing_at": record.get("application_deadline"),
            "snapshot_at": snapshot_at,
            "is_active": _active_at(
                record.get("application_deadline"), snapshot_at, listed_as_live=True
            ),
            "source_url": source_url,
            "normalization_notes": ";".join(
                filter(
                    None,
                    (
                        note,
                        "department:" + ",".join(department_names)
                        if department_names
                        else None,
                        "multiple_salary_tiers" if len(pay_ranges) > 1 else None,
                    ),
                )
            ),
            "_title_text": str(record.get("title") or ""),
            "_description_text": content_text,
            "_location_text": " ".join((location, *office_locations)),
            "_location_candidates": [location, *office_locations],
            "_department_text": " ".join(department_names),
        }
        jobs.append(job)
        requirements.extend(
            _atomic_requirements(
                provider="greenhouse",
                job_id=job_id,
                company_name=company,
                texts=bullets,
                source_url=source_url,
            )
        )
    return (
        jobs,
        requirements,
        {
            "provider": "greenhouse",
            "snapshot_at": snapshot_at,
            "record_count": len(jobs),
            "source_url": "https://boards-api.greenhouse.io",
            "coverage": "title, location, language, department, description; salary only when structured",
            "limitations": "board-specific; location country may be text-derived; prose pay tiers are not collapsed",
        },
    )


def normalize_lever_jobs(
    payload: Any,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    jobs, requirements = ([], [])
    snapshot_at = _snapshot(payload)
    for record in _records(payload, "jobs"):
        job_id = str(record.get("job_id") or record.get("id") or "")
        categories = (
            record.get("categories")
            if isinstance(record.get("categories"), dict)
            else {}
        )
        location = str(record.get("location") or categories.get("location") or "")
        all_locations = (
            record.get("allLocations")
            or record.get("all_locations")
            or categories.get("allLocations")
            or categories.get("all_locations")
            or []
        )
        if isinstance(all_locations, str):
            all_locations = [all_locations]
        location_candidates = [location, *(str(item) for item in all_locations if item)]
        country = record.get("country")
        country_note = (
            "provider_country" if country else _country_from_location(location)[1]
        )
        if not country:
            candidate_countries = {
                code
                for item in location_candidates
                if (code := _country_from_location(item)[0])
            }
            country = (
                candidate_countries.pop()
                if len(candidate_countries) == 1
                else _country_from_location(location)[0]
            )
        commitment = record.get("commitment") or categories.get("commitment")
        employment, employment_raw = _employment(commitment)
        salary = record.get("salaryRange") or record.get("salary_range") or {}
        source_url = record.get("hostedUrl") or record.get("hosted_url")
        board_slug = None
        if source_url:
            path_parts = [
                part for part in urlparse(str(source_url)).path.split("/") if part
            ]
            board_slug = path_parts[0] if path_parts else None
        company_name = record.get("company_name") or board_slug
        plain = record.get("descriptionPlain") or record.get("description") or ""
        list_rows = record.get("lists") or []
        requirement_texts: list[str] = []
        for item in list_rows:
            if not isinstance(item, dict):
                continue
            heading = str(item.get("text") or "").casefold()
            if not any(
                (
                    marker in heading
                    for marker in (
                        "who you",
                        "require",
                        "qualif",
                        "skill",
                        "preferred",
                        "nice",
                    )
                )
            ):
                continue
            _, bullets = _html_parts(item.get("content"))
            requirement_texts.extend(bullets)
        job = {
            "provider": "lever",
            "job_id": job_id,
            "entity_id": record.get("entity_id")
            or (f"ATS:LEVER:{board_slug.upper()}" if board_slug else None),
            "company_name": company_name,
            "company_type": record.get("company_type", "unknown"),
            "industry_raw": record.get("industry"),
            "business_unit": " / ".join(
                filter(
                    None,
                    (
                        str(categories.get("team") or ""),
                        str(categories.get("department") or ""),
                    ),
                )
            )
            or None,
            "institution_type_code": None,
            "institution_type_raw": None,
            "identity_link_status": "unresolved",
            "public_context": None,
            "public_institution_type": None,
            "legal_form": None,
            "ownership_sector": None,
            "title_raw": record.get("title") or record.get("text"),
            "occupation_label": record.get("title") or record.get("text"),
            "occupation_code": None,
            "occupation_system": "title-only",
            "occupation_pivot": resolve_title_to_isco(
                record.get("title") or record.get("text")
            ),
            "ncs_code": None,
            "country_code": country,
            "location_raw": location,
            "city": None,
            "region": None,
            "workplace_type": _workplace(
                location, record.get("workplaceType") or record.get("workplace_type")
            ),
            "employment_type": employment,
            "employment_type_raw": employment_raw,
            "posting_language": record.get("language"),
            "salary_min": salary.get("min"),
            "salary_max": salary.get("max"),
            "salary_currency": salary.get("currency"),
            "salary_period": salary.get("interval"),
            "salary_period_raw": salary.get("interval"),
            "salary_basis": "unspecified",
            "posted_at": record.get("createdAt") or record.get("created_at"),
            "updated_at": None,
            "closing_at": None,
            "snapshot_at": snapshot_at,
            "is_active": True,
            "source_url": source_url,
            "normalization_notes": ";".join(
                filter(
                    None,
                    (
                        country_note,
                        "company_from_board_slug"
                        if not record.get("company_name") and board_slug
                        else None,
                    ),
                )
            ),
            "_title_text": str(record.get("text") or record.get("title") or ""),
            "_description_text": str(plain),
            "_location_text": " ".join(location_candidates),
            "_location_candidates": location_candidates,
            "_department_text": " ".join(
                (
                    str(categories.get("team") or ""),
                    str(categories.get("department") or ""),
                )
            ),
        }
        jobs.append(job)
        requirements.extend(
            _atomic_requirements(
                provider="lever",
                job_id=job_id,
                company_name=company_name,
                texts=requirement_texts,
                source_url=source_url,
                default_necessity="unspecified",
            )
        )
    return (
        jobs,
        requirements,
        {
            "provider": "lever",
            "snapshot_at": snapshot_at,
            "record_count": len(jobs),
            "source_url": "https://api.lever.co/v0/postings",
            "coverage": "country, workplace, commitment, location, descriptions; salaryRange optional",
            "limitations": "site-specific; no global full-text search; posting language usually absent",
        },
    )


def normalize_mpm_jobs(
    payload: Any,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    snapshot_at = _snapshot(payload)
    jobs = []
    for record in _records(payload, "jobs", "postings"):
        job_id = str(record.get("posting_id") or record.get("idx") or "")
        posting_type_raw = (
            str(record.get("posting_type") or record.get("type02") or "").strip()
            or None
        )
        emp_type = "unknown"
        if posting_type_raw:
            lowered_pt = posting_type_raw.casefold()
            if "정규" in lowered_pt:
                emp_type = "permanent"
            elif "계약" in lowered_pt or "기간제" in lowered_pt:
                emp_type = "contract"
            elif "인턴" in lowered_pt:
                emp_type = "internship"
        title_str = str(record.get("title") or "")
        isco_pivot = resolve_title_to_isco(title_str)
        jobs.append(
            {
                "provider": "mpm_public_employment",
                "job_id": job_id,
                "entity_id": None,
                "company_name": record.get("institution_name")
                or record.get("insttname"),
                "company_type": "public-sector-employer",
                "industry_raw": None,
                "business_unit": None,
                "institution_type_code": record.get("institution_type")
                or record.get("type01"),
                "institution_type_raw": record.get("institution_type_name")
                or record.get("type01_name")
                or record.get("type01"),
                "identity_link_status": "unresolved",
                "public_context": "public_employment_listing",
                "public_institution_type": None,
                "legal_form": None,
                "ownership_sector": None,
                "title_raw": record.get("title"),
                "occupation_label": record.get("title"),
                "occupation_code": None,
                "occupation_system": "title-only",
                "occupation_pivot": isco_pivot,
                "ncs_code": None,
                "country_code": "KR",
                "location_raw": None,
                "city": None,
                "region": None,
                "workplace_type": "unknown",
                "employment_type": emp_type,
                "employment_type_raw": posting_type_raw,
                "posting_language": "ko",
                "salary_min": None,
                "salary_max": None,
                "salary_currency": None,
                "salary_period": None,
                "salary_period_raw": None,
                "salary_basis": None,
                "posted_at": record.get("registered_at") or record.get("regdate"),
                "updated_at": None,
                "closing_at": record.get("closing_at") or record.get("enddate"),
                "snapshot_at": snapshot_at,
                "is_active": _active_at(
                    record.get("closing_at") or record.get("enddate"),
                    snapshot_at,
                    listed_as_live=False,
                ),
                "source_url": record.get("source_url"),
                "normalization_notes": "list_metadata_only;requirements_unavailable;location_unavailable;salary_unavailable",
                "_title_text": str(record.get("title") or ""),
                "_description_text": "",
                "_location_text": "",
                "_location_candidates": [],
                "_department_text": "",
            }
        )
    return (
        jobs,
        [],
        {
            "provider": "mpm_public_employment",
            "snapshot_at": snapshot_at,
            "record_count": len(jobs),
            "source_url": "https://www.gojobs.go.kr",
            "coverage": "institution, title, posting type, registered/closing date",
            "limitations": "list metadata only; no verified location, salary, or qualification fields",
        },
    )


def _mpsv_location(record: dict[str, Any]) -> tuple[str | None, str | None, str | None]:
    place = (
        record.get("mistoVykonuPrace")
        if isinstance(record.get("mistoVykonuPrace"), dict)
        else {}
    )
    raw = place.get("adresaText")
    municipality = _value(place.get("obec"))
    districts = place.get("okresy") or []
    district = ",".join((str(_value(item)) for item in districts)) or None
    return (
        str(raw or municipality or "") or None,
        str(municipality) if municipality else None,
        district,
    )


def _mpsv_salary_period(value: Any) -> tuple[str | None, str | None]:
    raw = str(_value(value) or "") or None
    lowered = (raw or "").casefold()
    if (
        "hodin" in lowered
        or "hour" in lowered
        or lowered == "hod"
        or ("hod." in lowered)
        or ("/hod" in lowered)
    ):
        return ("hour", raw)
    if (
        "mesic" in lowered
        or "měsíc" in lowered
        or "month" in lowered
        or (lowered == "měs")
        or ("mes" in lowered)
    ):
        return ("month", raw)
    return (None, raw)


def normalize_mpsv_jobs(
    payload: Any,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    snapshot_at = _snapshot(payload)
    jobs, requirements = ([], [])
    for record in _records(payload, "polozky"):
        job_id = str(
            record.get("portalId")
            or record.get("id")
            or record.get("referencniCislo")
            or ""
        )
        employer = (
            record.get("zamestnavatel")
            if isinstance(record.get("zamestnavatel"), dict)
            else {}
        )
        company = employer.get("nazev")
        location, city, region = _mpsv_location(record)
        period, period_raw = _mpsv_salary_period(record.get("typMzdy"))
        title = _value(record.get("pozadovanaProfese"), "cs") or record.get(
            "pozadovanaProfese"
        )
        cz_isco = str(_value(record.get("profeseCzIsco")) or "").strip() or None
        isco_pivot = cz_isco[:4] if cz_isco and len(cz_isco) >= 4 else None
        employment_raw = (
            ",".join(
                (str(_value(item)) for item in record.get("pracovnePravniVztahy") or [])
            )
            or None
        )
        employment, employment_raw = _employment(employment_raw)
        source_url = record.get("urlAdresa")
        job = {
            "provider": "mpsv_cz",
            "job_id": job_id,
            "entity_id": f"ICO:{employer.get('ico')}" if employer.get("ico") else None,
            "company_name": company,
            "company_type": "public-sector-employer"
            if _strict_bool(record.get("statniSpravaSamosprava")) is True
            else "unknown",
            "industry_raw": None,
            "business_unit": None,
            "institution_type_code": None,
            "institution_type_raw": None,
            "identity_link_status": "unresolved",
            "public_context": "public_administration"
            if _strict_bool(record.get("statniSpravaSamosprava")) is True
            else None,
            "public_institution_type": None,
            "legal_form": None,
            "ownership_sector": None,
            "title_raw": title,
            "occupation_label": title,
            "occupation_code": cz_isco,
            "occupation_system": "CZ-ISCO",
            "occupation_pivot": isco_pivot,
            "ncs_code": None,
            "country_code": "CZ",
            "location_raw": location,
            "city": city,
            "region": region,
            "workplace_type": "unknown",
            "employment_type": employment,
            "employment_type_raw": employment_raw,
            "posting_language": "cs",
            "salary_min": record.get("mesicniMzdaOd"),
            "salary_max": record.get("mesicniMzdaDo"),
            "salary_currency": "CZK",
            "salary_period": period,
            "salary_period_raw": period_raw,
            "salary_basis": "unspecified",
            "posted_at": record.get("datumVlozeni"),
            "updated_at": record.get("datumZmeny"),
            "closing_at": record.get("expirace"),
            "snapshot_at": snapshot_at,
            "is_active": _active_at(
                record.get("expirace"), snapshot_at, listed_as_live=True
            ),
            "source_url": source_url,
            "normalization_notes": "official_open_data;salary_not_annualized;codebook_ids_preserved",
            "_title_text": str(title or ""),
            "_description_text": str(
                _value(record.get("upresnujiciInformace"), "cs") or ""
            ),
            "_location_text": str(location or ""),
            "_location_candidates": [str(location)] if location else [],
            "_department_text": "",
        }
        jobs.append(job)
        structured = [
            ("education", record.get("minPozadovaneVzdelani"), None),
            *(
                ("education", item, None)
                for item in record.get("pozadovaneVzdelani") or []
            ),
            *(
                ("experience", item, None)
                for item in record.get("pozadovanePovolani") or []
            ),
            *(
                ("skill", item.get("dovednost"), item.get("popis"))
                for item in record.get("pozadovanaDovednost") or []
                if isinstance(item, dict)
            ),
        ]
        for kind, item, label in structured:
            code = _value(item)
            if not code:
                continue
            requirements.append(
                {
                    "provider": "mpsv_cz",
                    "job_id": job_id,
                    "company_name": company,
                    "requirement_id": f"mpsv_cz:{job_id}:{len(requirements) + 1}",
                    "requirement_kind": kind,
                    "normalized_key": f"mpsv:{kind}:{code}",
                    "label": label or str(code),
                    "necessity": "required",
                    "value": str(code),
                    "proficiency": None,
                    "evidence_scope": "official_structured_job_field",
                    "source_url": source_url,
                    "confidence": "provider-structured",
                }
            )
        for item in record.get("pozadovanaJazykovaZnalost") or []:
            if not isinstance(item, dict) or not _value(item.get("jazyk")):
                continue
            code = str(_value(item["jazyk"]))
            requirements.append(
                {
                    "provider": "mpsv_cz",
                    "job_id": job_id,
                    "company_name": company,
                    "requirement_id": f"mpsv_cz:{job_id}:{len(requirements) + 1}",
                    "requirement_kind": "language",
                    "normalized_key": f"mpsv:language:{code}",
                    "label": item.get("popis") or code,
                    "necessity": "required",
                    "value": code,
                    "proficiency": _value(item.get("urovenZnalosti")),
                    "evidence_scope": "official_structured_job_field",
                    "source_url": source_url,
                    "confidence": "provider-structured",
                }
            )
    return (
        jobs,
        requirements,
        {
            "provider": "mpsv_cz",
            "snapshot_at": snapshot_at,
            "record_count": len(jobs),
            "source_url": "https://data.mpsv.cz/od/soubory/volna-mista/",
            "coverage": "CZ-ISCO, CZK pay, education, language, skill, employer IČO, work location",
            "limitations": "codebook IDs require lookup; pay period must be resolved before salary comparison; contact PII is intentionally dropped",
        },
    )


def normalize_provider_payloads(
    payloads: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
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
    return (jobs, requirements, sources)
