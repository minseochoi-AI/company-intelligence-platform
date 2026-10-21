"""Canonical responsibility owner; migrated from src/company_intel/classification.py."""

from __future__ import annotations
from cil_contracts.reports import DynamicColumnSpec


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
    def compile_schema(
        cls, dynamic_attributes: list[str] | None = None
    ) -> list[DynamicColumnSpec]:
        """Compile complete ordered list of DynamicColumnSpec with dynamic hyperlink target indexing."""
        attrs = dynamic_attributes or [
            "legal_form",
            "entity_type",
            "hours_or_headcount",
            "salary_min",
            "salary_max",
            "currency",
            "location",
            "education_level",
            "role_equiv",
            "description",
        ]
        specs: list[DynamicColumnSpec] = []
        col_idx = 1
        for header, key, align in cls.CORE_HEADERS:
            letter = cls.get_column_letter(col_idx)
            specs.append(DynamicColumnSpec(col_idx, header, key, letter, align))
            col_idx += 1
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
            align = (
                "right"
                if "salary" in attr or "amount" in attr or "assets" in attr
                else "center"
                if attr in ("currency", "legal_form")
                else "left"
            )
            specs.append(DynamicColumnSpec(col_idx, header, attr, letter, align))
            col_idx += 1
        raw_url_col_letter = cls.get_column_letter(col_idx)
        for header, key, align in cls.PROVENANCE_HEADERS:
            letter = cls.get_column_letter(col_idx)
            if key == "hyperlink":
                specs.append(
                    DynamicColumnSpec(
                        index=col_idx,
                        header=header,
                        field_key=key,
                        column_letter=letter,
                        alignment=align,
                        is_hyperlink=True,
                        formula_template=f'=HYPERLINK({raw_url_col_letter}{{row}}, "공고 확인 ↗")',
                    )
                )
            elif key == "freshness":
                specs.append(
                    DynamicColumnSpec(
                        index=col_idx,
                        header=header,
                        field_key=key,
                        column_letter=letter,
                        alignment=align,
                        is_freshness=True,
                    )
                )
            else:
                specs.append(
                    DynamicColumnSpec(
                        index=col_idx,
                        header=header,
                        field_key=key,
                        column_letter=letter,
                        alignment=align,
                    )
                )
            col_idx += 1
        return specs
