from __future__ import annotations

from collections.abc import Iterable

from .models import AnalysisEligibility, CompanyClassification, TaxonomyFact

CAPABILITY_AXES = ("financial", "job_posting", "employment", "market", "macro", "public_context")
TAXONOMY_AXES = (
    "ownership_sector",
    "public_institution_type",
    "legal_form",
    "industry",
    "market_status",
    "posting_organization_unit",
)


def evaluate_analysis_eligibility(*, identity_resolved: bool, period_aligned: bool, unit_aligned: bool, available_at_present: bool) -> AnalysisEligibility:
    reasons: list[str] = []
    if not identity_resolved:
        reasons.append("identity_unresolved")
    if not period_aligned:
        reasons.append("missing-period-alignment")
    if not unit_aligned:
        reasons.append("missing-unit-alignment")
    if not available_at_present:
        reasons.append("missing-available-at")
    if not reasons:
        return AnalysisEligibility(True, False, ("causal-evidence-not-established",))
    return AnalysisEligibility(False, False, tuple(reasons))


def classify_taxonomy_axes(facts: Iterable[TaxonomyFact]) -> dict[str, tuple[TaxonomyFact, ...]]:
    """Group taxonomy facts without converting provider-native codes.

    The returned values are facts rather than a single string because a legal
    form, industry code, or public-institution type can be multi-valued.  In
    particular, this function intentionally does *not* infer an ownership
    sector from a legal-form code or a current market status from a listing
    venue.  Callers that need a cross-provider comparison must first select a
    common namespace and document their mapping.
    """

    grouped: dict[str, list[TaxonomyFact]] = {axis: [] for axis in TAXONOMY_AXES}
    for fact in facts:
        grouped.setdefault(fact.semantic_field, []).append(fact)
    return {
        axis: tuple(
            sorted(
                entries,
                key=lambda item: (item.namespace, item.value, item.raw_field),
            )
        )
        for axis, entries in grouped.items()
    }


def legacy_company_type(facts: Iterable[TaxonomyFact]) -> str:
    """Return the conservative legacy company-type value used by old callers.

    ``company_type`` was historically a catch-all field.  Only a source that
    explicitly declares an ownership sector may populate the legacy adapter;
    legal forms, ATS departments, and filing entity types remain ``unknown``.
    """

    ownership = [fact.value for fact in facts if fact.semantic_field == "ownership_sector"]
    if len(set(ownership)) == 1 and ownership:
        return ownership[0]
    return "unknown"


def classify_company(
    entity_id: str,
    capabilities: dict[str, str],
    *,
    evidence_complete: bool,
    identity_resolved: bool = True,
    period_aligned: bool = False,
    unit_aligned: bool = True,
    available_at_present: bool = True,
    taxonomy_facts: Iterable[TaxonomyFact] = (),
) -> CompanyClassification:
    allowed = {"available", "unavailable", "unknown", "context_only", "proxy_only"}
    normalized = {axis: capabilities.get(axis, "unknown") for axis in CAPABILITY_AXES}
    normalized = {axis: status if status in allowed else "unknown" for axis, status in normalized.items()}
    reasons = [f"{axis}_{status}" for axis, status in normalized.items() if status != "available"]
    if not evidence_complete:
        reasons.append("missing-aligned-series")
    eligibility = evaluate_analysis_eligibility(
        identity_resolved=identity_resolved,
        period_aligned=period_aligned and evidence_complete,
        unit_aligned=unit_aligned,
        available_at_present=available_at_present,
    )
    if not evidence_complete and "missing-aligned-series" not in eligibility.reasons:
        eligibility = AnalysisEligibility(
            eligibility.correlation_ready,
            eligibility.causal_ready,
            (*eligibility.reasons, "missing-aligned-series"),
        )
    facts = tuple(taxonomy_facts)
    return CompanyClassification(entity_id, normalized, eligibility, tuple(reasons), facts)


def identity_eligibility(status: str | None) -> dict[str, object]:
    """Describe which public-sector axes can be used as hard filters."""

    normalized = str(status or "unresolved")
    if normalized == "linked":
        return {"identity_status": normalized, "filterable": True, "reason": None}
    if normalized == "conflict":
        return {"identity_status": normalized, "filterable": False, "reason": "identity_conflict"}
    return {"identity_status": normalized if normalized == "candidate" else "unresolved", "filterable": False, "reason": "identity_unresolved"}


def public_sector_axes(
    *, public_context: str | None = None, public_institution_type: str | None = None,
    legal_form: str | None = None, ownership_sector: str | None = None, identity_status: str | None = None,
) -> dict[str, dict[str, object]]:
    """Keep source context, institution type, legal form, and ownership independent."""

    link = identity_eligibility(identity_status)
    return {
        "public_context": {"value": public_context, "filterable": public_context is not None, "source_scoped": True},
        "public_institution_type": {"value": public_institution_type, "filterable": bool(link["filterable"] and public_institution_type), "identity": link},
        "legal_form": {"value": legal_form, "filterable": bool(link["filterable"] and legal_form), "identity": link},
        "ownership_sector": {"value": ownership_sector, "filterable": bool(link["filterable"] and ownership_sector), "identity": link},
    }


from dataclasses import dataclass, field


@dataclass(frozen=True)
class ClusterSignature:
    """5-level composable cluster signature for macro roll-up and micro cohort drill-down.

    Key structure: <Region>:<Sector>:<Tier>:<Contract>:<Workplace>
    Wildcard: 'ALL' matches any value in that level.
    """
    region: str = "ALL"        # KR, CZ, US, ALL
    sector: str = "ALL"        # PUBLIC_INSTITUTION, STATE_OWNED, PRIVATE, GOVERNMENT, ALL
    tier: str = "ALL"          # KOSPI, KOSDAQ, CZ_SRO, CZ_AS, SOE_MARKET, ALL
    contract: str = "ALL"      # REGULAR, NON_REGULAR, INTERN, INDEFINITE, ALL
    workplace: str = "ALL"     # ONSITE, HYBRID, REMOTE, ALL

    @property
    def key(self) -> str:
        return f"{self.region}:{self.sector}:{self.tier}:{self.contract}:{self.workplace}"

    def matches(self, other: ClusterSignature) -> bool:
        """Wildcard matching for Roll-up and Drill-down queries."""
        for field in ("region", "sector", "tier", "contract", "workplace"):
            v1, v2 = getattr(self, field), getattr(other, field)
            if v1 != "ALL" and v2 != "ALL" and v1 != v2:
                return False
        return True

    @classmethod
    def parse(cls, key_str: str) -> ClusterSignature:
        parts = key_str.split(":")
        region = parts[0] if len(parts) > 0 and parts[0] else "ALL"
        sector = parts[1] if len(parts) > 1 and parts[1] else "ALL"
        tier = parts[2] if len(parts) > 2 and parts[2] else "ALL"
        contract = parts[3] if len(parts) > 3 and parts[3] else "ALL"
        workplace = parts[4] if len(parts) > 4 and parts[4] else "ALL"
        return cls(region=region, sector=sector, tier=tier, contract=contract, workplace=workplace)


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
    sector, tier = sector_map.get(str(instt_se or "").lower(), ("PUBLIC_INSTITUTION", "ALL"))
    contract = contract_map.get(str(pblanc_ty or "").lower(), "ALL")
    workplace = "REMOTE" if work_type == "remote" else ("HYBRID" if work_type == "hybrid" else "ONSITE")
    return ClusterSignature(region="KR", sector=sector, tier=tier, contract=contract, workplace=workplace)


def from_kr_worknet(
    coclcd: str | None = None,
    emptype: str | None = None,
    work_type: str | None = None,
) -> ClusterSignature:
    """Map Korean WorkNet API attributes (coClcd, empType) to ClusterSignature."""
    sector_tier_map = {
        "01": ("PRIVATE", "LARGE_CONGLOMERATE"),
        "02": ("PRIVATE", "MID_SIZED"),
        "03": ("PRIVATE", "SME"),
        "04": ("PRIVATE", "VENTURE"),
        "05": ("STATE_OWNED", "PUBLIC_CORP"),
        "06": ("PRIVATE", "FOREIGN_INVESTED"),
    }
    contract_map = {
        "10": "REGULAR",
        "20": "NON_REGULAR",
        "40": "DISPATCHED",
    }
    sector, tier = sector_tier_map.get(str(coclcd or ""), ("PRIVATE", "ALL"))
    contract = contract_map.get(str(emptype or ""), "ALL")
    workplace = "REMOTE" if work_type == "remote" else "ONSITE"
    return ClusterSignature(region="KR", sector=sector, tier=tier, contract=contract, workplace=workplace)


def from_kr_opendart(
    corp_cls: str | None = None,
    induty_code: str | None = None,
) -> ClusterSignature:
    """Map Korean OpenDART API attributes (corp_cls) to ClusterSignature."""
    tier_map = {
        "Y": "KOSPI",
        "K": "KOSDAQ",
        "N": "KONEX",
        "E": "EXTERNAL_AUDIT",
    }
    tier = tier_map.get(str(corp_cls or "").upper(), "ALL")
    return ClusterSignature(region="KR", sector="PRIVATE", tier=tier, contract="ALL", workplace="ALL")


def from_cz_ares(
    pravni_forma: str | None = None,
    cz_nace: str | None = None,
) -> ClusterSignature:
    """Map Czech ARES Register attributes (pravniForma) to ClusterSignature."""
    form_map = {
        "101": ("PRIVATE", "CZ_OSVC"),
        "112": ("PRIVATE", "CZ_SRO"),
        "121": ("PRIVATE", "CZ_AS"),
        "301": ("STATE_OWNED", "CZ_STATNI_PODNIK"),
        "331": ("PUBLIC_INSTITUTION", "CZ_PRISPEVKOVA_ORG"),
        "325": ("GOVERNMENT", "CZ_ORGANIZACNI_SLOZKA"),
        "701": ("PRIVATE", "CZ_DRUZSTVO"),
        "421": ("PRIVATE", "CZ_FOREIGN_BRANCH"),
    }
    sector, tier = form_map.get(str(pravni_forma or ""), ("PRIVATE", "ALL"))
    return ClusterSignature(region="CZ", sector=sector, tier=tier, contract="ALL", workplace="ALL")


def from_cz_mpsv(
    statni_sprava: bool | None = None,
    typ_mzdy: str | None = None,
) -> ClusterSignature:
    """Map Czech MPSV Job Portal attributes (statniSpravaSamosprava) to ClusterSignature."""
    sector = "PUBLIC_INSTITUTION" if statni_sprava else "PRIVATE"
    return ClusterSignature(region="CZ", sector=sector, tier="ALL", contract="REGULAR", workplace="ONSITE")


def from_us_sec_or_usaspending(
    recipient_type: str | None = None,
    entity_type: str | None = None,
) -> ClusterSignature:
    """Map US SEC / USAspending attributes to ClusterSignature."""
    if recipient_type == "for_profit_organization":
        return ClusterSignature(region="US", sector="PRIVATE", tier="US_FOR_PROFIT", contract="ALL", workplace="ALL")
    if recipient_type == "nonprofit_organization":
        return ClusterSignature(region="US", sector="PUBLIC_INSTITUTION", tier="US_NONPROFIT", contract="ALL", workplace="ALL")
    if recipient_type in ("state_government", "local_government"):
        return ClusterSignature(region="US", sector="GOVERNMENT", tier="US_LOCAL_GOV", contract="ALL", workplace="ALL")
    if recipient_type == "higher_education":
        return ClusterSignature(region="US", sector="PUBLIC_INSTITUTION", tier="US_HIGHER_ED", contract="ALL", workplace="ALL")
    return ClusterSignature(region="US", sector="PRIVATE", tier="ALL", contract="ALL", workplace="ALL")


class KeyAlignmentError(KeyError):
    """Raised when a raw job record from an API lacks required attributes or alias keys."""
    pass


@dataclass(frozen=True)
class CanonicalJobRecord:
    """Canonical cross-national job vacancy record with 5-level ClusterSignature."""

    job_id: str
    job_url: str
    employer_name: str
    org_id: str
    job_title: str
    occupation_code: str
    education_level: str
    contract_type: str
    salary_min: Any
    salary_max: Any
    currency: str
    location: str
    deadline: str
    description: str
    source_api: str
    cluster_signature: ClusterSignature
    legal_form: str = ""
    entity_type: str = ""
    hours_or_headcount: str = ""
    raw_attributes: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "job_url": self.job_url,
            "employer_name": self.employer_name,
            "org_id": self.org_id,
            "legal_form": self.legal_form,
            "entity_type": self.entity_type,
            "job_title": self.job_title,
            "occupation_code": self.occupation_code,
            "education_level": self.education_level,
            "contract_type": self.contract_type,
            "hours_or_headcount": self.hours_or_headcount,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "currency": self.currency,
            "location": self.location,
            "deadline": self.deadline,
            "description": self.description,
            "source_api": self.source_api,
            "cluster_key": self.cluster_signature.key,
        }


@dataclass
class DynamicAttributeDefinition:
    """Definition of an API return attribute with aliases, type, and optional constraint validator."""
    name: str
    aliases: tuple[str, ...]
    data_type: type = str
    required: bool = False
    default: Any = None
    validator: Any = None  # Callable[[Any], bool] | None
    description: str = ""


class DynamicJobSchemaRegistry:
    """Dynamic attribute registration and constraint validation engine for API return attributes.
    
    Allows dynamic registration of new API attributes, aliases, and constraint validators
    at runtime across different industry sectors (IT, Civil, Fire Safety, Energy Risk, etc.)
    without modifying static class definitions.
    """
    _registry: dict[str, DynamicAttributeDefinition] = {}

    @classmethod
    def register_attribute(
        cls,
        name: str,
        aliases: tuple[str, ...] | list[str],
        data_type: type = str,
        required: bool = False,
        default: Any = None,
        validator: Any = None,
        description: str = "",
    ) -> None:
        """Register a new API return attribute dynamically into the schema contract."""
        cls._registry[name] = DynamicAttributeDefinition(
            name=name,
            aliases=tuple(aliases),
            data_type=data_type,
            required=required,
            default=default,
            validator=validator,
            description=description,
        )

    @classmethod
    def get_attribute(cls, name: str) -> DynamicAttributeDefinition | None:
        return cls._registry.get(name)

    @classmethod
    def list_registered_attributes(cls) -> list[dict[str, Any]]:
        """List all dynamically registered attributes and their alias mappings."""
        return [
            {
                "canonical_name": attr.name,
                "aliases": list(attr.aliases),
                "data_type": attr.data_type.__name__,
                "required": attr.required,
                "default": attr.default,
                "description": attr.description,
                "has_custom_validator": attr.validator is not None,
            }
            for attr in cls._registry.values()
        ]

    @classmethod
    def validate_and_extract(cls, raw: dict[str, Any], provider: str = "UNKNOWN") -> dict[str, Any]:
        """Extract all registered dynamic attributes from raw API payload and enforce constraints."""
        extracted: dict[str, Any] = {}
        missing_errors: list[str] = []
        constraint_errors: list[str] = []

        for name, attr in cls._registry.items():
            matched_val = None
            for alias in attr.aliases:
                val = raw.get(alias)
                if val is not None and str(val).strip() != "" and str(val).lower() != "none":
                    matched_val = val
                    break

            if matched_val is None:
                if attr.required:
                    missing_errors.append(f"Dynamic required field '{name}' missing; checked aliases {attr.aliases}")
                else:
                    extracted[name] = attr.default
                continue

            # Type casting
            try:
                if attr.data_type in (int, float) and isinstance(matched_val, (str, int, float)):
                    matched_val = attr.data_type(str(matched_val).replace(",", "").strip())
                elif attr.data_type is bool and isinstance(matched_val, str):
                    matched_val = matched_val.lower() in ("true", "1", "y", "yes")
                elif attr.data_type is str and not isinstance(matched_val, str):
                    matched_val = str(matched_val).strip()
            except Exception as e:
                constraint_errors.append(f"Type cast error for '{name}'={matched_val} to {attr.data_type.__name__}: {e}")
                continue

            # Constraint validation
            if attr.validator and callable(attr.validator):
                try:
                    if not attr.validator(matched_val):
                        constraint_errors.append(f"Constraint check failed for '{name}' with value '{matched_val}'")
                        continue
                except Exception as e:
                    constraint_errors.append(f"Validator exception for '{name}': {e}")
                    continue

            extracted[name] = matched_val

        all_errors = missing_errors + constraint_errors
        if all_errors:
            raise KeyAlignmentError(
                f"[{provider}] Dynamic schema contract violation:\n  " + "\n  ".join(all_errors)
            )

        return extracted


class JobSchemaContract:
    """Enforces attribute key alignment and defends against silent None omissions across APIs."""

    REQUIRED_CANONICAL_FIELDS: dict[str, tuple[str, ...]] = {
        "job_id": ("job_id", "portal_id", "idx", "pblJobId", "PositionID", "MatchedObjectId", "id", "wantedAuthNo"),
        "job_url": ("posting_url", "job_url", "url", "pbancUrl", "srcUrl", "PositionURI", "wantedInfoUrl"),
        "employer_name": ("employer_name", "employer", "institution_name", "insttNm", "insttname", "OrganizationName", "company"),
        "job_title": ("job_title", "job_title_cz", "title", "PositionTitle", "pblJobNm"),
    }

    @classmethod
    def register_dynamic_attribute(
        cls,
        name: str,
        aliases: tuple[str, ...] | list[str],
        data_type: type = str,
        required: bool = False,
        default: Any = None,
        validator: Any = None,
        description: str = "",
    ) -> None:
        """Register a new API return attribute dynamically into the schema contract."""
        DynamicJobSchemaRegistry.register_attribute(
            name=name,
            aliases=aliases,
            data_type=data_type,
            required=required,
            default=default,
            validator=validator,
            description=description,
        )

    @classmethod
    def list_dynamic_attributes(cls) -> list[dict[str, Any]]:
        return DynamicJobSchemaRegistry.list_registered_attributes()

    @classmethod
    def validate_and_normalize(cls, raw_job: dict[str, Any], provider: str) -> dict[str, Any]:
        """Validate presence of required canonical keys and resolve aliases."""
        normalized = dict(raw_job)
        missing_errors: list[str] = []

        for canonical_key, aliases in cls.REQUIRED_CANONICAL_FIELDS.items():
            matched_val = None
            matched_alias = None
            for alias in aliases:
                val = raw_job.get(alias)
                if val is not None and str(val).strip() != "" and str(val).lower() != "none":
                    matched_val = str(val).strip()
                    matched_alias = alias
                    break

            # Handle deterministic portal URL synthesis for Czech MPSV if job_url missing
            if canonical_key == "job_url":
                if matched_val is not None:
                    if matched_val.startswith("www.") or (not matched_val.startswith("http://") and not matched_val.startswith("https://") and "." in matched_val):
                        matched_val = f"https://{matched_val}"
                elif provider in ("CZ_MPSV", "MPSV"):
                    portal_id = raw_job.get("portal_id") or raw_job.get("job_id")
                    if portal_id:
                        matched_val = f"https://www.uradprace.cz/web/cz/volna-mista-v-cr#/volna-mista-detail/{str(portal_id).strip()}"
                        matched_alias = "synthesized:portal_id"

            if matched_val is None:
                missing_errors.append(f"Field '{canonical_key}' missing; checked aliases {aliases}")
            else:
                normalized[canonical_key] = matched_val
                normalized[f"_{canonical_key}_source_alias"] = matched_alias

        if missing_errors:
            raise KeyAlignmentError(
                f"[{provider}] Job schema contract violation:\n  " + "\n  ".join(missing_errors)
            )

        # Also extract any registered dynamic attributes
        if DynamicJobSchemaRegistry._registry:
            dynamic_vals = DynamicJobSchemaRegistry.validate_and_extract(raw_job, provider=provider)
            normalized.update(dynamic_vals)

        return normalized


def from_cz_mpsv_job_record(raw: dict[str, Any], entity_meta: dict[str, Any] | None = None) -> CanonicalJobRecord:
    """Normalize raw Czech MPSV vacancy record into CanonicalJobRecord with ClusterSignature."""
    clean = JobSchemaContract.validate_and_normalize(raw, provider="CZ_MPSV")
    meta = entity_meta or {}

    statni_sprava = raw.get("public_administration_flag")
    if statni_sprava is None:
        statni_sprava = str(raw.get("statni_sprava", "")).lower() in ("true", "1")
    else:
        statni_sprava = bool(statni_sprava)

    sig = from_cz_mpsv(statni_sprava=statni_sprava)
    legal_form = meta.get("legal_form") or raw.get("legal_form") or ""
    tier = meta.get("entity_type") or ("CZ_PUBLIC" if statni_sprava else "CZ_PRIVATE")
    sig = ClusterSignature(
        region="CZ",
        sector=sig.sector,
        tier=tier,
        contract="REGULAR" if "plny" in str(raw.get("employment_relationship_codes", "")).lower() else "ALL",
        workplace="ONSITE",
    )

    edu = str(raw.get("minimum_education_code", "")).replace("VzdelaniDetailniKategorie/", "").strip()
    isco = str(raw.get("cz_isco", "")).replace("CzIsco/", "").strip()

    weekly_hours = str(raw.get("weekly_hours") or "").strip()
    places = str(raw.get("vacancy_places") or "").strip()
    hours_hc = f"{weekly_hours}h/주 ({places}명 모집)" if weekly_hours and places else (f"{weekly_hours}h/주" if weekly_hours else (f"{places}명 모집" if places else "-"))

    return CanonicalJobRecord(
        job_id=clean["job_id"],
        job_url=clean["job_url"],
        employer_name=clean["employer_name"],
        org_id=str(raw.get("employer_ico", "")).strip(),
        job_title=clean["job_title"],
        occupation_code=isco,
        education_level=edu or "무관/기타",
        contract_type=str(raw.get("employment_relationship_codes", "plny")).replace("PracovnepravniVztah/", ""),
        salary_min=raw.get("salary_from_czk") or "내규/협의",
        salary_max=raw.get("salary_to_czk") or "내규/협의",
        currency=str(raw.get("salary_currency") or "CZK").strip(),
        location=str(raw.get("workplace_municipality_code") or "Praha (CZ0100)"),
        deadline=str(raw.get("expiry_date") or "").strip(),
        description=str(raw.get("job_description_cz") or raw.get("requirement_narrative") or "")[:300],
        source_api="MPSV_CZ_JOB_VACANCY_API",
        cluster_signature=sig,
        legal_form=legal_form or "공공기관 / 국가행정조직",
        entity_type=tier,
        hours_or_headcount=hours_hc,
        raw_attributes=raw,
    )


def from_kr_public_job_record(raw: dict[str, Any]) -> CanonicalJobRecord:
    """Normalize raw Korean JOB-ALIO vacancy record into CanonicalJobRecord with ClusterSignature."""
    clean = JobSchemaContract.validate_and_normalize(raw, provider="JOB_ALIO")

    instt_type = str(raw.get("institution_type_filter") or raw.get("instt_se") or "").strip().lower()
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
    hours_hc = f"{career} ({headcount}명)" if career and headcount else (headcount or career or "-")

    if "정규직" in emp_type or emp_type.lower() == "e01":
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
        workplace="ONSITE",
    )

    return CanonicalJobRecord(
        job_id=clean["job_id"],
        job_url=clean["job_url"],
        employer_name=clean["employer_name"],
        org_id=str(raw.get("org_id") or raw.get("institution_type_filter") or raw.get("instt_code") or "").strip(),
        job_title=clean["job_title"],
        occupation_code=str(raw.get("ncs_job") or "").strip(),
        education_level=str(raw.get("education") or "학력무관").strip(),
        contract_type=str(raw.get("employment_type") or "정규직").strip(),
        salary_min=raw.get("salary_min") or "내규",
        salary_max=raw.get("salary_max") or "내규",
        currency="KRW",
        location=str(raw.get("location") or raw.get("region") or raw.get("workRgnNm") or "전국").strip(),
        deadline=str(raw.get("closeDate") or raw.get("closing_at") or raw.get("posting_period") or "").strip(),
        description=str(raw.get("eligibility_summary") or raw.get("description") or "")[:300],
        source_api="JOB_ALIO_RECRUIT_API",
        cluster_signature=sig,
        legal_form="공공기관 / 공기업",
        entity_type=entity_name,
        hours_or_headcount=hours_hc,
        raw_attributes=raw,
    )


def from_sk_upsvar_record(raw: dict[str, Any]) -> CanonicalJobRecord:
    """Normalize raw Slovak ÚPSVaR vacancy record into CanonicalJobRecord with ClusterSignature."""
    clean = JobSchemaContract.validate_and_normalize(raw, provider="SK_UPSVAR")

    sig = ClusterSignature(
        region="SK",
        sector="STATE_OWNED" if "Štátny" in str(raw.get("legal_form", "")) else "PUBLIC_INSTITUTION",
        tier=str(raw.get("entity_type", "PUBLIC")),
        contract="REGULAR",
        workplace="ONSITE",
    )

    return CanonicalJobRecord(
        job_id=clean["job_id"],
        job_url=clean["job_url"],
        employer_name=clean["employer_name"],
        org_id=str(raw.get("ico", "")).strip(),
        job_title=clean["job_title"],
        occupation_code=str(raw.get("isco", "")).strip(),
        education_level=str(raw.get("edu", "bakal")).strip(),
        contract_type="REGULAR",
        salary_min=raw.get("sal_min") or 0,
        salary_max=raw.get("sal_max") or 0,
        currency=str(raw.get("curr", "EUR")).strip(),
        location=str(raw.get("loc", "Bratislava (SK010)")).strip(),
        deadline=str(raw.get("closing_at", "2026-12-31")).strip(),
        description=str(raw.get("desc", ""))[:300],
        source_api="UPSVAR_SK_JOB_API",
        cluster_signature=sig,
        legal_form=str(raw.get("legal_form", "Štátny podnik")),
        entity_type=str(raw.get("entity_type", "국영 공기업")),
        hours_or_headcount="주 40시간 (1명)",
        raw_attributes=raw,
    )


def from_us_usajobs_record(raw: dict[str, Any]) -> CanonicalJobRecord:
    """Normalize raw US USAJOBS vacancy record into CanonicalJobRecord with ClusterSignature."""
    clean = JobSchemaContract.validate_and_normalize(raw, provider="US_USAJOBS")

    sig = ClusterSignature(
        region="US",
        sector="GOVERNMENT",
        tier="FEDERAL_GS",
        contract="REGULAR" if "Permanent" in str(raw.get("PositionOfferingType", "")) else "ALL",
        workplace="REMOTE" if raw.get("UserArea", {}).get("Details", {}).get("TeleworkEligible") else "ONSITE",
    )

    remun = raw.get("PositionRemuneration", [{}])
    min_sal = remun[0].get("MinimumRange") if isinstance(remun, list) and remun else None
    max_sal = remun[0].get("MaximumRange") if isinstance(remun, list) and remun else None

    return CanonicalJobRecord(
        job_id=clean["job_id"],
        job_url=clean["job_url"],
        employer_name=clean["employer_name"],
        org_id=str(raw.get("DepartmentName", "")).strip(),
        job_title=clean["job_title"],
        occupation_code=str(raw.get("JobCode", "")).strip(),
        education_level=str(raw.get("EducationRequirement", "bachelor")).strip(),
        contract_type=str(raw.get("PositionOfferingType", "Permanent")).strip(),
        salary_min=min_sal or "Negotiable",
        salary_max=max_sal or "Negotiable",
        currency="USD",
        location=str(raw.get("PositionLocationDisplay", "Washington, DC")).strip(),
        deadline=str(raw.get("ApplicationCloseDate", "")).strip(),
        description=str(raw.get("UserArea", {}).get("Details", {}).get("JobSummary", ""))[:300],
        source_api="USAJOBS_SEARCH_API",
        cluster_signature=sig,
        legal_form="Federal Executive Branch",
        entity_type="연방정부 공공기구",
        hours_or_headcount=str(raw.get("PositionOfferingType", "Permanent Full-Time")),
        raw_attributes=raw,
    )


# =========================================================================
# Pre-flight Baseline Cluster Space Disclosure & Dynamic Report Schema
# =========================================================================

BASELINE_API_CATALOG = {
    "total_providers": 28,
    "keyed_providers": 12,
    "keyless_providers": 16,
    "total_source_attributes": 142,
    "field_dictionary": {
        "identifier_url_status": [
            ("job_id", "공고 고유 식별자"),
            ("portal_id", "포털 관리번호"),
            ("idx", "순번 인덱스"),
            ("posting_url", "원천 공고 URL"),
            ("PositionURI", "미국 연방공고 웹주소"),
            ("wantedInfoUrl", "워크넷 상세정보 URL"),
        ],
        "entity_status": [
            ("pravniForma", "체코 법적·법인 형태 코드 (301: 국영기업 등)"),
            ("instt_se", "한국 공공기관 구분 코드 (시장형/준정부 등)"),
            ("corp_cls", "DART 법인분류 (Y: 유가, K: 코스닥, N: 코넥스, E: 기타)"),
            ("recipient_type", "USAspending 수주자 법인유형"),
            ("apbaTypeNa", "알리오 기관유형 공식명칭"),
        ],
        "job_competency_education": [
            ("isco", "ISCO-08 국제표준직업분류 코드"),
            ("ncs_job", "NCS 국가직무능력표준 세분류"),
            ("edu", "최소 학력 요건"),
            ("QualificationSummary", "미국 연방 자격요건 요약"),
            ("competency_unit", "NCS 직무능력단위 명칭"),
        ],
        "working_conditions_wage": [
            ("salary_min/max", "최소/최대 급여 (월급/연봉)"),
            ("weekly_hours", "주당 소정 근로시간"),
            ("employment_type", "고용 계약 형태 (정규/계약/인턴)"),
            ("CurrencyCode", "급여 지급 통화 코드 (KRW, CZK, USD, EUR)"),
        ],
        "financial_procurement_activity": [
            ("Award Amount", "미 연방조달 계약 체결 금액"),
            ("Assets USD", "SEC 공시 총자산 (USD 환산액)"),
            ("capital_stock", "자본금 총액"),
            ("pushed_at", "GitHub 최근 커밋 일시"),
            ("publication_year", "OpenAlex 논문 발행연도"),
        ],
    },
    "dimension_dictionary": {
        "region": [
            ("KR", "한국"),
            ("CZ", "체코"),
            ("SK", "슬로바키아"),
            ("US", "미국"),
            ("ALL", "전체 국가"),
        ],
        "sector": [
            ("PUBLIC_INSTITUTION", "공공기관"),
            ("STATE_OWNED", "국영기업/공기업"),
            ("GOVERNMENT", "정부부처/지자체"),
            ("PRIVATE", "민간기업"),
            ("ALL", "전체 섹터"),
        ],
        "tier_samples": [
            ("KOSPI", "유가증권시장 상장"),
            ("KOSDAQ", "코스닥 상장"),
            ("MARKET_SOE", "시장형 공기업"),
            ("QUASI_GOV", "준정부기관"),
            ("OTHER_PUBLIC", "기타공공기관"),
            ("CZ_STATNI_PODNIK", "체코 국영기업"),
            ("CZ_PRISPEVKOVA_ORG", "체코 출연/보조기관"),
            ("SK_STATNY_PODNIK", "슬로바키아 국영기업"),
            ("FEDERAL_GS", "미 연방 일반직 급여체계"),
            ("US_FOR_PROFIT", "미국 영리기업"),
            ("US_HIGHER_ED", "미국 고등교육/대학"),
            ("ALL", "전체 티어"),
        ],
        "contract": [
            ("REGULAR", "정규직"),
            ("NON_REGULAR", "계약직/비정규직"),
            ("INTERN", "인턴/수습"),
            ("INDEFINITE", "무기계약직 (체코/슬로바키아)"),
            ("DISPATCHED", "파견직"),
            ("ALL", "전체 고용형태"),
        ],
        "workplace": [
            ("ONSITE", "현장출근"),
            ("HYBRID", "하이브리드 원격혼합"),
            ("REMOTE", "전면 재택원격"),
            ("ALL", "전체 근무방식"),
        ],
    },
    "dimensions": {
        "region": ["KR", "CZ", "SK", "US", "ALL"],
        "sector": ["PUBLIC_INSTITUTION", "STATE_OWNED", "GOVERNMENT", "PRIVATE", "ALL"],
        "tier": [
            "KOSPI", "KOSDAQ", "KONEX", "EXTERNAL_AUDIT", "MARKET_SOE", "QUASI_GOV",
            "OTHER_PUBLIC", "LOCAL_SOE", "LARGE_CONGLOMERATE", "MID_SIZED", "SME", "VENTURE",
            "PUBLIC_CORP", "FOREIGN_INVESTED", "CENTRAL_GOV", "LOCAL_GOV",
            "CZ_STATNI_PODNIK", "CZ_PRISPEVKOVA_ORG", "CZ_SRO", "CZ_AS", "CZ_OSVC",
            "CZ_ORGANIZACNI_SLOZKA", "CZ_DRUZSTVO", "CZ_FOREIGN_BRANCH",
            "SK_STATNY_PODNIK", "SK_SAV", "SK_PRISPEVKOVA", "SK_STATNY_ORGAN", "SK_AS",
            "FEDERAL_GS", "US_FOR_PROFIT", "US_NONPROFIT", "US_HIGHER_ED", "US_LOCAL_GOV",
            "ALL"
        ],
        "contract": ["REGULAR", "NON_REGULAR", "INTERN", "INDEFINITE", "DISPATCHED", "ALL"],
        "workplace": ["ONSITE", "HYBRID", "REMOTE", "ALL"],
    },
    "theoretical_combinations": 5 * 5 * 35 * 6 * 4,  # 21,000
    "physical_records": 741,
    "physical_entities": 18238,
}


def get_cluster_baseline_spec_text() -> str:
    """Return the fixed pre-flight baseline cluster space disclosure string with dual original and Korean terms."""
    cat = BASELINE_API_CATALOG
    dim = cat["dimensions"]
    fdict = cat["field_dictionary"]
    ddict = cat["dimension_dictionary"]

    def _fmt_fields(items: list[tuple[str, str]]) -> str:
        return ", ".join(f"{orig} ({ko})" for orig, ko in items)

    def _fmt_dims(items: list[tuple[str, str]]) -> str:
        return ", ".join(f"{code} ({ko})" for code, ko in items)

    return f"""========================================================================================
[Company-Intel Platform] 28대 연결 API 기반 클러스터 시그니처 제어 공간 명세
========================================================================================
1. 총 연결 데이터 공급자: {cat['total_providers']}개 API (Keyed: {cat['keyed_providers']}개, Keyless: {cat['keyless_providers']}개)
   - 한국 (KR: 6)   : ALIO (경영공시/채용), WorkNet (고용정보), OpenDART (기업공시), HRDKorea (NCS직무능력), ECOS (한국은행), MPM (인사혁신처)
   - 체코 (CZ: 3)   : ARES (경제주체등록원·법인형태), MPSV (통합구인포털), CNB (체코국립은행 환율/금리)
   - 슬로바키아 (SK: 3) : ÚPSVaR (중앙노동포털), RPO (법인등록원), SAV (국립과학원 연구기관)
   - 미국 (US: 6)   : SEC EDGAR (공시/XBRL), USAspending (연방조달), USAJobs (연방채용), BLS (노동통계), FRED (연은경제데이터), BEA (경제분석국)
   - 글로벌/EU (10) : GLEIF (글로벌법인식별자), TED (EU공공조달), Greenhouse (글로벌채용), Lever (글로벌채용), GitHub (오픈소스활동), OpenAlex (글로벌학술), Eurostat (EU통계), ECB (유럽중앙은행), OECD (경제협력개발기구), WorldBank (세계은행)

2. 물리적 원천 속성 풀: 총 {cat['total_source_attributes']}개 원천 필드 (원어 및 한국어 정규화 의미 1:1 매핑)
   - 식별자/URL/상태 : {_fmt_fields(fdict['identifier_url_status'])} 등 (22개)
   - 법인/기관 지위  : {_fmt_fields(fdict['entity_status'])} 등 (18개)
   - 직무/역량/학력  : {_fmt_fields(fdict['job_competency_education'])} 등 (34개)
   - 근로조건/임금   : {_fmt_fields(fdict['working_conditions_wage'])} 등 (28개)
   - 재무/조달/활동성: {_fmt_fields(fdict['financial_procurement_activity'])} 등 (40개)

3. 5계층 클러스터 시그니처 (<Region>:<Sector>:<Tier>:<Contract>:<Workplace>) 제어 공간:
   - [Level 0] Region    ({len(dim['region']):2d}개) : {_fmt_dims(ddict['region'])}
   - [Level 1] Sector    ({len(dim['sector']):2d}개) : {_fmt_dims(ddict['sector'])}
   - [Level 2] Tier      ({len(dim['tier']):2d}개) : {_fmt_dims(ddict['tier_samples'])}
   - [Level 3] Contract  ({len(dim['contract']):2d}개) : {_fmt_dims(ddict['contract'])}
   - [Level 4] Workplace ({len(dim['workplace']):2d}개) : {_fmt_dims(ddict['workplace'])}
   => 이론적 제어 가능 조합: {len(dim['region'])} × {len(dim['sector'])} × {len(dim['tier'])} × {len(dim['contract'])} × {len(dim['workplace'])} = 총 {cat['theoretical_combinations']:,}개 다차원 클러스터 좌표

4. 현재 물리적 앵커 데이터: {cat['physical_records']}건 전수 검증 공고 및 {cat['physical_entities']:,}개 등록 기관 1:1 무결성 바인딩
========================================================================================"""


def resolve_active_providers(signature: ClusterSignature) -> dict[str, Any]:
    """Resolve active providers, attribute space, and free dimensions for a ClusterSignature."""
    region = signature.region
    sector = signature.sector
    tier = signature.tier

    provider_map = {
        "KR": ["mpm_public_employment", "alioplus_organization", "worknet", "opendart", "hrdkorea", "ecos"],
        "CZ": ["ares", "mpsv_cz", "cnb_exchange", "cnb_czeonia"],
        "SK": ["upsvar_sk", "rpo_sk", "sav_research"],
        "US": ["sec_submissions", "sec_companyfacts", "usaspending", "usajobs", "bls", "fred", "bea"],
        "ALL": ["mpm_public_employment", "mpsv_cz", "upsvar_sk", "usajobs", "ares", "opendart", "sec_submissions"],
    }
    active_providers = provider_map.get(region, provider_map["ALL"])

    # Determine free dimensions
    free_dims = []
    if signature.region == "ALL":
        free_dims.append("region")
    if signature.sector == "ALL":
        free_dims.append("sector")
    if signature.tier == "ALL":
        free_dims.append("tier")
    if signature.contract == "ALL":
        free_dims.append("contract")
    if signature.workplace == "ALL":
        free_dims.append("workplace")

    return {
        "signature_key": signature.key,
        "active_providers": active_providers,
        "free_dimensions": free_dims,
        "is_macro_rollup": len(free_dims) >= 3,
        "is_micro_cohort": len(free_dims) == 0,
    }


@dataclass(frozen=True)
class DynamicColumnSpec:
    """Specification of an Excel column in a dynamically compiled report."""
    index: int
    header: str
    field_key: str
    column_letter: str
    alignment: str = "left"
    is_hyperlink: bool = False
    is_freshness: bool = False
    formula_template: str = ""


class DynamicReportSchemaCompiler:
    """Compiles dynamic workbook schemas based on pinned cluster signature and active attributes."""

    CORE_HEADERS = [
        ("순번 (No)", "no", "center"),
        ("국가 (Country)", "country", "center"),
        ("기관/기업명 (Employer Name)", "employer_name", "left"),
        ("사업자등록번호 (IČO / Org ID)", "org_id", "center"),
        ("공고 고유 식별자 (Job ID)", "job_id", "center"),
        ("공식 직무명 (Job Title)", "job_title", "left"),
        ("직업/NCS/ISCO 코드 (Job Code)", "occupation_code", "center"),
        ("클러스터 시그니처 (Cluster Signature)", "cluster_key", "center"),
    ]

    PROVENANCE_HEADERS = [
        ("원천 공고 URL (Posting URL)", "job_url", "left"),
        ("공고 바로가기 (Clickable Hyperlink)", "hyperlink", "center"),
        ("공고 실시간 상태 (Listing Freshness)", "freshness", "center"),
        ("접수 마감일 (Application Deadline)", "deadline", "center"),
        ("원천 API 명칭 (Source API)", "source_api", "center"),
        ("무결성 검증 (Join Verified)", "join_verified", "center"),
        ("검증 메모 (Verification Note)", "verification_note", "left"),
    ]

    @classmethod
    def get_column_letter(cls, col_idx: int) -> str:
        """Convert 1-based column index to Excel column letter (e.g., 1 -> A, 27 -> AA)."""
        string = ""
        while col_idx > 0:
            col_idx, remainder = divmod(col_idx - 1, 26)
            string = chr(65 + remainder) + string
        return string

    @classmethod
    def compile_schema(cls, dynamic_attributes: list[str] | None = None) -> list[DynamicColumnSpec]:
        """Compile complete ordered list of DynamicColumnSpec with dynamic hyperlink target indexing."""
        attrs = dynamic_attributes or [
            "legal_form", "entity_type", "hours_or_headcount", "salary_min",
            "salary_max", "currency", "location", "education_level", "role_equiv", "description"
        ]

        specs: list[DynamicColumnSpec] = []
        col_idx = 1

        # 1. Core Layer
        for header, key, align in cls.CORE_HEADERS:
            letter = cls.get_column_letter(col_idx)
            specs.append(DynamicColumnSpec(col_idx, header, key, letter, align))
            col_idx += 1

        # 2. Dynamic Attribute Layer
        attr_labels = {
            "legal_form": "법인 형태 (Legal Form)",
            "entity_type": "공공 분류 / 기관 유형 (Entity Type)",
            "hours_or_headcount": "주간 근무시간 / 모집인원 (Work Hours / Headcount)",
            "salary_min": "급여 최소 (Salary Min)",
            "salary_max": "급여 최대 (Salary Max)",
            "currency": "통화 (Currency)",
            "location": "근무지 / 소재지 (Location)",
            "education_level": "최소 학력 요건 (Education Requirement)",
            "role_equiv": "IT경영/도메인 맞춤 직무 매칭 (Role Equiv)",
            "description": "직무 설명 요약 (Description)",
            "award_amount": "연방조달 계약금액 (Award Amount)",
            "awarding_agency": "조달 발주기관 (Awarding Agency)",
            "assets_usd": "총자산 (Assets USD)",
        }
        for attr in attrs:
            header = attr_labels.get(attr, f"속성 ({attr})")
            letter = cls.get_column_letter(col_idx)
            align = "right" if "salary" in attr or "amount" in attr or "assets" in attr else ("center" if attr in ("currency", "legal_form") else "left")
            specs.append(DynamicColumnSpec(col_idx, header, attr, letter, align))
            col_idx += 1

        # 3. Action & Provenance Layer
        raw_url_col_letter = cls.get_column_letter(col_idx)  # The column where raw posting_url resides

        for header, key, align in cls.PROVENANCE_HEADERS:
            letter = cls.get_column_letter(col_idx)
            if key == "hyperlink":
                specs.append(DynamicColumnSpec(
                    index=col_idx,
                    header=header,
                    field_key=key,
                    column_letter=letter,
                    alignment=align,
                    is_hyperlink=True,
                    formula_template=f'=HYPERLINK({raw_url_col_letter}{{row}}, "공고 확인 ↗")',
                ))
            elif key == "freshness":
                specs.append(DynamicColumnSpec(
                    index=col_idx,
                    header=header,
                    field_key=key,
                    column_letter=letter,
                    alignment=align,
                    is_freshness=True,
                ))
            else:
                specs.append(DynamicColumnSpec(
                    index=col_idx,
                    header=header,
                    field_key=key,
                    column_letter=letter,
                    alignment=align,
                ))
            col_idx += 1

        return specs


