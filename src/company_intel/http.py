from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from email.message import Message
from typing import Any

from .middleware import GLOBAL_TRAFFIC_GOVERNOR, HttpTrafficGovernor
from .models import HttpResult, Probe

TRANSIENT_CODES = {429, 500, 502, 503, 504}
LOG_HEADERS = {"content-type", "content-length", "etag", "last-modified", "retry-after", "cache-control"}


def _selected_headers(headers: Message | Any) -> dict[str, str]:
    output: dict[str, str] = {}
    for key, value in headers.items():
        lowered = key.lower()
        if lowered in LOG_HEADERS or "ratelimit" in lowered or "quota" in lowered:
            output[lowered] = value
    return output


class HttpClient:
    def __init__(
        self,
        timeout: float = 45.0,
        retries: int = 2,
        delay: float = 0.2,
        traffic_governor: HttpTrafficGovernor | None = None,
    ) -> None:
        self.timeout = timeout
        self.retries = retries
        self.delay = delay
        self.traffic_governor = traffic_governor or GLOBAL_TRAFFIC_GOVERNOR

    def execute(self, probe: Probe) -> HttpResult:
        parsed_url = urllib.parse.urlsplit(probe.url)
        host = parsed_url.hostname or "default"
        can_go, reject_reason = self.traffic_governor.acquire(host, timeout=2.0)
        if not can_go:
            return HttpResult(
                503,
                {"retry-after": "60"},
                b"",
                0.0,
                0,
                f"TrafficGovernor rejected: {reject_reason}",
            )

        url = probe.url
        if probe.params:
            query = urllib.parse.urlencode(probe.params, doseq=True)
            url = f"{url}{'&' if '?' in url else '?'}{query}"
        data = None
        headers = {
            "Accept": "application/json, application/xml, text/xml, */*",
            "User-Agent": "keyless-company-api-validator/1.0",
            **probe.headers,
        }
        if probe.json_body is not None:
            data = json.dumps(probe.json_body, ensure_ascii=False).encode("utf-8")
            headers.setdefault("Content-Type", "application/json")
        elif probe.form_body is not None:
            data = urllib.parse.urlencode(probe.form_body, doseq=True).encode("utf-8")
            headers.setdefault("Content-Type", "application/x-www-form-urlencoded")

        last: HttpResult | None = None
        for attempt in range(self.retries + 1):
            request = urllib.request.Request(url, data=data, headers=headers, method=probe.method)
            started = time.perf_counter()
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    body = response.read()
                    self.traffic_governor.record_success(host)
                    result = HttpResult(
                        response.status,
                        _selected_headers(response.headers),
                        body,
                        round((time.perf_counter() - started) * 1000, 2),
                        attempt + 1,
                    )
                    time.sleep(self.delay)
                    return result
            except urllib.error.HTTPError as error:
                if error.code in TRANSIENT_CODES:
                    self.traffic_governor.record_failure(host, f"HTTP {error.code}")
                last = HttpResult(
                    error.code,
                    _selected_headers(error.headers),
                    error.read(),
                    round((time.perf_counter() - started) * 1000, 2),
                    attempt + 1,
                    f"HTTPError: {error.reason}",
                )
                if error.code not in TRANSIENT_CODES or attempt >= self.retries:
                    return last
                retry_after = last.headers.get("retry-after")
                wait = float(retry_after) if retry_after and retry_after.isdigit() else min(2**attempt, 8)
                time.sleep(wait)
            except (urllib.error.URLError, TimeoutError, OSError) as error:
                self.traffic_governor.record_failure(host, f"{type(error).__name__}: {error}")
                last = HttpResult(
                    None,
                    {},
                    b"",
                    round((time.perf_counter() - started) * 1000, 2),
                    attempt + 1,
                    f"{type(error).__name__}: {error}",
                )
                if attempt >= self.retries:
                    return last
                time.sleep(min(2**attempt, 8))
        assert last is not None
        return last
