def test_legacy_request_type_is_the_same_parser_and_round_trips_extension_options():
    from company_intel.report_request import ReportRequest as LegacyRequest
    from cil_contracts.requests import ReportRequest
    assert LegacyRequest is ReportRequest
    raw = {'purpose': ['financial'], 'question': '비교', 'as_of': '2026-10-20T00:00:00Z', 'financial_spec': {'entity_ids': ['example']}, 'argument_origins': [{'json_pointer': '/', 'origin': 'user_explicit'}]}
    parsed = LegacyRequest.from_dict(raw)
    assert ReportRequest.from_dict(parsed.as_dict()).request_hash == parsed.request_hash
