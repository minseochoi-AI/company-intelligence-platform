import pytest
from cil_integrations.providers.koneps.procurements import KONEPSProcurementConnector


def test_api_status_error_cannot_create_procurement_records():
    connector = KONEPSProcurementConnector(service_key="fixture-key")
    with pytest.raises(ValueError, match="response status"):
        connector._parse_koneps_xml(
            b"<response><header><resultCode>30</resultCode></header><body><items><item><bidNtceNo>fake</bidNtceNo></item></items></body></response>"
        )
