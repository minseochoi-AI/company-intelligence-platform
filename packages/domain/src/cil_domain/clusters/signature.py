"""Canonical responsibility owner; migrated from src/company_intel/classification.py."""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ClusterSignature:
    """5-level composable cluster signature for macro roll-up and micro cohort drill-down.

    Key structure: <Region>:<Sector>:<Tier>:<Contract>:<Workplace>
    Wildcard: 'ALL' matches any value in that level.
    """

    region: str = "ALL"
    sector: str = "ALL"
    tier: str = "ALL"
    contract: str = "ALL"
    workplace: str = "ALL"

    def __post_init__(self) -> None:
        if any(
            not isinstance(v, str) or not v or ":" in v
            for v in (
                self.region,
                self.sector,
                self.tier,
                self.contract,
                self.workplace,
            )
        ):
            raise ValueError("signature requires five nonempty dimensions")

    @property
    def key(self) -> str:
        return (
            f"{self.region}:{self.sector}:{self.tier}:{self.contract}:{self.workplace}"
        )

    def matches(self, other: ClusterSignature) -> bool:
        """The query is self. Unknown source dimensions never establish a match."""
        for field in ("region", "sector", "tier", "contract", "workplace"):
            v1, v2 = (getattr(self, field), getattr(other, field))
            if v1 != "ALL" and (v2 in {"ALL", "UNKNOWN", "unknown"} or v1 != v2):
                return False
        return True

    @classmethod
    def parse(cls, key_str: str) -> ClusterSignature:
        if (
            not isinstance(key_str, str)
            or len(key_str.split(":")) != 5
            or any(not p.strip() for p in key_str.split(":"))
        ):
            raise ValueError("signature requires exactly five nonempty dimensions")
        parts = key_str.split(":")
        region = parts[0] if len(parts) > 0 and parts[0] else "ALL"
        sector = parts[1] if len(parts) > 1 and parts[1] else "ALL"
        tier = parts[2] if len(parts) > 2 and parts[2] else "ALL"
        contract = parts[3] if len(parts) > 3 and parts[3] else "ALL"
        workplace = parts[4] if len(parts) > 4 and parts[4] else "ALL"
        return cls(
            region=region,
            sector=sector,
            tier=tier,
            contract=contract,
            workplace=workplace,
        )
