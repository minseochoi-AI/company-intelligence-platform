from datetime import date
import pytest


def test_missing_deadline_and_missing_reference_never_claim_live(proof):
    from cil_domain.jobs.freshness import FreshnessPolicy

    assert (
        proof.invoke(
            "AR-D06-contract",
            FreshnessPolicy.compute_freshness,
            None,
            reference_date=date(2026, 10, 20),
            checks={
                "input": lambda b, a, r, e: (
                    b["args"][0] is None
                    and b["kwargs"]["reference_date"] == date(2026, 10, 20)
                ),
                "return": lambda b, a, r, e: e is None and r == "UNKNOWN",
                "relation": lambda b, a, r, e: (
                    r != "LIVE_ACTIVE" and b["args"][0] is None
                ),
            },
        )
        == "UNKNOWN"
    )
    assert (
        FreshnessPolicy.compute_freshness("상시채용", reference_date=date(2026, 10, 20))
        == "OPEN_ENDED_UNVERIFIED"
    )
    with pytest.raises(ValueError, match="reference"):
        FreshnessPolicy.compute_freshness("2026-12-31")
