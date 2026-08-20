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
        fields = "OK" if not item.get("missing_fields") else ", ".join(item["missing_fields"][:3])
        note = (
            item.get("provider_error")
            or item.get("parse_error")
            or item.get("message")
            or item.get("limitation")
            or ""
        )
        lines.append(
            f"| {item['id']} | {item['provider']} | {', '.join(item['regions'])} | {item['category']} | "
            f"{item.get('http_status') or '-'} | {item['status']} | {fields} | {str(note).replace('|', '/')} |"
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
