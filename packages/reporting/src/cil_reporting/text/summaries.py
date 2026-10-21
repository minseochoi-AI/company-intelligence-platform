"""Canonical responsibility owner; migrated from src/company_intel/reporting.py."""

from __future__ import annotations
from pathlib import Path
from typing import Any


def validation_report_ko(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# 기업 인텔리전스 API 실행 검증",
        "",
        f"- 시작: `{payload['started_at']}`",
        f"- 종료: `{payload['finished_at']}`",
        f"- 전체 프로브: **{summary['probe_count']}**",
        f"- 통과: **{summary['passed']}**",
        f"- 미통과/건너뜀: **{summary['not_passed']}**",
        f"- 상태 분포: `{summary['status_counts']}`",
        "",
        "## 공급자별 결과",
        "",
        "| 프로브 | 공급자 | 지역 | 범주 | HTTP | 판정 | 필드 | 주의사항 |",
        "|---|---|---|---|---:|---|---|---|",
    ]
    for item in payload["results"]:
        fields = (
            "OK"
            if not item.get("missing_fields")
            else ", ".join(item["missing_fields"][:3])
        )
        note = (
            item.get("provider_error")
            or item.get("parse_error")
            or item.get("message")
            or item.get("limitation")
            or ""
        )
        lines.append(
            f"| {item['id']} | {item['provider']} | {', '.join(item['regions'])} | {item['category']} | {item.get('http_status') or '-'} | {item['status']} | {fields} | {str(note).replace('|', '/')} |"
        )
    lines.extend(
        [
            "",
            "## 판정 해석",
            "",
            "- `passed`: 실제 응답이 성공했고 계획상 필수 필드가 존재함.",
            "- `missing_secret`: 커넥터는 있으나 해당 환경변수가 없어 호출하지 않음.",
            "- `provider_error`: HTTP는 성공했지만 공급자가 오류 또는 제한 메시지를 반환함.",
            "- `field_mismatch`: 형식은 읽었지만 계획 필드가 없어서 운영 입력으로 채택하지 않음.",
            "- 성공한 표본은 전체 기업 커버리지, 재배포 권리, 장기 SLA를 보장하지 않음.",
            "- 기업 순위와 미래가치는 산업·국가·규모 동료군, point-in-time 시점, 데이터 신뢰도를 함께 사용해야 함.",
            "",
        ]
    )
    return "\n".join(lines)


def write_validation_report(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(validation_report_ko(payload), encoding="utf-8")


def render_export_summary(
    manifest: dict[str, Any],
    *,
    unavailable_count: int = 0,
    run_manifest: dict[str, Any] | None = None,
) -> str:
    lines = [
        "# 기업·채용 근거 내보내기",
        "",
        f"- 형식 버전: `{manifest.get('format_version')}`",
        f"- 생성 시각: `{manifest.get('generated_at')}`",
        f"- 요건 미확인/제한 행: **{unavailable_count}**",
        "",
        "## 파일",
        "",
    ]
    for item in manifest.get("files", []):
        lines.append(f"- `{item['name']}` — SHA-256 `{item['sha256']}`")
    lines.extend(
        [
            "",
            "## 안내",
            "",
            "- CSV bundle이 기준 계약이며 XLSX는 동일 테이블의 표시 형식이다.",
            "- 자격요건에 원천 URL 또는 제외 사유가 없으면 확정 요건으로 해석하지 않는다.",
        ]
    )
    summary = "\n".join(lines) + "\n"
    return (
        summary
        if run_manifest is None
        else summary + "\n" + render_run_lineage_summary(run_manifest)
    )


def render_verdict_counts(
    *, matched: int, no_match: int, unverifiable: int, conflict: int
) -> str:
    return (
        f"일치 {matched}, 불일치 {no_match}, 검증불가 {unverifiable}, 충돌 {conflict}"
    )


def render_run_lineage_summary(manifest: dict[str, Any]) -> str:
    """Render a Korean, non-sensitive explanation of a saved local run.

    The full profile and source snapshots remain in the JSON manifest.  This
    summary deliberately reports their hashes and coverage counts instead of
    echoing user-entered values or provider response bodies.
    """
    lineage = manifest.get("lineage")
    if not isinstance(lineage, dict):
        lineage = {}
    facets = manifest.get("facets")
    sources = manifest.get("sources")
    verdict_counts = manifest.get("verdict_counts")
    outputs = manifest.get("output_files")
    lines = [
        "## 실행 근거와 적용 범위",
        "",
        f"- 실행 ID: `{manifest.get('run_id', 'unknown')}`",
        f"- 명령: `{manifest.get('command', 'unknown')}`",
        f"- 생성 시각: `{manifest.get('generated_at', 'unknown')}`",
        f"- profile SHA-256: `{lineage.get('profile_sha256', 'unknown')}`",
        f"- facet snapshot SHA-256: `{lineage.get('facet_snapshot_sha256', 'unknown')}`",
        f"- source snapshot SHA-256: `{lineage.get('source_snapshot_sha256', 'unknown')}`",
        f"- 선택지: **{(len(facets) if isinstance(facets, list) else 0)}개**, 원천: **{(len(sources) if isinstance(sources, list) else 0)}개**",
    ]
    if isinstance(verdict_counts, dict):
        ordered_counts = ", ".join(
            (f"{key} {verdict_counts[key]}" for key in sorted(verdict_counts))
        )
        lines.append(f"- 판정: {ordered_counts or '기록 없음'}")
    else:
        lines.append("- 판정: 기록 없음")
    if isinstance(outputs, list):
        lines.append(f"- 출력 파일: **{len(outputs)}개**")
    lines.extend(
        [
            "",
            "- `불일치`는 제공된 구조화 값이 조건과 맞지 않는 경우이고, `검증불가`는 원천이 해당 필드를 제공하지 않거나 비교 규격이 맞지 않는 경우입니다.",
            "- 이 요약은 저장된 snapshot의 coverage만 설명하며, live provider 상태나 현재 채용 여부를 새로 주장하지 않습니다.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_provider_limitations(sources: list[dict[str, object]]) -> list[str]:
    return [
        f"{row.get('provider', 'unknown')}: {row.get('limitations', '제한 정보 없음')}"
        for row in sources
    ]


def render_selection_summary(selection: dict[str, Any]) -> str:
    return "선택 목적: `{}` · mode: `{}` · snapshot: `{}`".format(
        selection.get("purpose", "unknown"),
        selection.get("mode", "unknown"),
        selection.get("snapshot_id", "not_selected"),
    )


def render_denominators(denominators: dict[str, Any]) -> str:
    labels = (
        "provider_returned",
        "normalized",
        "active",
        "strict_match",
        "unverifiable",
        "no_match",
        "conflict",
    )
    return " · ".join((f"{label}={denominators.get(label, 0)}" for label in labels))


def render_trend_eligibility(eligibility: dict[str, Any]) -> str:
    if eligibility.get("eligible"):
        return "동향 분석 가능: 동일 provider·분류·coverage signature의 반복 snapshot입니다."
    return f"동향 분석 불가: `{eligibility.get('reason', 'insufficient_history')}`"


def render_replay_guidance(run_id: str | None) -> str:
    return f"재현은 저장된 `run_id={run_id or 'unknown'}`의 selection·snapshot ref만 사용하며 provider를 자동 갱신하지 않습니다."


def write_export_summary(
    path: Path,
    manifest: dict[str, Any],
    *,
    unavailable_count: int = 0,
    run_manifest: dict[str, Any] | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_export_summary(
            manifest, unavailable_count=unavailable_count, run_manifest=run_manifest
        ),
        encoding="utf-8",
    )
