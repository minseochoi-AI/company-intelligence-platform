import pytest


def test_missing_key_error_and_empty_response_never_become_fixtures(monkeypatch, proof):
    from cil_integrations.providers.koneps.procurements import (
        KONEPSProcurementConnector,
    )

    for name in ("KONEPS_API_KEY", "DATA_GO_KR_API_KEY", "nomal"):
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(ValueError, match="key"):
        KONEPSProcurementConnector().search_procurements()
    connector = KONEPSProcurementConnector(service_key="fake")
    assert (
        proof.invoke(
            "AR-D08-contract",
            connector._parse_koneps_xml,
            b"<response><header><resultCode>00</resultCode></header><body><items/></body></response>",
            checks={
                "input": lambda b, a, r, e: b"<items/>" in b["args"][0],
                "return": lambda b, a, r, e: e is None and isinstance(r, list),
                "relation": lambda b, a, r, e: (
                    r == [] and b"<resultCode>00</resultCode>" in b["args"][0]
                ),
            },
        )
        == []
    )
    with pytest.raises(ValueError, match="response"):
        connector._parse_koneps_xml(b"not xml")
