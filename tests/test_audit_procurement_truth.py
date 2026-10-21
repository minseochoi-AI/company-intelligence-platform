import pytest
from cil_integrations.providers.koneps.procurements import KONEPSProcurementConnector


def test_transport_error_is_not_replaced_and_demo_query_no_match_is_empty(monkeypatch):
    import urllib.request
    def fail(*args, **kwargs): raise OSError('transport failure')
    monkeypatch.setattr(urllib.request, 'urlopen', fail)
    with pytest.raises(RuntimeError, match='no fixture fallback'):
        KONEPSProcurementConnector(service_key='fixture-key').search_procurements()
    assert KONEPSProcurementConnector(demo=True).search_procurements('no-such-result-unique') == []
