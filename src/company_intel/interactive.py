"""Evidence-aware terminal selection for the composable ``company-intel`` CLI.

The normal subcommands remain the machine-friendly contract.  This module only
compiles a user selection into those same arguments; it never refreshes a
provider or invents a filter value that is absent from a saved snapshot.
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import asdict, dataclass, is_dataclass
from pathlib import Path
from typing import Any, Protocol, Sequence

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
            "argv": list(self.argv),
            "profile": self.profile,
            "notes": list(self.notes),
            "runnable": self.runnable,
        }


class Selector(Protocol):
    def select(self, prompt_id: str, title: str, options: Sequence[MenuOption], *, multiple: bool = False) -> list[str]: ...

    def text(self, prompt_id: str, title: str, *, required: bool = False, default: str = "") -> str: ...


class ScriptedSelector:
    """Non-TTY adapter used by tests and repeatable saved interactive scripts."""

    def __init__(self, answers: dict[str, Any]) -> None:
        self.answers = answers

    def select(self, prompt_id: str, title: str, options: Sequence[MenuOption], *, multiple: bool = False) -> list[str]:
        available = {option.value: option for option in options}
        value = self.answers.get(prompt_id, [])
        selected = [value] if isinstance(value, str) else list(value or [])
        if not multiple and len(selected) > 1:
            selected = selected[:1]
        invalid = [item for item in selected if item not in available or not available[item].enabled]
        if invalid:
            raise ValueError(f"{prompt_id}: unsupported or disabled selection: {', '.join(str(item) for item in invalid)}")
        return [str(item) for item in selected]

    def text(self, prompt_id: str, title: str, *, required: bool = False, default: str = "") -> str:
        value = str(self.answers.get(prompt_id, default)).strip()
        if required and not value:
            raise ValueError(f"{prompt_id}: a value is required")
        return value


class ArrowMenu:
    """Minimal standard-library arrow/space/Enter menu.

    ``curses`` deliberately remains an adapter rather than product logic, so
    the same workflow can be tested through :class:`ScriptedSelector`.
    """

    def select(self, prompt_id: str, title: str, options: Sequence[MenuOption], *, multiple: bool = False) -> list[str]:
        if not options:
            return []
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            raise RuntimeError("interactive selection needs a TTY; use --script for a saved selection")
        import curses

        def render(screen: Any) -> list[str]:
            curses.curs_set(0)
            index = next((number for number, option in enumerate(options) if option.enabled), 0)
            selected: set[str] = set()
            while True:
                screen.erase()
                height, width = screen.getmaxyx()
                screen.addnstr(0, 0, title, max(1, width - 1), curses.A_BOLD)
                screen.addnstr(1, 0, "↑/↓ move · Space toggle · Enter confirm · Esc cancel", max(1, width - 1))
                for number, option in enumerate(options[: max(1, height - 3)]):
                    marker = "●" if option.value in selected else "○"
                    cursor = ">" if number == index else " "
                    suffix = f" — {option.detail}" if option.detail else ""
                    style = curses.A_REVERSE if number == index else curses.A_NORMAL
                    if not option.enabled:
                        style |= curses.A_DIM
                    screen.addnstr(number + 3, 0, f"{cursor} {marker if multiple else ' '} {option.label}{suffix}", max(1, width - 1), style)
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
            raise ValueError(f"{prompt_id}: a value is required")
        return value


TOP_LEVEL = (
    MenuOption("readiness", "데이터 준비 상태", "provider 상태·coverage·제한"),
    MenuOption("discovery", "채용·기업 탐색", "국가·직무·위치·조건·분류"),
    MenuOption("comparison", "기업 비교", "비교 가능 cohort와 순위"),
    MenuOption("analysis", "시간축·가치·AI 사건", "근거와 사전조건을 먼저 확인"),
    MenuOption("delivery", "설명·내보내기", "run 근거와 CSV/XLSX"),
)

ACTION_OPTIONS = {
    "readiness": (MenuOption("provider-status", "Provider 상태", "사용 가능 field와 activation 경계"),),
    "discovery": (
        MenuOption("job-search", "채용공고 검색", "공고·요건·자격·근무 조건"),
        MenuOption("company-search", "기업/공공기관 검색", "법적 형태·소유·산업·시장 상태"),
    ),
    "comparison": (MenuOption("screen", "동료군 스크리너", "비교 가능한 signature group만 정렬"),),
    "analysis": (
        MenuOption("timeline", "회사·시장·거시 시간축", "axis별 series group"),
        MenuOption("valuation", "가치 시나리오", "source/time/unit/currency 조건"),
        MenuOption("ai-event", "AI 사건 분석", "control 없으면 association-only"),
    ),
    "delivery": (
        MenuOption("explain", "판단 근거 설명", "제외·검사 불가·source coverage"),
        MenuOption("export", "증거 스프레드시트", "CSV/XLSX와 manifest"),
    ),
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
        providers = ", ".join(value.get("providers") or ([value["provider"]] if value.get("provider") else []))
        status = str(value.get("filterability") or value.get("status") or "exact-select")
        reason = str(value.get("reason") or value.get("disabled_reason") or "")
        label = str(value.get("display_label") or value.get("label") or raw)
        namespace = str(value.get("vocabulary_namespace") or "").strip()
        selection_value = f"{namespace}:{raw}" if preserve_namespace and namespace else raw
        if preserve_namespace and namespace:
            label = f"{label} [{namespace}]"
        detail = " · ".join(part for part in (f"{count}건" if count is not None else "", providers, status, reason) if part)
        result.append(MenuOption(selection_value, label, detail, status not in {"unavailable", "display-only", "forbidden"}))
    return result


def _payload_paths(data_dir: Path) -> dict[str, Path]:
    aliases = {
        "greenhouse": ("greenhouse",), "lever": ("lever",),
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
            f"{group['count']}건 · {', '.join(sorted(group['providers']))} · {group['kind']} · {necessity}",
        )
        for (normalized, label), group in sorted(grouped.items(), key=lambda item: (-item[1]["count"], item[0][1].casefold()))
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
        raise ValueError(f"{prompt_id}: enter a finite number or leave blank") from error
    if not math.isfinite(value):
        raise ValueError(f"{prompt_id}: enter a finite number or leave blank")
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
            raise ValueError("job-country-allocation: use ISO=non-negative integer pairs")
        code = country.strip().upper()
        if code not in countries:
            raise ValueError("job-country-allocation: country must be selected above")
        try:
            value = int(count.strip())
        except ValueError as error:
            raise ValueError("job-country-allocation: use ISO=non-negative integer pairs") from error
        if value < 0:
            raise ValueError("job-country-allocation: limit cannot be negative")
        allocation[code] = value
    return allocation


def build_job_search_request(selector: Selector, payload_paths: dict[str, Path], output: Path) -> InteractiveRequest:
    payloads = _load_payloads(payload_paths)
    jobs, requirements, _sources = normalize_provider_payloads(payloads)
    facets = build_job_facets(jobs)
    countries = _select_facets(selector, facets, "country_code", "국가를 선택하세요", multiple=True)
    keywords = _split_terms(selector.text("job-keywords", "직무/키워드 (쉼표로 구분)", required=True))
    if not countries:
        raise ValueError("job-country_code: at least one available country must be selected")
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
        "occupations": _select_facets(selector, facets, "occupation_label", "직종/직무명 (저장된 공고 기준)", multiple=True),
        "locations": _select_facets(selector, facets, "location", "근무 위치", multiple=True),
        "workplace_types": _select_facets(selector, facets, "workplace_type", "근무 방식", multiple=True),
        "employment_types": _select_facets(selector, facets, "employment_type", "고용 형태", multiple=True),
        "posting_languages": _select_facets(selector, facets, "posting_language", "공고 표시 언어", multiple=True),
        "business_units": _select_facets(selector, facets, "business_unit", "공고 조직 단위", multiple=True),
        "industries": _select_facets(selector, facets, "industry", "산업 (원천에 있는 경우)", multiple=True),
        "company_types": _select_facets(selector, facets, "company_type", "고용주 유형 (검증된 경우)", multiple=True),
        "required_requirement_terms": _select_requirements(
            selector, requirements, "job-required-requirements", "필수 요건 (저장된 공고 기준)", necessity="required"
        ),
        "preferred_requirement_terms": _select_requirements(
            selector, requirements, "job-preferred-requirements", "우대 요건 (정렬 가중치)", necessity="preferred"
        ),
        "required_languages": _select_requirements(
            selector, requirements, "job-required-languages", "지원자 필수 언어", necessity="required", language_only=True
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
            MenuOption("exclude", "제외", "기본 script/API 호환값"),
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
        minimum = _optional_number(selector, "job-minimum-salary", "최소 연봉/급여 (선택한 형식의 숫자, 비우면 미사용)")
        maximum = _optional_number(selector, "job-maximum-salary", "최대 연봉/급여 (선택한 형식의 숫자, 비우면 미사용)")
        if minimum is not None:
            profile["minimum_salary_floor"] = minimum
        if maximum is not None:
            profile["maximum_salary_ceiling"] = maximum
    profile = {key: value for key, value in profile.items() if value not in (None, [], {}, "")}
    profile_path = output / "job-search-profile.json"
    argv: list[str] = ["job-search", "--profile", str(profile_path), "--output", str(output / "job-search")]
    for provider, path in sorted(payload_paths.items()):
        argv.extend(("--payload", f"{provider}={path}"))
    return InteractiveRequest("job-search", tuple(argv), profile, ("Facet counts describe only saved snapshots.",))


def _file_options(data_dir: Path) -> list[MenuOption]:
    return [MenuOption(str(path), str(path.relative_to(data_dir)), "saved local JSON") for path in sorted(data_dir.rglob("*.json"))] if data_dir.is_dir() else []


def _taxonomy_records(data_dir: Path) -> list[dict[str, Any]]:
    """Best-effort local entity snapshot reader; it never treats ATS jobs as entities."""
    records: list[dict[str, Any]] = []
    for path in sorted(data_dir.rglob("*.json")) if data_dir.is_dir() else []:
        if not any(token in path.name.casefold() for token in ("entity", "company", "organization", "institution", "ares", "gleif", "sec", "alio")):
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        candidates: Any = value
        if isinstance(value, dict):
            candidates = next((value[key] for key in ("entities", "companies", "organizations", "data", "results") if isinstance(value.get(key), list)), [])
        if isinstance(candidates, list):
            lowered = path.name.casefold()
            provider = next((name for name, hint in (
                ("ares", "ares"), ("gleif", "gleif"), ("sec", "sec"),
                ("alio", "alio"), ("mpm_public_employment", "mpm"),
            ) if hint in lowered), None)
            records.extend(
                {**item, "provider": item.get("provider") or provider}
                for item in candidates if isinstance(item, dict)
            )
    return records


def _file_request(selector: Selector, command: str, data_dir: Path, output: Path) -> InteractiveRequest:
    if command == "company-search":
        countries = selector.text("company-countries", "국가 코드 (쉼표로 구분)", required=True)
        terms = selector.text("company-keywords", "회사명/직무 키워드 (선택, 쉼표로 구분)", required=False)
        taxonomy_facets = build_taxonomy_facets(_taxonomy_records(data_dir))
        profile = {
            "countries": _split_terms(countries), "job_keywords": _split_terms(terms),
            "ownership_sectors": _select_facets(selector, taxonomy_facets, "ownership_sector", "소유 부문", multiple=True, preserve_namespace=True),
            "legal_forms": _select_facets(selector, taxonomy_facets, "legal_form", "법적 형태 (원천 namespace 유지)", multiple=True, preserve_namespace=True),
            "industries": _select_facets(selector, taxonomy_facets, "industry", "산업 코드/분류", multiple=True, preserve_namespace=True),
            "market_statuses": _select_facets(selector, taxonomy_facets, "market_status", "시장 상태", multiple=True, preserve_namespace=True),
            "public_institution_types": _select_facets(selector, taxonomy_facets, "public_institution_type", "공공기관 유형", multiple=True, preserve_namespace=True),
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
                MenuOption("exclude", "제외", "기본 script/API 호환값"),
                MenuOption("include", "후보에 포함", "검증불가 상태를 유지"),
            ),
            multiple=False,
        )
        profile["require_resolved_identity"] = (identity_choice or ["true"])[0] == "true"
        profile["unknown_policy"] = (policy_choice or ["report"])[0]
        profile = {key: value for key, value in profile.items() if value not in (None, [], {}, "")}
        if not profile.get("job_keywords") and len(profile) == 1:
            raise ValueError("company-search: enter a keyword or select an observed taxonomy value")
        note = "Taxonomy options retain provider namespaces and never merge legal form with ownership."
        return InteractiveRequest(command, (command, "--profile", str(output / "company-search-profile.json")), profile, (note,))
    options = _file_options(data_dir)
    if not options:
        return InteractiveRequest(command, (), {}, ("No saved JSON input was found; add a local artifact or use the scriptable command.",), False)
    if command == "screen":
        profile = selector.select("screen-profile", "스크리너 profile JSON", options, multiple=False)
        rows = selector.select("screen-rows", "비교 대상 rows JSON", options, multiple=False)
        return InteractiveRequest(command, (command, "--profile", *profile, "--rows", *rows), {}, (), bool(profile and rows))
    if command == "timeline":
        rows = selector.select("timeline-rows", "시간축 rows JSON", options, multiple=False)
        entity = selector.text("timeline-entity", "기업/기관 ID", required=True)
        as_of = selector.text("timeline-as-of", "as-of (ISO datetime)", required=True)
        return InteractiveRequest(command, (command, "--rows", *rows, "--entity-id", entity, "--as-of", as_of), {}, (), bool(rows))
    if command in {"valuation", "ai-event", "explain"}:
        selected = selector.select(f"{command}-input", f"{command} input JSON", options, multiple=False)
        return InteractiveRequest(command, (command, "--input", *selected), {}, (), bool(selected))
    if command == "export":
        tables = selector.select("export-tables", "내보낼 evidence tables JSON", options, multiple=False)
        return InteractiveRequest(command, (command, "--tables", *tables, "--output", str(output / "export")), {}, (), bool(tables))
    return InteractiveRequest(command, (command,), {}, ())


def build_interactive_request(selector: Selector, data_dir: Path, output: Path) -> InteractiveRequest:
    """Run menu selection only; writing/executing happens separately and is observable."""
    category = selector.select("main-category", "Company Intelligence 기능을 선택하세요", TOP_LEVEL, multiple=False)
    if not category:
        return InteractiveRequest("cancelled", (), {}, ("No command selected.",), False)
    action_options = ACTION_OPTIONS[category[0]]
    action = selector.select("category-action", "세부 기능을 선택하세요", action_options, multiple=False)
    if not action:
        return InteractiveRequest("cancelled", (), {}, ("No subcommand selected.",), False)
    command = action[0]
    if command == "provider-status":
        return InteractiveRequest(command, (command,), {}, ("Provider status reads local configuration and saved evidence only.",))
    if command == "job-search":
        paths = _payload_paths(data_dir)
        if not paths:
            return InteractiveRequest(command, (), {}, ("No recognized saved job-provider JSON was found.",), False)
        return build_job_search_request(selector, paths, output)
    return _file_request(selector, command, data_dir, output)


def write_interactive_profile(request: InteractiveRequest, output: Path) -> InteractiveRequest:
    """Persist only a generated profile, never raw credentials or provider responses."""
    output.mkdir(parents=True, exist_ok=True)
    if not request.profile:
        return request
    name = "company-search-profile.json" if request.command == "company-search" else "job-search-profile.json"
    (output / name).write_text(json.dumps(request.profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return request


def load_scripted_selector(path: Path) -> ScriptedSelector:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("interactive script must be a JSON object")
    return ScriptedSelector(value.get("answers", value))
