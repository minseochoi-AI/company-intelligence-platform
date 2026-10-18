"""Provider-native taxonomy extraction for company and posting records.

The module records what a provider actually says.  It does not try to turn a
legal-form code into ownership, an ATS department into an industry, or a
listing venue into a current market status.  Any future crosswalk belongs in a
separate, explicitly versioned mapping with its own evidence.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from .models import TaxonomyFact
from .normalization import resolve_field_path


TAXONOMY_AXES = (
    "ownership_sector",
    "public_institution_type",
    "legal_form",
    "industry",
    "market_status",
    "posting_organization_unit",
    # Provider-native axes that must not be silently promoted to one of the
    # common axes above.
    "legal_entity_status",
    "entity_category",
    "filing_entity_type",
    "listing_venue",
    "public_institution_group",
    "public_business_name",
    "public_employment_type_code",
    "posting_office",
    "occupation_code",
    "occupation_pivot",
    "ncs_code",
)

NCS_TO_ISCO_MAP: dict[str, str] = {
    # 01 사업관리 / 프로젝트 관리
    "010101": "2421",  # 경영전략/사업기획 -> ISCO 2421 (Management/Org Analysts)
    "010102": "2421",  # 프로젝트관리 -> ISCO 2421
    "010201": "2141",  # 품질관리 -> ISCO 2141 (Industrial & Production Engineers)
    
    # 02 경영·회계·사무 / 20 정보통신 IT (공통 호환)
    "020101": "2511",  # 빅데이터기획/분석 -> ISCO 2511 (Systems/Data Analysts)
    "020102": "2511",  # AI서비스기획 -> ISCO 2511
    "020103": "2512",  # 정보기술전략/아키텍처 -> ISCO 2512 (Software Developers)
    "020201": "2512",  # 응용SW개발 -> ISCO 2512
    "020202": "2512",  # 시스템SW개발 -> ISCO 2512
    "020203": "2513",  # UI/UX개발/퍼블리싱 -> ISCO 2513 (Web & Multimedia Developers)
    "020301": "2521",  # 데이터베이스엔지니어링 -> ISCO 2521 (Database Designers & DBAs)
    "020401": "2522",  # 네트워크엔지니어링 -> ISCO 2522 (Systems Administrators)
    "020402": "2523",  # 통신인프라엔지니어링 -> ISCO 2523 (Computer Network Professionals)
    "020501": "2529",  # 정보보안엔지니어링 -> ISCO 2529 (Database & Network Professionals NEC)
    
    # 02 경영기획·인사·회계
    "020110": "2421",  # 경영기획 -> ISCO 2421
    "020210": "2423",  # 인사·조직관리 -> ISCO 2423 (Personnel and Careers Professionals)
    "020310": "2423",  # 총무·노무관리 -> ISCO 2423
    "020410": "2411",  # 회계·재무·세무 -> ISCO 2411 (Accountants & Tax)

    # 03 금융·보험
    "030101": "2412",  # 금융·투자자문/자산운용 -> ISCO 2412 (Financial & Investment Advisers)
    "030102": "2413",  # 금융상품개발/리스크관리 -> ISCO 2413 (Financial Analysts)
    "030201": "2413",  # 보험계리·위험관리 -> ISCO 2413

    # 04 교육·연구·자연/사회과학
    "040101": "2111",  # 물리/천문/자연과학 연구 -> ISCO 2111 (Physicists and Astronomers)
    "040102": "2113",  # 화학/신소재 연구 -> ISCO 2113 (Chemists)
    "040103": "2131",  # 생명과학/바이오 연구 -> ISCO 2131 (Biologists, Botanists, Zoologists)
    "040201": "2310",  # 대학교수/고등교육 -> ISCO 2310 (University & Higher Education Teachers)

    # 05 법률·보안·행정
    "050101": "2611",  # 법률·변호·송무 -> ISCO 2611 (Lawyers)
    "050102": "2619",  # 변리·지식재산권 -> ISCO 2619 (Legal Professionals NEC)

    # 06 보건·의료·제약
    "060101": "2211",  # 일반의사 -> ISCO 2211 (Generalist Medical Practitioners)
    "060102": "2212",  # 전문의사 -> ISCO 2212 (Specialist Medical Practitioners)
    "060201": "2221",  # 간호사 -> ISCO 2221 (Nursing Professionals)
    "060301": "2262",  # 약사/제약임상 -> ISCO 2262 (Pharmacists)

    # 08 문화·예술·디자인·방송
    "080101": "2166",  # 시각·그래픽디자인 -> ISCO 2166 (Graphic and Multimedia Designers)
    "080102": "2163",  # 제품·패션디자인 -> ISCO 2163 (Product and Garment Designers)
    "080201": "2642",  # 방송제작·기자·PD -> ISCO 2642 (Journalists)

    # 10 영업·마케팅
    "100101": "2433",  # 기술영업/B2B영업 -> ISCO 2433 (Technical and Medical Sales)
    "100201": "2431",  # 마케팅전략·시장조사 -> ISCO 2431 (Advertising & Marketing Professionals)

    # 14 건설·건축·토목
    "140101": "2161",  # 건축설계/건축가 -> ISCO 2161 (Building Architects)
    "140201": "2142",  # 토목구조/인프라공학 -> ISCO 2142 (Civil Engineers)

    # 15 기계·자동차·로봇
    "150101": "2144",  # 기계설계/메카트로닉스 -> ISCO 2144 (Mechanical Engineers)
    "150201": "2144",  # 자동차/모빌리티공학 -> ISCO 2144

    # 16 재료·금속
    "160101": "2146",  # 신소재/금속공학 -> ISCO 2146 (Mining Engineers, Metallurgists)

    # 17 화학·바이오·제약공학
    "170101": "2145",  # 화학공학/정유배터리 -> ISCO 2145 (Chemical Engineers)
    "170201": "2131",  # 바이오공학/의약바이오 -> ISCO 2131

    # 19 전기·전자·반도체
    "190101": "2151",  # 전기공학/전력시스템 -> ISCO 2151 (Electrical Engineers)
    "190201": "2152",  # 전자회로/반도체설계 -> ISCO 2152 (Electronics Engineers)
    "190202": "2153",  # 통신시스템공학 -> ISCO 2153 (Telecommunications Engineers)

    # 20 정보통신 공식코드 계열
    "200101": "2511",  # IT기획/빅데이터 -> ISCO 2511
    "200201": "2512",  # 응용SW엔지니어링 -> ISCO 2512
    "200301": "2521",  # 데이터베이스구축 -> ISCO 2521
    "200401": "2522",  # 네트워크엔지니어링 -> ISCO 2522
    "200501": "2529",  # 정보보안엔지니어링 -> ISCO 2529

    # 23 환경·에너지·안전
    "230101": "2143",  # 환경공학/탄소중립 -> ISCO 2143 (Environmental Engineers)
    "230201": "2263",  # 산업안전/보건관리 -> ISCO 2263 (Environmental & Occupational Health)
}

TITLE_TO_ISCO_PATTERNS: tuple[tuple[tuple[str, ...], str], ...] = (
    # IT & 데이터 & 엔지니어링
    (("data analyst", "data scientist", "bi analyst", "데이터 분석", "빅데이터 분석", "analytik dat"), "2511"),
    (("software engineer", "developer", "backend", "frontend", "full stack", "개발자", "프로그래머", "vývojář", "programátor"), "2512"),
    (("web developer", "multimedia", "웹개발", "퍼블리셔", "webový"), "2513"),
    (("database administrator", "dba", "data engineer", "데이터 엔지니어", "데이터베이스", "databáz"), "2521"),
    (("devops", "sre", "infrastructure", "systems administrator", "시스템 엔지니어", "인프라", "správce systém"), "2522"),
    (("network engineer", "네트워크", "síťový"), "2523"),
    (("security engineer", "cybersecurity", "정보보안", "보안", "bezpečnost"), "2529"),
    
    # 기획·프로덕트·경영
    (("product manager", "project manager", "scrum master", "기획자", "pm", "po", "경영기획", "analytik řízení"), "2421"),
    (("hr manager", "recruiter", "talent acquisition", "인사", "채용", "노무", "personalista"), "2423"),
    (("accountant", "accounting", "tax", "회계", "세무", "재무", "účetní"), "2411"),
    (("financial analyst", "investment", "portfolio", "금융", "투자", "자산운용", "finanční analytik"), "2412"),
    
    # 마케팅·영업
    (("marketing", "growth hacker", "seo", "마케팅", "홍보", "marketingový"), "2431"),
    (("sales engineer", "account executive", "b2b sales", "기술영업", "해외영업", "영업", "obchodní"), "2433"),
    
    # 연구·자연과학·의료
    (("research scientist", "researcher", "연구원", "연구개발", "r&d", "výzkumný"), "2111"),
    (("chemist", "화학", "배터리 연구", "chemik"), "2113"),
    (("biologist", "biotech", "바이오", "생명과학", "biolog"), "2131"),
    (("physician", "doctor", "의사", "전문의", "lékař"), "2211"),
    (("pharmacist", "clinical", "약사", "임상", "lékárník"), "2262"),
    (("nurse", "간호사", "zdravotní sestra"), "2221"),
    
    # 디자인·미디어
    (("graphic designer", "ui designer", "ux designer", "디자이너", "시각디자인", "grafik"), "2166"),
    (("product designer", "industrial designer", "제품디자인", "패션디자인", "návrhář"), "2163"),
    
    # 하드웨어·전자·기계·건설
    (("mechanical engineer", "기계설계", "기계엔지니어", "strojní inženýr"), "2144"),
    (("electrical engineer", "전기엔지니어", "전력", "elektroinženýr"), "2151"),
    (("electronics engineer", "semiconductor", "전자엔지니어", "반도체설계", "elektronik"), "2152"),
    (("telecommunications engineer", "통신엔지니어", "telekomunikační"), "2153"),
    (("chemical engineer", "화학공학", "공정설계", "chemický inženýr"), "2145"),
    (("civil engineer", "토목", "토목엔지니어", "stavební inženýr"), "2142"),
    (("architect", "건축가", "건축설계", "architekt"), "2161"),
    (("environmental engineer", "환경엔지니어", "탄소중립", "environmentální"), "2143"),
)


def resolve_title_to_isco(title: str | None) -> str | None:
    if not title:
        return None
    lowered = title.casefold()
    for patterns, isco in TITLE_TO_ISCO_PATTERNS:
        if any(pat in lowered for pat in patterns):
            return isco
    return None


def _first(record: dict[str, Any], *paths: str) -> tuple[str | None, Any]:
    for path in paths:
        value = resolve_field_path(record, path)
        if value not in (None, "", [], {}):
            return path, value
    return None, None


def _values(value: Any) -> tuple[Any, ...]:
    if isinstance(value, list):
        return tuple(item for item in value if item not in (None, "", [], {}))
    return (value,) if value not in (None, "", [], {}) else ()


def _native_value(value: Any) -> str | None:
    """Extract an identifier from a provider value without translating it."""

    if isinstance(value, dict):
        for key in ("id", "code", "kod", "value", "name", "nazev"):
            nested = value.get(key)
            if nested not in (None, ""):
                return str(nested)
        return None
    return str(value).strip() or None


def _entity_id(provider: str, record: dict[str, Any], explicit: str | None) -> str | None:
    if explicit:
        return explicit
    existing = record.get("entity_id")
    if existing not in (None, ""):
        return str(existing)
    identifiers = {
        "ares": ("ico", "ICO"),
        "gleif": ("id", "data.0.id"),
        "sec": ("cik", "CIK"),
        "alioplus": ("apbaId", "apba_id"),
    }
    prefix = {"ares": "ICO", "gleif": "LEI", "sec": "CIK", "alioplus": "ALIO"}
    path, value = _first(record, *identifiers.get(provider, ()))
    native = _native_value(value)
    return f"{prefix[provider]}:{native}" if path and native and provider in prefix else None


def _add(
    facts: list[TaxonomyFact],
    *,
    semantic_field: str,
    value: Any,
    namespace: str,
    provider: str,
    raw_field: str,
    raw_value: Any,
    entity_id: str | None,
    source_record_id: str | None,
    evidence_status: str = "observed",
    filterability: str = "filterable",
    sortability: str = "not_sortable",
) -> None:
    native = _native_value(value)
    if native is None:
        return
    fact = TaxonomyFact(
        semantic_field=semantic_field,
        value=native,
        namespace=namespace,
        provider=provider,
        raw_field=raw_field,
        raw_value=raw_value,
        entity_id=entity_id,
        source_record_id=source_record_id,
        evidence_status=evidence_status,
        filterability=filterability,
        sortability=sortability,
    )
    if fact not in facts:
        facts.append(fact)


def _add_many(
    facts: list[TaxonomyFact],
    *,
    semantic_field: str,
    field_path: str | None,
    value: Any,
    namespace: str,
    provider: str,
    entity_id: str | None,
    source_record_id: str | None,
    evidence_status: str = "observed",
    filterability: str = "filterable",
) -> None:
    if field_path is None:
        return
    for item in _values(value):
        _add(
            facts,
            semantic_field=semantic_field,
            value=item,
            namespace=namespace,
            provider=provider,
            raw_field=field_path,
            raw_value=item,
            entity_id=entity_id,
            source_record_id=source_record_id,
            evidence_status=evidence_status,
            filterability=filterability,
        )


def _ares_facts(record: dict[str, Any], facts: list[TaxonomyFact], entity_id: str | None, source_record_id: str | None) -> None:
    form_path, form = _first(record, "pravniForma", "pravniFormaRos", "dalsiUdaje.0.pravniForma", "dalsiUdaje.0.pravniFormaRos")
    _add_many(
        facts, semantic_field="legal_form", field_path=form_path, value=form,
        namespace="ARES:pravniForma", provider="ares", entity_id=entity_id, source_record_id=source_record_id,
    )
    nace_path, nace = _first(record, "czNace", "czNace2008", "dalsiUdaje.0.czNace", "dalsiUdaje.0.czNace2008")
    _add_many(
        facts, semantic_field="industry", field_path=nace_path, value=nace,
        namespace="CZ-NACE", provider="ares", entity_id=entity_id, source_record_id=source_record_id,
    )


def _gleif_facts(record: dict[str, Any], facts: list[TaxonomyFact], entity_id: str | None, source_record_id: str | None) -> None:
    form_path, form = _first(record, "attributes.entity.legalForm.id", "entity.legalForm.id", "legalForm.id", "data.0.attributes.entity.legalForm.id")
    _add_many(
        facts, semantic_field="legal_form", field_path=form_path, value=form,
        namespace="GLEIF:ELF", provider="gleif", entity_id=entity_id, source_record_id=source_record_id,
    )
    status_path, status = _first(record, "attributes.entity.status", "entity.status", "status", "data.0.attributes.entity.status")
    _add_many(
        facts, semantic_field="legal_entity_status", field_path=status_path, value=status,
        namespace="GLEIF:entity.status", provider="gleif", entity_id=entity_id, source_record_id=source_record_id,
        filterability="display_only",
    )
    category_path, category = _first(record, "attributes.entity.category", "entity.category", "category", "data.0.attributes.entity.category")
    _add_many(
        facts, semantic_field="entity_category", field_path=category_path, value=category,
        namespace="GLEIF:entity.category", provider="gleif", entity_id=entity_id, source_record_id=source_record_id,
        filterability="display_only",
    )


def _sec_facts(record: dict[str, Any], facts: list[TaxonomyFact], entity_id: str | None, source_record_id: str | None) -> None:
    sic_path, sic = _first(record, "sic", "sic_code")
    _add_many(
        facts, semantic_field="industry", field_path=sic_path, value=sic,
        namespace="SEC:SIC", provider="sec", entity_id=entity_id, source_record_id=source_record_id,
    )
    entity_type_path, entity_type = _first(record, "entityType", "entity_type")
    _add_many(
        facts, semantic_field="filing_entity_type", field_path=entity_type_path, value=entity_type,
        namespace="SEC:entityType", provider="sec", entity_id=entity_id, source_record_id=source_record_id,
        filterability="display_only",
    )
    exchange_path, exchange = _first(record, "exchanges", "exchange")
    _add_many(
        facts, semantic_field="listing_venue", field_path=exchange_path, value=exchange,
        namespace="SEC:exchange", provider="sec", entity_id=entity_id, source_record_id=source_record_id,
        filterability="display_only",
    )
    # Only an explicitly named market status becomes that axis.  An exchange
    # and a filing entity type are intentionally not substitutes for it.
    market_path, market = _first(record, "marketStatus", "market_status")
    _add_many(
        facts, semantic_field="market_status", field_path=market_path, value=market,
        namespace="SEC:marketStatus", provider="sec", entity_id=entity_id, source_record_id=source_record_id,
    )


def _alio_facts(record: dict[str, Any], facts: list[TaxonomyFact], entity_id: str | None, source_record_id: str | None) -> None:
    # ALIO Plus is an official public-institution context source.  It supports
    # a contextual sector fact but does not establish a legal form or industry.
    _add(
        facts, semantic_field="ownership_sector", value="public_institution",
        namespace="ALIO:source_scope", provider="alioplus", raw_field="provider_scope",
        raw_value="public_institution_context", entity_id=entity_id, source_record_id=source_record_id,
        evidence_status="provider_context", filterability="display_only",
    )
    type_path, institution_type = _first(record, "apbaTypeNa", "apba_type_name")
    _add_many(
        facts, semantic_field="public_institution_type", field_path=type_path, value=institution_type,
        namespace="ALIO:apbaTypeNa", provider="alioplus", entity_id=entity_id, source_record_id=source_record_id,
    )
    group_path, group = _first(record, "apbaGb", "apba_group")
    _add_many(
        facts, semantic_field="public_institution_group", field_path=group_path, value=group,
        namespace="ALIO:apbaGb", provider="alioplus", entity_id=entity_id, source_record_id=source_record_id,
        filterability="display_only",
    )
    business_path, business = _first(record, "bsnNa", "business_name")
    _add_many(
        facts, semantic_field="public_business_name", field_path=business_path, value=business,
        namespace="ALIO:bsnNa", provider="alioplus", entity_id=entity_id, source_record_id=source_record_id,
        filterability="display_only",
    )


def _mpm_facts(record: dict[str, Any], facts: list[TaxonomyFact], entity_id: str | None, source_record_id: str | None) -> None:
    _add(
        facts, semantic_field="ownership_sector", value="public_sector_employer",
        namespace="MPM:source_scope", provider="mpm_public_employment", raw_field="provider_scope",
        raw_value="public_employment_listing", entity_id=entity_id, source_record_id=source_record_id,
        evidence_status="provider_context", filterability="display_only",
    )
    organization_path, organization = _first(record, "institution_name", "insttname", "institutionName")
    _add_many(
        facts, semantic_field="posting_organization_unit", field_path=organization_path, value=organization,
        namespace="MPM:institution_name", provider="mpm_public_employment", entity_id=entity_id,
        source_record_id=source_record_id, evidence_status="unresolved_identity", filterability="display_only",
    )
    for path in ("type01", "type02", "posting_type"):
        value = resolve_field_path(record, path)
        _add_many(
            facts, semantic_field="public_employment_type_code", field_path=path, value=value,
            namespace=f"MPM:{path}", provider="mpm_public_employment", entity_id=entity_id,
            source_record_id=source_record_id, evidence_status="codebook_unverified", filterability="display_only",
        )
    title = record.get("title")
    isco_pivot = resolve_title_to_isco(title)
    if isco_pivot:
        _add(
            facts, semantic_field="occupation_pivot", value=isco_pivot,
            namespace="ISCO:08", provider="mpm_public_employment", raw_field="title",
            raw_value=title, entity_id=entity_id, source_record_id=source_record_id,
        )


def _mpsv_facts(record: dict[str, Any], facts: list[TaxonomyFact], entity_id: str | None, source_record_id: str | None) -> None:
    """Keep public-administration context separate from ARES legal form."""

    if record.get("statniSpravaSamosprava") is True:
        _add(
            facts, semantic_field="ownership_sector", value="public_administration_context",
            namespace="MPSV:statniSpravaSamosprava", provider="mpsv_cz", raw_field="statniSpravaSamosprava",
            raw_value=True, entity_id=entity_id, source_record_id=source_record_id,
            evidence_status="posting_context", filterability="display_only",
        )
    employer = record.get("zamestnavatel") if isinstance(record.get("zamestnavatel"), dict) else {}
    ico = employer.get("ico")
    _add_many(
        facts, semantic_field="posting_organization_unit", field_path="zamestnavatel.nazev", value=employer.get("nazev"),
        namespace="MPSV:zamestnavatel", provider="mpsv_cz", entity_id=entity_id, source_record_id=source_record_id,
        evidence_status="posting_scope", filterability="display_only",
    )
    if ico:
        _add_many(
            facts, semantic_field="entity_category", field_path="zamestnavatel.ico", value=ico,
            namespace="MPSV:ICO", provider="mpsv_cz", entity_id=entity_id, source_record_id=source_record_id,
            evidence_status="identifier_observed", filterability="display_only",
        )
    cz_isco = record.get("profeseCzIsco")
    if isinstance(cz_isco, dict):
        cz_isco = cz_isco.get("id") or cz_isco.get("kod") or cz_isco.get("value")
    if cz_isco:
        cz_isco_str = str(cz_isco).strip()
        _add(
            facts, semantic_field="occupation_code", value=cz_isco_str,
            namespace="CZ-ISCO", provider="mpsv_cz", raw_field="profeseCzIsco",
            raw_value=cz_isco, entity_id=entity_id, source_record_id=source_record_id,
        )
        if len(cz_isco_str) >= 4:
            _add(
                facts, semantic_field="occupation_pivot", value=cz_isco_str[:4],
                namespace="ISCO:08", provider="mpsv_cz", raw_field="profeseCzIsco",
                raw_value=cz_isco_str[:4], entity_id=entity_id, source_record_id=source_record_id,
            )


def _worknet_facts(record: dict[str, Any], facts: list[TaxonomyFact], entity_id: str | None, source_record_id: str | None) -> None:
    job_cd = record.get("jobCd") or record.get("jobsCd") or record.get("job_cd") or record.get("jobs_cd")
    if job_cd:
        _add(
            facts, semantic_field="occupation_code", value=str(job_cd).strip(),
            namespace="KECO", provider="worknet", raw_field="jobCd",
            raw_value=job_cd, entity_id=entity_id, source_record_id=source_record_id,
        )
    ncs_cd = record.get("ncsClCd") or record.get("ncsSubCd") or record.get("ncs_cl_cd") or record.get("ncs_sub_cd")
    if ncs_cd:
        ncs_str = str(ncs_cd).strip()
        _add(
            facts, semantic_field="ncs_code", value=ncs_str,
            namespace="NCS", provider="worknet", raw_field="ncsClCd",
            raw_value=ncs_cd, entity_id=entity_id, source_record_id=source_record_id,
        )
        isco = NCS_TO_ISCO_MAP.get(ncs_str[:6]) or NCS_TO_ISCO_MAP.get(ncs_str[:4])
        if isco:
            _add(
                facts, semantic_field="occupation_pivot", value=isco,
                namespace="ISCO:08", provider="worknet", raw_field="ncsClCd",
                raw_value=isco, entity_id=entity_id, source_record_id=source_record_id,
            )


def _hrdkorea_facts(record: dict[str, Any], facts: list[TaxonomyFact], entity_id: str | None, source_record_id: str | None) -> None:
    ncs_sub = record.get("ncsSubCd") or record.get("subCd") or record.get("ncs_sub_cd")
    if ncs_sub:
        ncs_str = str(ncs_sub).strip()
        _add(
            facts, semantic_field="ncs_code", value=ncs_str,
            namespace="NCS", provider="hrdkorea", raw_field="ncsSubCd",
            raw_value=ncs_sub, entity_id=entity_id, source_record_id=source_record_id,
        )
        isco = NCS_TO_ISCO_MAP.get(ncs_str[:6]) or NCS_TO_ISCO_MAP.get(ncs_str[:4])
        if isco:
            _add(
                facts, semantic_field="occupation_pivot", value=isco,
                namespace="ISCO:08", provider="hrdkorea", raw_field="ncsSubCd",
                raw_value=isco, entity_id=entity_id, source_record_id=source_record_id,
            )


def normalize_alio_taxonomy(record: Mapping[str, Any]) -> tuple[TaxonomyFact, ...]:
    return taxonomy_facts_from_record("alioplus", dict(record))


def normalize_ares_taxonomy(record: Mapping[str, Any]) -> tuple[TaxonomyFact, ...]:
    return taxonomy_facts_from_record("ares", dict(record))


def link_status(record: Mapping[str, Any]) -> str:
    value = str(record.get("identity_link_status") or record.get("identity_status") or "unresolved")
    return value if value in {"linked", "candidate", "unresolved", "conflict"} else "unresolved"


def _ats_facts(provider: str, record: dict[str, Any], facts: list[TaxonomyFact], entity_id: str | None, source_record_id: str | None) -> None:
    if provider == "greenhouse":
        departments = resolve_field_path(record, "departments")
        if departments is not None:
            for department in _values(departments):
                name = department.get("name") if isinstance(department, dict) else department
                _add(
                    facts, semantic_field="posting_organization_unit", value=name,
                    namespace="ATS:GREENHOUSE:department", provider=provider, raw_field="departments",
                    raw_value=department, entity_id=entity_id, source_record_id=source_record_id,
                    evidence_status="posting_scope",
                )
        offices = resolve_field_path(record, "offices")
        if offices is not None:
            for office in _values(offices):
                location = office.get("location") if isinstance(office, dict) else office
                _add(
                    facts, semantic_field="posting_office", value=location,
                    namespace="ATS:GREENHOUSE:office", provider=provider, raw_field="offices",
                    raw_value=office, entity_id=entity_id, source_record_id=source_record_id,
                    evidence_status="posting_scope",
                )
    elif provider == "lever":
        for path in ("categories.team", "categories.department"):
            value = resolve_field_path(record, path)
            _add_many(
                facts, semantic_field="posting_organization_unit", field_path=path, value=value,
                namespace=f"ATS:LEVER:{path.rsplit('.', 1)[-1]}", provider=provider, entity_id=entity_id,
                source_record_id=source_record_id, evidence_status="posting_scope",
            )
    title = record.get("title") or record.get("text")
    isco_pivot = resolve_title_to_isco(title)
    if isco_pivot:
        _add(
            facts, semantic_field="occupation_pivot", value=isco_pivot,
            namespace="ISCO:08", provider=provider, raw_field="title",
            raw_value=title, entity_id=entity_id, source_record_id=source_record_id,
        )


def taxonomy_facts_from_record(
    provider: str,
    record: dict[str, Any],
    *,
    entity_id: str | None = None,
    source_record_id: str | None = None,
) -> tuple[TaxonomyFact, ...]:
    """Extract facts from one saved provider record without joining entities.

    ``provider`` selects the source-specific contract.  Unknown providers
    return no facts rather than guessing at the meaning of similarly named
    fields.  This makes a newly added provider opt-in by design.
    """

    normalized_provider = provider.casefold().strip()
    aliases = {
        "mpm": "mpm_public_employment",
        "mpm_public_employment_list": "mpm_public_employment",
        "alio": "alioplus",
        "alio_plus": "alioplus",
        "worknet_job_duty": "worknet",
        "worknet_job_info": "worknet",
        "hrdkorea_ncs": "hrdkorea",
    }
    normalized_provider = aliases.get(normalized_provider, normalized_provider)
    if not isinstance(record, dict):
        return ()

    resolved_entity = _entity_id(normalized_provider, record, entity_id)
    resolved_record_id = source_record_id or _native_value(
        resolve_field_path(record, "id")
        or resolve_field_path(record, "idx")
        or resolve_field_path(record, "posting_id")
    )
    facts: list[TaxonomyFact] = []
    if normalized_provider == "ares":
        _ares_facts(record, facts, resolved_entity, resolved_record_id)
    elif normalized_provider == "gleif":
        _gleif_facts(record, facts, resolved_entity, resolved_record_id)
    elif normalized_provider == "sec":
        _sec_facts(record, facts, resolved_entity, resolved_record_id)
    elif normalized_provider == "alioplus":
        _alio_facts(record, facts, resolved_entity, resolved_record_id)
    elif normalized_provider == "mpm_public_employment":
        _mpm_facts(record, facts, resolved_entity, resolved_record_id)
    elif normalized_provider in {"mpsv", "mpsv_cz"}:
        _mpsv_facts(record, facts, resolved_entity, resolved_record_id)
    elif normalized_provider in {"greenhouse", "lever"}:
        _ats_facts(normalized_provider, record, facts, resolved_entity, resolved_record_id)
    elif normalized_provider == "worknet":
        _worknet_facts(record, facts, resolved_entity, resolved_record_id)
    elif normalized_provider == "hrdkorea":
        _hrdkorea_facts(record, facts, resolved_entity, resolved_record_id)
    return tuple(facts)


def taxonomy_facts_from_records(provider: str, records: Iterable[dict[str, Any]]) -> tuple[TaxonomyFact, ...]:
    """Convenience helper that keeps each source record separate."""

    return tuple(fact for record in records for fact in taxonomy_facts_from_record(provider, record))
