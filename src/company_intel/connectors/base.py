from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from typing import Any

MISSING = object()


def get_path(value: Any, path: str) -> Any:
    current = value
    for token in path.split("."):
        if isinstance(current, list) and token.isdigit():
            index = int(token)
            if index >= len(current):
                return MISSING
            current = current[index]
        elif isinstance(current, dict) and token in current:
            current = current[token]
        else:
            return MISSING
    return current


def json_payload(body: bytes) -> Any:
    return json.loads(body.decode("utf-8-sig"))


def xml_payload(body: bytes) -> ET.Element:
    return ET.fromstring(body)


def to_number(value: Any) -> float | None:
    if value in (None, "", ".", "-"):
        return None
    try:
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None


def compact(value: Any, max_items: int = 5, depth: int = 0) -> Any:
    if depth >= 3:
        if isinstance(value, list):
            return {"_type": "array", "_length": len(value)}
        if isinstance(value, dict):
            return {"_type": "object", "_keys": len(value)}
    if isinstance(value, list):
        sample = [compact(item, max_items, depth + 1) for item in value[:max_items]]
        if len(value) > max_items:
            sample.append({"_truncated_items": len(value) - max_items})
        return sample
    if isinstance(value, dict):
        items = list(value.items())
        result = {key: compact(item, max_items, depth + 1) for key, item in items[:20]}
        if len(items) > 20:
            result["_truncated_keys"] = len(items) - 20
        return result
    if isinstance(value, str) and len(value) > 600:
        return value[:600] + f"…<{len(value) - 600} chars omitted>"
    return value
