from __future__ import annotations

import json
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

SENSITIVE_QUERY_KEYS = {
    "api_key",
    "apikey",
    "authkey",
    "crtfc_key",
    "userid",
    "key",
    "servicekey",
    "authorization",
}


def redact_url(url: str, secrets: list[str] | tuple[str, ...] = ()) -> str:
    parts = urlsplit(url)
    query = []
    for key, value in parse_qsl(parts.query, keep_blank_values=True):
        query.append((key, "<redacted>" if key.lower() in SENSITIVE_QUERY_KEYS else value))
    redacted = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))
    for secret in secrets:
        if secret:
            redacted = redacted.replace(secret, "<redacted>")
    return redacted


def redact_value(value: Any, secrets: list[str] | tuple[str, ...]) -> Any:
    if isinstance(value, dict):
        return {
            key: "<redacted>" if key.lower() in SENSITIVE_QUERY_KEYS else redact_value(item, secrets)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_value(item, secrets) for item in value]
    if isinstance(value, str):
        result = value
        for secret in secrets:
            if secret:
                result = result.replace(secret, "<redacted>")
        return result
    return value


def redact_body(body: bytes, secrets: list[str], content_type: str = "") -> tuple[bytes, bool]:
    if not body or not secrets:
        return body, False
    if not any(secret.encode("utf-8") in body for secret in secrets if secret):
        return body, False
    try:
        if "json" in content_type.lower() or body.lstrip().startswith((b"{", b"[")):
            payload = json.loads(body.decode("utf-8-sig"))
            redacted = json.dumps(redact_value(payload, secrets), ensure_ascii=False, indent=2).encode(
                "utf-8"
            )
        else:
            text = body.decode("utf-8", errors="replace")
            redacted_text = text
            for secret in secrets:
                redacted_text = redacted_text.replace(secret, "<redacted>")
            redacted = redacted_text.encode("utf-8")
        return redacted, redacted != body
    except (UnicodeError, json.JSONDecodeError, TypeError, ValueError):
        output = body
        changed = False
        for secret in secrets:
            if not secret:
                continue
            encoded = secret.encode("utf-8")
            if encoded in output:
                output = output.replace(encoded, b"<redacted>")
                changed = True
        return output, changed
