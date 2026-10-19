from __future__ import annotations

import time
import pytest
from company_intel.http import HttpClient
from company_intel.middleware.rate_limiter import (
    CircuitBreaker,
    CircuitState,
    HttpTrafficGovernor,
    TokenBucket,
)
from company_intel.models import Probe


def test_token_bucket_acquisition_and_depletion():
    bucket = TokenBucket(rate=10.0, capacity=3.0)
    # Acquired 3 times successfully
    assert bucket.acquire(1.0, timeout=0.1) is True
    assert bucket.acquire(1.0, timeout=0.1) is True
    assert bucket.acquire(1.0, timeout=0.1) is True
    # Bucket depleted, timeout too short
    assert bucket.acquire(1.0, timeout=0.01) is False
    # Wait for refill
    time.sleep(0.15)
    assert bucket.acquire(1.0, timeout=0.2) is True


def test_circuit_breaker_transitions():
    cb = CircuitBreaker(failure_threshold=3, cooldown_seconds=0.2)
    host = "api.example.com"

    # Initial state CLOSED
    can_go, msg = cb.can_request(host)
    assert can_go is True
    assert msg == "OK"

    # 1st failure
    cb.record_failure(host, "HTTP 500")
    assert cb._get_host_info(host).state == CircuitState.CLOSED
    assert cb._get_host_info(host).consecutive_failures == 1

    # 2nd failure
    cb.record_failure(host, "HTTP 502")
    assert cb._get_host_info(host).state == CircuitState.CLOSED

    # 3rd failure -> trips to OPEN
    cb.record_failure(host, "HTTP 503")
    assert cb._get_host_info(host).state == CircuitState.OPEN

    # Request rejected while OPEN
    can_go, msg = cb.can_request(host)
    assert can_go is False
    assert "Circuit breaker OPEN" in msg

    # Wait for cooldown to expire
    time.sleep(0.25)

    # First request after cooldown moves to HALF_OPEN
    can_go, msg = cb.can_request(host)
    assert can_go is True
    assert "HALF_OPEN" in msg
    assert cb._get_host_info(host).state == CircuitState.HALF_OPEN

    # Successful response resets to CLOSED
    cb.record_success(host)
    assert cb._get_host_info(host).state == CircuitState.CLOSED
    assert cb._get_host_info(host).consecutive_failures == 0


def test_http_client_with_governor_fail_fast(monkeypatch):
    import urllib.error

    def mock_urlopen(*args, **kwargs):
        raise urllib.error.URLError("Connection refused mock")

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)

    governor = HttpTrafficGovernor(failure_threshold=2, cooldown_seconds=0.5)
    client = HttpClient(timeout=1.0, retries=0, traffic_governor=governor)
    probe = Probe("test_probe", "test", "test", ["KR"], "GET", "http://test-circuit-breaker-host.local/api")

    # Attempt 1: Network error -> failure 1
    res1 = client.execute(probe)
    assert res1.status_code is None
    assert governor.circuit_breaker._get_host_info("test-circuit-breaker-host.local").consecutive_failures == 1

    # Attempt 2: Network error -> failure 2 -> trips to OPEN
    res2 = client.execute(probe)
    assert governor.circuit_breaker._get_host_info("test-circuit-breaker-host.local").state == CircuitState.OPEN

    # Attempt 3: Fail-fast immediately intercepted by CircuitBreaker (status 503, 0 attempts)
    res3 = client.execute(probe)
    assert res3.status_code == 503
    assert res3.attempts == 0
    assert "Circuit breaker" in (res3.error or "")
