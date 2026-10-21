"""Canonical responsibility owner; migrated from src/company_intel/middleware/rate_limiter.py."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import threading
import time


class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


@dataclass
class TokenBucket:
    """Token Bucket rate limiter per host/domain."""

    rate: float = 10.0
    capacity: float = 20.0
    tokens: float = field(init=False)
    last_update: float = field(default_factory=time.monotonic)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def __post_init__(self) -> None:
        self.tokens = self.capacity

    def acquire(self, requested: float = 1.0, timeout: float = 2.0) -> bool:
        """Attempt to acquire tokens; wait up to timeout seconds if bucket is empty."""
        deadline = time.monotonic() + timeout
        while True:
            with self._lock:
                now = time.monotonic()
                elapsed = now - self.last_update
                self.last_update = now
                self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
                if self.tokens >= requested:
                    self.tokens -= requested
                    return True
            wait_needed = (requested - self.tokens) / self.rate
            if time.monotonic() + wait_needed > deadline:
                return False
            time.sleep(min(wait_needed, 0.05))


@dataclass
class HostCircuitInfo:
    state: CircuitState = CircuitState.CLOSED
    consecutive_failures: int = 0
    failure_threshold: int = 3
    cooldown_seconds: float = 60.0
    last_state_change: float = field(default_factory=time.monotonic)
    last_error: str | None = None


class CircuitBreaker:
    """Guards downstream APIs from cascade failures with CLOSED -> OPEN -> HALF_OPEN state machine."""

    def __init__(
        self, failure_threshold: int = 3, cooldown_seconds: float = 60.0
    ) -> None:
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self._hosts: dict[str, HostCircuitInfo] = {}
        self._lock = threading.Lock()

    def _get_host_info(self, host: str) -> HostCircuitInfo:
        if host not in self._hosts:
            self._hosts[host] = HostCircuitInfo(
                failure_threshold=self.failure_threshold,
                cooldown_seconds=self.cooldown_seconds,
            )
        return self._hosts[host]

    def can_request(self, host: str) -> tuple[bool, str]:
        """Check if request is allowed through the circuit breaker."""
        with self._lock:
            info = self._get_host_info(host)
            now = time.monotonic()
            if info.state == CircuitState.OPEN:
                elapsed = now - info.last_state_change
                if elapsed >= info.cooldown_seconds:
                    info.state = CircuitState.HALF_OPEN
                    info.last_state_change = now
                    return (
                        True,
                        "Circuit breaker transitioning to HALF_OPEN (trial request)",
                    )
                return (
                    False,
                    f"Circuit breaker OPEN for host '{host}' (cooldown remaining: {round(info.cooldown_seconds - elapsed, 1)}s)",
                )
            return (True, "OK")

    def record_success(self, host: str) -> None:
        """Record successful response (resets failures and moves to CLOSED)."""
        with self._lock:
            info = self._get_host_info(host)
            info.consecutive_failures = 0
            info.state = CircuitState.CLOSED
            info.last_state_change = time.monotonic()
            info.last_error = None

    def record_failure(self, host: str, error_reason: str | None = None) -> None:
        """Record upstream error; trips to OPEN if failure_threshold reached."""
        with self._lock:
            info = self._get_host_info(host)
            info.consecutive_failures += 1
            info.last_error = error_reason
            now = time.monotonic()
            if info.state == CircuitState.HALF_OPEN:
                info.state = CircuitState.OPEN
                info.last_state_change = now
            elif info.consecutive_failures >= info.failure_threshold:
                info.state = CircuitState.OPEN
                info.last_state_change = now

    def get_status(self) -> dict[str, Any]:
        """Diagnostic snapshot of all host circuits."""
        with self._lock:
            return {
                host: {
                    "state": info.state.value,
                    "consecutive_failures": info.consecutive_failures,
                    "last_error": info.last_error,
                }
                for host, info in self._hosts.items()
            }


class HttpTrafficGovernor:
    """Combined TokenBucket Rate Limiter and Circuit Breaker for HTTP clients."""

    def __init__(
        self,
        default_rate: float = 10.0,
        default_capacity: float = 20.0,
        failure_threshold: int = 3,
        cooldown_seconds: float = 60.0,
    ) -> None:
        self.default_rate = default_rate
        self.default_capacity = default_capacity
        self.circuit_breaker = CircuitBreaker(failure_threshold, cooldown_seconds)
        self._buckets: dict[str, TokenBucket] = {}
        self._lock = threading.Lock()

    def _get_bucket(self, host: str) -> TokenBucket:
        with self._lock:
            if host not in self._buckets:
                self._buckets[host] = TokenBucket(
                    rate=self.default_rate, capacity=self.default_capacity
                )
            return self._buckets[host]

    def acquire(self, host: str, timeout: float = 2.0) -> tuple[bool, str]:
        can_go, reason = self.circuit_breaker.can_request(host)
        if not can_go:
            return (False, reason)
        bucket = self._get_bucket(host)
        if not bucket.acquire(1.0, timeout=timeout):
            return (False, f"Rate limit token exhausted for host '{host}'")
        return (True, "OK")

    def record_success(self, host: str) -> None:
        self.circuit_breaker.record_success(host)

    def record_failure(self, host: str, error_reason: str | None = None) -> None:
        self.circuit_breaker.record_failure(host, error_reason)


GLOBAL_TRAFFIC_GOVERNOR = HttpTrafficGovernor()
