"""Evidence-aware terminal selection for the composable ``company-intel`` CLI.

The normal subcommands remain the machine-friendly contract.  This module only
compiles a user selection into those same arguments; it never refreshes a
provider or invents a filter value that is absent from a saved snapshot.
"""

from __future__ import annotations

import json
import math
import sys
from collections.abc import Sequence
from dataclasses import asdict, dataclass, is_dataclass
from pathlib import Path
from typing import Any, Protocol

from .category_tree import SelectionSession, branches_for_selection, preview_selection, roots
from .cli_guide import korean_command, korean_option
from .facets import build_job_facets, build_taxonomy_facets
from .job_search import normalize_provider_payloads


@dataclass(frozen=True)
class MenuOption:
    value: str
    label: str
    detail: str = ""
    enabled: bool = True


@dataclass(frozen=True)
class InteractiveRequest:
    """A reversible, inspectable command compiled from terminal selections."""

    command: str
    argv: tuple[str, ...]
    profile: dict[str, Any]
    notes: tuple[str, ...] = ()
    runnable: bool = True

    def as_dict(self) -> dict[str, Any]:
        return {
            "command": self.command,
            "명령": korean_command(self.command)
            if self.command
            in {
                "provider-status",
                "job-search",
                "company-search",
                "screen",
                "timeline",
                "valuation",
                "ai-event",
                "explain",
                "export",
                "current-jobs",
                "job-trends",
            }
            else self.command,
            "argv": list(self.argv),
            "profile": self.profile,
            "안내": list(self.notes),
            "notes": list(self.notes),
            "runnable": self.runnable,
        }


class Selector(Protocol):
    def select(
        self, prompt_id: str, title: str, options: Sequence[MenuOption], *, multiple: bool = False
    ) -> list[str]: ...

    def text(self, prompt_id: str, title: str, *, required: bool = False, default: str = "") -> str: ...


class ScriptedSelector:
    """Non-TTY adapter used by tests and repeatable saved interactive scripts."""

    def __init__(self, answers: dict[str, Any]) -> None:
        self.answers = answers

    def select(
        self, prompt_id: str, title: str, options: Sequence[MenuOption], *, multiple: bool = False
    ) -> list[str]:
        available = {option.value: option for option in options}
        value = self.answers.get(prompt_id, [])
        selected = [value] if isinstance(value, str) else list(value or [])
        if not multiple and len(selected) > 1:
            selected = selected[:1]
        invalid = [item for item in selected if item not in available or not available[item].enabled]
        if invalid:
            raise ValueError(
                f"{prompt_id}: 지원하지 않거나 선택할 수 없는 값입니다: {', '.join(str(item) for item in invalid)}"
            )
        return [str(item) for item in selected]

    def text(self, prompt_id: str, title: str, *, required: bool = False, default: str = "") -> str:
        value = str(self.answers.get(prompt_id, default)).strip()
        if required and not value:
            raise ValueError(f"{prompt_id}: 값을 입력해야 합니다.")
        return value


class ArrowMenu:
    """Minimal standard-library arrow/space/Enter menu.

    ``curses`` deliberately remains an adapter rather than product logic, so
    the same workflow can be tested through :class:`ScriptedSelector`.
    """

    def select(
        self, prompt_id: str, title: str, options: Sequence[MenuOption], *, multiple: bool = False
    ) -> list[str]:
        if not options:
            return []
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            raise RuntimeError(
                "화살표 선택에는 TTY가 필요합니다. 저장한 선택에는 --선택-스크립트(--script)를 사용하세요."
            )
        import curses

        def render(screen: Any) -> list[str]:
            curses.curs_set(0)
            index = next((number for number, option in enumerate(options) if option.enabled), 0)
            selected: set[str] = set()
            while True:
                screen.erase()
                height, width = screen.getmaxyx()
                screen.addnstr(0, 0, title, max(1, width - 1), curses.A_BOLD)
                screen.addnstr(1, 0, "↑/↓ 이동 · Space 선택/해제 · Enter 확정 · Esc 취소", max(1, width - 1))
                for number, option in enumerate(options[: max(1, height - 3)]):
                    marker = "●" if option.value in selected else "○"
                    cursor = ">" if number == index else " "
                    suffix = f" — {option.detail}" if option.detail else ""
                    style = curses.A_REVERSE if number == index else curses.A_NORMAL
                    if not option.enabled:
                        style |= curses.A_DIM
                    screen.addnstr(
                        number + 3,
                        0,
                        f"{cursor} {marker if multiple else ' '} {option.label}{suffix}",
                        max(1, width - 1),
                        style,
                    )
                key = screen.getch()
                if key in (curses.KEY_UP, ord("k")):
                    for _ in options:
                        index = (index - 1) % len(options)
                        if options[index].enabled:
                            break
                elif key in (curses.KEY_DOWN, ord("j")):
                    for _ in options:
                        index = (index + 1) % len(options)
                        if options[index].enabled:
                            break
                elif key == ord(" ") and multiple and options[index].enabled:
                    value = options[index].value
                    if value in selected:
                        selected.remove(value)
                    else:
                        selected.add(value)
                elif key in (curses.KEY_ENTER, ord("\n"), ord("\r")):
                    if multiple:
                        return [option.value for option in options if option.value in selected]
                    return [options[index].value] if options[index].enabled else []
                elif key in (27, ord("q")):
                    return []

        return curses.wrapper(render)

    def text(self, prompt_id: str, title: str, *, required: bool = False, default: str = "") -> str:
        prompt = f"{title}{f' [{default}]' if default else ''}: "
        value = input(prompt).strip() or default
        if required and not value:
            raise ValueError(f"{prompt_id}: 값을 입력해야 합니다.")
        return value


TOP_LEVEL = (
    MenuOption("readiness", "데이터 준비 상태", "원천 상태·수집 범위·제한"),
    MenuOption("discovery", "채용·기업 탐색", "국가·직무·위치·조건·분류"),
    MenuOption("comparison", "기업 비교", "비교 가능한 집단과 순위"),
    MenuOption("analysis", "시간축·가치·AI 사건", "근거와 사전조건을 먼저 확인"),
    MenuOption("delivery", "설명·내보내기", "실행 근거와 CSV/XLSX"),
)

ACTION_OPTIONS = {
    "readiness": (MenuOption("provider-status", "원천 상태", "사용 가능한 필드와 활성화 조건"),),
    "discovery": (
        MenuOption("job-search", "채용공고 검색", "공고·요건·자격·근무 조건"),
        MenuOption("company-search", "기업/공공기관 검색", "법적 형태·소유·산업·시장 상태"),
    ),
    "comparison": (MenuOption("screen", "동료군 스크리너", "비교 가능 규격 집단만 정렬"),),
    "analysis": (
        MenuOption("timeline", "회사·시장·거시 시간축", "축별 시계열 규격 집단"),
        MenuOption("valuation", "가치 시나리오", "출처·시점·단위·통화 조건"),
        MenuOption("ai-event", "AI 사건 분석", "대조군이 없으면 연관성만 표시"),
    ),
    "delivery": (
        MenuOption("explain", "판단 근거 설명", "제외·검사 불가·원천 수집 범위"),
        MenuOption("export", "증거 스프레드시트", "CSV/XLSX와 실행 매니페스트"),
    ),
}


PURPOSE_ACTIONS = {
    "data_status": (MenuOption("provider-status", "원천 상태·스냅샷", "저장된 수집 범위와 최신성"),),
    "current_jobs": (MenuOption("current-jobs", "현재 채용 검색", "선택 스냅샷의 활성 공고만"),),
    "job_trends": (MenuOption("job-trends", "채용 동향", "호환되는 반복 스냅샷이 있을 때만"),),
    "organization_analysis": ACTION_OPTIONS["comparison"] + ACTION_OPTIONS["analysis"],
    "delivery": ACTION_OPTIONS["delivery"],
}


def _mapping(value: Any) -> dict[str, Any]:
    if hasattr(value, "as_dict"):
        return dict(value.as_dict())
    if is_dataclass(value):
        return asdict(value)
    return dict(value) if isinstance(value, dict) else {}


def _facet_options(
    facets: Sequence[Any], field: str, *, preserve_namespace: bool = False
) -> list[MenuOption]:
    """Render only source-supported facet values as selectable menu items.

    Taxonomy namespaces are part of a value's identity.  They are carried in
    the menu value (rather than merely the label), so choosing an ARES legal
    form cannot silently match a GLEIF code that happens to have the same
    spelling.
    """
    result: list[MenuOption] = []
    for facet in facets:
        value = _mapping(facet)
        semantic_field = str(value.get("semantic_field") or value.get("field") or "")
        if semantic_field != field:
            continue
        raw = str(value.get("normalized_value") or value.get("value") or "")
        if not raw:
            continue
        count = value.get("record_count", value.get("count", 0))
        providers = ", ".join(
            value.get("providers") or ([value["provider"]] if value.get("provider") else [])
        )
        status = str(value.get("filterability") or value.get("status") or "exact-select")
        reason = str(value.get("reason") or value.get("disabled_reason") or "")
        label = str(value.get("display_label") or value.get("label") or raw)
        namespace = str(value.get("vocabulary_namespace") or "").strip()
        selection_value = f"{namespace}:{raw}" if preserve_namespace and namespace else raw
        if preserve_namespace and namespace:
            label = f"{label} [{namespace}]"
        status_label = {
            "exact-select": "정확 선택 가능",
            "unavailable": "선택 불가",
            "display-only": "표시 전용",
            "forbidden": "사용 금지",
        }.get(status, status)
        detail = " · ".join(
            part
            for part in (
                f"{count}건" if count is not None else "",
                providers,
                status_label,
                f"사유: {reason}" if reason else "",
            )
            if part
        )
        result.append(
            MenuOption(
                selection_value, label, detail, status not in {"unavailable", "display-only", "forbidden"}
            )
        )
    return result


def _payload_paths(data_dir: Path) -> dict[str, Path]:
    aliases = {
        "greenhouse": ("greenhouse",),
        "lever": ("lever",),
        "mpm_public_employment": ("mpm", "public_employment", "gojobs"),
        "mpsv_cz": ("mpsv", "volna_mista"),
    }
    found: dict[str, Path] = {}
    for path in sorted(data_dir.rglob("*.json")) if data_dir.is_dir() else []:
        lowered = path.name.casefold()
        for provider, hints in aliases.items():
            if provider not in found and any(hint in lowered for hint in hints):
                found[provider] = path
    return found


def _load_payloads(paths: dict[str, Path]) -> dict[str, Any]:
    return {provider: json.loads(path.read_text(encoding="utf-8")) for provider, path in paths.items()}


def _split_terms(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _select_facets(
    selector: Selector,
    facets: Sequence[Any],
    field: str,
    title: str,
    *,
    multiple: bool = True,
    preserve_namespace: bool = False,
) -> list[str]:
    options = _facet_options(facets, field, preserve_namespace=preserve_namespace)
    return selector.select(f"job-{field}", title, options, multiple=multiple) if options else []


def _requirement_options(
    requirements: Sequence[dict[str, Any]], *, necessity: str, language_only: bool = False
) -> list[MenuOption]:
    """Expose observed atomic requirements without turning prose into facts."""

    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    for row in requirements:
        if row.get("necessity") != necessity:
            continue
        if language_only and row.get("requirement_kind") != "language":
            continue
        normalized = str(row.get("normalized_key") or "").strip()
        label = str(row.get("label") or "").strip()
        if not normalized or not label:
            continue
        key = (normalized, label)
        group = grouped.setdefault(key, {"count": 0, "providers": set(), "kind": row.get("requirement_kind")})
        group["count"] += 1
        group["providers"].add(str(row.get("provider") or "unknown"))
    return [
        MenuOption(
            normalized,
            label,
            " · ".join(
                (
                    f"{group['count']}건",
                    ", ".join(sorted(group["providers"])),
                    str(group["kind"] or "요건"),
                    {"required": "필수", "preferred": "우대"}.get(necessity, necessity),
                )
            ),
        )
        for (normalized, label), group in sorted(
            grouped.items(), key=lambda item: (-item[1]["count"], item[0][1].casefold())
        )
    ]


def _select_requirements(
    selector: Selector,
    requirements: Sequence[dict[str, Any]],
    prompt_id: str,
    title: str,
    *,
    necessity: str,
    language_only: bool = False,
) -> list[str]:
    options = _requirement_options(requirements, necessity=necessity, language_only=language_only)
    return selector.select(prompt_id, title, options, multiple=True) if options else []


def _optional_number(selector: Selector, prompt_id: str, title: str) -> float | None:
    raw = selector.text(prompt_id, title, required=False).strip()
    if not raw:
        return None
    try:
        value = float(raw)
    except ValueError as error:
        raise ValueError(f"{prompt_id}: 유한한 숫자를 입력하거나 비워 두세요.") from error
    if not math.isfinite(value):
        raise ValueError(f"{prompt_id}: 유한한 숫자를 입력하거나 비워 두세요.")
    return value


def _country_allocation(selector: Selector, countries: Sequence[str]) -> dict[str, int]:
    raw = selector.text(
        "job-country-allocation",
        "국가별 최대 결과 수 (예: US=10,KR=5; 비우면 제한 없음)",
        required=False,
    ).strip()
    if not raw:
        return {}
    allocation: dict[str, int] = {}
    for item in raw.split(","):
        country, marker, count = item.partition("=")
        if not marker or not country.strip() or not count.strip():
            raise ValueError("job-country-allocation: ISO=0 이상의 정수 형식을 사용하세요.")
        code = country.strip().upper()
        if code not in countries:
            raise ValueError("job-country-allocation: 위에서 선택한 국가만 지정할 수 있습니다.")
        try:
            value = int(count.strip())
        except ValueError as error:
            raise ValueError("job-country-allocation: ISO=0 이상의 정수 형식을 사용하세요.") from error
        if value < 0:
            raise ValueError("job-country-allocation: 결과 수는 음수일 수 없습니다.")
        allocation[code] = value
    return allocation


def build_job_search_request(
    selector: Selector, payload_paths: dict[str, Path], output: Path
) -> InteractiveRequest:
    payloads = _load_payloads(payload_paths)
    jobs, requirements, _sources = normalize_provider_payloads(payloads)
    facets = build_job_facets(jobs)
    countries = _select_facets(selector, facets, "country_code", "국가를 선택하세요", multiple=True)
    keywords = _split_terms(selector.text("job-keywords", "직무/키워드 (쉼표로 구분)", required=True))
    if not countries:
        raise ValueError("job-country_code: 저장된 원천에 있는 국가를 하나 이상 선택해야 합니다.")
    salary_signature = _select_facets(
        selector,
        facets,
        "salary_signature",
        "비교 가능한 구조화 연봉 형식 (통화/기간/기준)",
        multiple=False,
    )
    profile = {
        "countries": countries,
        "job_keywords": keywords,
        "occupations": _select_facets(
            selector, facets, "occupation_label", "직종/직무명 (저장된 공고 기준)", multiple=True
        ),
        "locations": _select_facets(selector, facets, "location", "근무 위치", multiple=True),
        "workplace_types": _select_facets(selector, facets, "workplace_type", "근무 방식", multiple=True),
        "employment_types": _select_facets(selector, facets, "employment_type", "고용 형태", multiple=True),
        "posting_languages": _select_facets(
            selector, facets, "posting_language", "공고 표시 언어", multiple=True
        ),
        "business_units": _select_facets(selector, facets, "business_unit", "공고 조직 단위", multiple=True),
        "industries": _select_facets(selector, facets, "industry", "산업 (원천에 있는 경우)", multiple=True),
        "company_types": _select_facets(
            selector, facets, "company_type", "고용주 유형 (검증된 경우)", multiple=True
        ),
        "required_requirement_terms": _select_requirements(
            selector,
            requirements,
            "job-required-requirements",
            "필수 요건 (저장된 공고 기준)",
            necessity="required",
        ),
        "preferred_requirement_terms": _select_requirements(
            selector,
            requirements,
            "job-preferred-requirements",
            "우대 요건 (정렬 가중치)",
            necessity="preferred",
        ),
        "required_languages": _select_requirements(
            selector,
            requirements,
            "job-required-languages",
            "지원자 필수 언어",
            necessity="required",
            language_only=True,
        ),
    }
    active_choice = selector.select(
        "job-active-only",
        "활성 공고만 포함할까요?",
        (MenuOption("true", "활성 공고만", "기본값"), MenuOption("false", "저장 시점의 비활성 공고도 포함")),
        multiple=False,
    )
    policy_choice = selector.select(
        "job-unknown-policy",
        "검사 불가 필드 처리",
        (
            MenuOption("report", "제외하고 검사 불가 표에 보고", "권장: 0건의 원인을 확인"),
            MenuOption("exclude", "제외", "기존 스크립트/API 호환값"),
            MenuOption("include", "결과에 포함", "검사 불가임을 유지한 채 포함"),
        ),
        multiple=False,
    )
    profile["active_only"] = (active_choice or ["true"])[0] == "true"
    profile["unknown_policy"] = (policy_choice or ["report"])[0]
    allocation = _country_allocation(selector, countries)
    if allocation:
        profile["country_allocation"] = allocation
    if salary_signature:
        currency, period, basis = salary_signature[0].split("/", 2)
        profile.update(
            {
                "salary_currency": currency,
                "salary_period": period,
                "salary_basis": basis,
            }
        )
        minimum = _optional_number(
            selector, "job-minimum-salary", "최소 연봉/급여 (선택한 형식의 숫자, 비우면 미사용)"
        )
        maximum = _optional_number(
            selector, "job-maximum-salary", "최대 연봉/급여 (선택한 형식의 숫자, 비우면 미사용)"
        )
        if minimum is not None:
            profile["minimum_salary_floor"] = minimum
        if maximum is not None:
            profile["maximum_salary_ceiling"] = maximum
    profile = {key: value for key, value in profile.items() if value not in (None, [], {}, "")}
    profile_path = output / "job-search-profile.json"
    argv: list[str] = [
        korean_command("job-search"),
        korean_option("profile"),
        str(profile_path),
        korean_option("output"),
        str(output / "job-search"),
    ]
    for provider, path in sorted(payload_paths.items()):
        argv.extend((korean_option("payload"), f"{provider}={path}"))
    return InteractiveRequest(
        "job-search",
        tuple(argv),
        profile,
        ("선택지 건수는 저장된 스냅샷에서 관측된 값만 설명합니다.",),
    )


def _file_options(data_dir: Path) -> list[MenuOption]:
    return (
        [
            MenuOption(str(path), str(path.relative_to(data_dir)), "저장된 로컬 JSON")
            for path in sorted(data_dir.rglob("*.json"))
        ]
        if data_dir.is_dir()
        else []
    )


def _taxonomy_records(data_dir: Path) -> list[dict[str, Any]]:
    """Best-effort local entity snapshot reader; it never treats ATS jobs as entities."""
    records: list[dict[str, Any]] = []
    for path in sorted(data_dir.rglob("*.json")) if data_dir.is_dir() else []:
        if not any(
            token in path.name.casefold()
            for token in ("entity", "company", "organization", "institution", "ares", "gleif", "sec", "alio")
        ):
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        candidates: Any = value
        if isinstance(value, dict):
            candidates = next(
                (
                    value[key]
                    for key in ("entities", "companies", "organizations", "data", "results")
                    if isinstance(value.get(key), list)
                ),
                [],
            )
        if isinstance(candidates, list):
            lowered = path.name.casefold()
            provider = next(
                (
                    name
                    for name, hint in (
                        ("ares", "ares"),
                        ("gleif", "gleif"),
                        ("sec", "sec"),
                        ("alio", "alio"),
                        ("mpm_public_employment", "mpm"),
                    )
                    if hint in lowered
                ),
                None,
            )
            records.extend(
                {**item, "provider": item.get("provider") or provider}
                for item in candidates
                if isinstance(item, dict)
            )
    return records


def _file_request(selector: Selector, command: str, data_dir: Path, output: Path) -> InteractiveRequest:
    if command == "company-search":
        countries = selector.text("company-countries", "국가 코드 (쉼표로 구분)", required=True)
        terms = selector.text("company-keywords", "회사명/직무 키워드 (선택, 쉼표로 구분)", required=False)
        taxonomy_facets = build_taxonomy_facets(_taxonomy_records(data_dir))
        profile = {
            "countries": _split_terms(countries),
            "job_keywords": _split_terms(terms),
            "ownership_sectors": _select_facets(
                selector,
                taxonomy_facets,
                "ownership_sector",
                "소유 부문",
                multiple=True,
                preserve_namespace=True,
            ),
            "legal_forms": _select_facets(
                selector,
                taxonomy_facets,
                "legal_form",
                "법적 형태 (원천 네임스페이스 유지)",
                multiple=True,
                preserve_namespace=True,
            ),
            "industries": _select_facets(
                selector,
                taxonomy_facets,
                "industry",
                "산업 코드/분류",
                multiple=True,
                preserve_namespace=True,
            ),
            "market_statuses": _select_facets(
                selector,
                taxonomy_facets,
                "market_status",
                "시장 상태",
                multiple=True,
                preserve_namespace=True,
            ),
            "public_institution_types": _select_facets(
                selector,
                taxonomy_facets,
                "public_institution_type",
                "공공기관 유형",
                multiple=True,
                preserve_namespace=True,
            ),
        }
        identity_choice = selector.select(
            "company-require-resolved-identity",
            "법인 식별이 확인된 결과만 포함할까요?",
            (
                MenuOption("true", "확인된 법인만", "권장: 동명이인·기관명 혼동 방지"),
                MenuOption("false", "식별 미확인 후보도 표시", "검증불가 상태를 유지해 표시"),
            ),
            multiple=False,
        )
        policy_choice = selector.select(
            "company-unknown-policy",
            "회사 속성 검사 불가 처리",
            (
                MenuOption("report", "제외하고 검증불가로 보고", "권장"),
                MenuOption("exclude", "제외", "기존 스크립트/API 호환값"),
                MenuOption("include", "후보에 포함", "검증불가 상태를 유지"),
            ),
            multiple=False,
        )
        profile["require_resolved_identity"] = (identity_choice or ["true"])[0] == "true"
        profile["unknown_policy"] = (policy_choice or ["report"])[0]
        profile = {key: value for key, value in profile.items() if value not in (None, [], {}, "")}
        if not profile.get("job_keywords") and len(profile) == 1:
            raise ValueError(
                "company-search: 키워드를 입력하거나 저장된 taxonomy 값을 하나 이상 선택해야 합니다."
            )
        note = "분류 선택값은 원천 네임스페이스를 유지하며 법적 형태와 소유 부문을 임의로 합치지 않습니다."
        return InteractiveRequest(
            command,
            (korean_command(command), korean_option("profile"), str(output / "company-search-profile.json")),
            profile,
            (note,),
        )
    options = _file_options(data_dir)
    if not options:
        return InteractiveRequest(
            command,
            (),
            {},
            ("저장된 JSON 입력이 없습니다. 로컬 artifact를 추가하거나 직접 명령을 사용하세요.",),
            False,
        )
    if command == "screen":
        profile = selector.select("screen-profile", "스크리너 프로필 JSON", options, multiple=False)
        rows = selector.select("screen-rows", "비교 대상 행 JSON", options, multiple=False)
        return InteractiveRequest(
            command,
            (korean_command(command), korean_option("profile"), *profile, korean_option("rows"), *rows),
            {},
            (),
            bool(profile and rows),
        )
    if command == "timeline":
        rows = selector.select("timeline-rows", "시간축 행 JSON", options, multiple=False)
        entity = selector.text("timeline-entity", "기업/기관 ID", required=True)
        as_of = selector.text("timeline-as-of", "기준 시각 (ISO 8601)", required=True)
        return InteractiveRequest(
            command,
            (
                korean_command(command),
                korean_option("rows"),
                *rows,
                korean_option("entity_id"),
                entity,
                korean_option("as_of"),
                as_of,
            ),
            {},
            (),
            bool(rows),
        )
    if command in {"valuation", "ai-event", "explain"}:
        selected = selector.select(
            f"{command}-input", f"{korean_command(command)} 입력 JSON", options, multiple=False
        )
        return InteractiveRequest(
            command, (korean_command(command), korean_option("input"), *selected), {}, (), bool(selected)
        )
    if command == "export":
        tables = selector.select("export-tables", "내보낼 근거 표 JSON", options, multiple=False)
        return InteractiveRequest(
            command,
            (
                korean_command(command),
                korean_option("tables"),
                *tables,
                korean_option("output"),
                str(output / "export"),
            ),
            {},
            (),
            bool(tables),
        )
    return InteractiveRequest(command, (command,), {}, ())


def build_interactive_request(selector: Selector, data_dir: Path, output: Path) -> InteractiveRequest:
    """Run menu selection only; writing/executing happens separately and is observable."""
    purpose_options = tuple(MenuOption(node.value, node.label, node.detail) for node in roots())
    purpose = selector.select("purpose", "목적을 선택하세요", purpose_options, multiple=False)
    if purpose:
        action = selector.select(
            "purpose-action", "목적의 세부 기능을 선택하세요", PURPOSE_ACTIONS[purpose[0]], multiple=False
        )
        if not action:
            return InteractiveRequest(
                "cancelled", (), {}, ("목적의 세부 기능을 선택하지 않았습니다.",), False
            )
        command = action[0]
        if command == "current-jobs":
            paths = _payload_paths(data_dir)
            if not paths:
                return InteractiveRequest(
                    command, (), {}, ("인식 가능한 저장 채용 원천 JSON이 없습니다.",), False
                )
            compiled = build_job_search_request(selector, paths, output)
            profile = {**compiled.profile, "mode": "current_job", "purpose": purpose[0]}
            return InteractiveRequest(
                command,
                (korean_command("current-jobs"), *compiled.argv[1:]),
                profile,
                (*compiled.notes, "현재 채용 모드는 선택한 로컬 스냅샷 하나만 사용합니다."),
                compiled.runnable,
            )
        if command == "job-trends":
            snapshots = _file_options(data_dir)
            selected = selector.select("trend-snapshots", "반복 스냅샷 JSON", snapshots, multiple=True)
            metric = selector.select(
                "trend-metric",
                "동향 지표",
                (
                    MenuOption("active_postings", "활성 공고 수"),
                    MenuOption("new_postings", "신규 공고 수"),
                    MenuOption("closed_postings", "종료 공고 수"),
                ),
                multiple=False,
            )
            argv: list[str] = [korean_command("job-trends")]
            for snapshot in selected:
                argv.extend((korean_option("snapshot"), snapshot))
            argv.extend((korean_option("metric"), *(metric or ["active_postings"])))
            return InteractiveRequest(
                command,
                tuple(argv),
                {"mode": "job_trend", "purpose": purpose[0], "metric": (metric or ["active_postings"])[0]},
                ("호환되는 반복 스냅샷이 제공되기 전에는 동향을 계산할 수 없습니다.",),
                bool(selected),
            )
        if command == "provider-status":
            return InteractiveRequest(
                command,
                (korean_command(command),),
                {"purpose": purpose[0]},
                ("원천 상태는 로컬 설정과 저장된 근거만 읽습니다.",),
            )
        return _file_request(selector, command, data_dir, output)
    category = selector.select("main-category", "회사·채용 정보 기능을 선택하세요", TOP_LEVEL, multiple=False)
    if not category:
        return InteractiveRequest("cancelled", (), {}, ("기능을 선택하지 않았습니다.",), False)
    action_options = ACTION_OPTIONS[category[0]]
    action = selector.select("category-action", "세부 기능을 선택하세요", action_options, multiple=False)
    if not action:
        return InteractiveRequest("cancelled", (), {}, ("세부 기능을 선택하지 않았습니다.",), False)
    command = action[0]
    if command == "provider-status":
        return InteractiveRequest(
            command,
            (korean_command(command),),
            {},
            ("원천 상태는 로컬 설정과 저장된 근거만 읽습니다.",),
        )
    if command == "job-search":
        paths = _payload_paths(data_dir)
        if not paths:
            return InteractiveRequest(
                command, (), {}, ("인식 가능한 저장 채용 원천 JSON이 없습니다.",), False
            )
        return build_job_search_request(selector, paths, output)
    return _file_request(selector, command, data_dir, output)


def select_purpose(selector: Selector) -> str | None:
    choices = selector.select(
        "purpose",
        "목적을 선택하세요",
        tuple(MenuOption(node.value, node.label) for node in roots()),
        multiple=False,
    )
    return choices[0] if choices else None


def select_current_job_mode(rows: Sequence[dict[str, Any]], snapshot_id: str | None = None) -> dict[str, Any]:
    session = SelectionSession("current_jobs", snapshot_id=snapshot_id)
    return {"mode": "current_job", "preview": preview_selection(rows, session)}


def select_trend_mode(rows: Sequence[dict[str, Any]], snapshot_id: str | None = None) -> dict[str, Any]:
    session = SelectionSession("job_trends", snapshot_id=snapshot_id)
    return {"mode": "job_trend", "preview": preview_selection(rows, session)}


def render_branch(
    rows: Sequence[dict[str, Any]], session: SelectionSession, field: str
) -> list[dict[str, Any]]:
    return [item.__dict__ for item in branches_for_selection(rows, session, field)]


def apply_selection(
    rows: Sequence[dict[str, Any]], session: SelectionSession, field: str, value: str
) -> SelectionSession:
    from .category_tree import advance_selection

    return advance_selection(session, rows, field, value)


def backtrack(session: SelectionSession, field: str | None = None) -> SelectionSession:
    from .category_tree import backtrack_selection

    return backtrack_selection(session, field)


def render_preview(rows: Sequence[dict[str, Any]], session: SelectionSession) -> dict[str, Any]:
    return preview_selection(rows, session)


def write_interactive_profile(request: InteractiveRequest, output: Path) -> InteractiveRequest:
    """Persist only a generated profile, never raw credentials or provider responses."""
    output.mkdir(parents=True, exist_ok=True)
    if not request.profile:
        return request
    name = "company-search-profile.json" if request.command == "company-search" else "job-search-profile.json"
    (output / name).write_text(
        json.dumps(request.profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return request


def load_scripted_selector(path: Path) -> ScriptedSelector:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError("선택 스크립트는 JSON 객체여야 합니다.")
    return ScriptedSelector(value.get("answers", value))
