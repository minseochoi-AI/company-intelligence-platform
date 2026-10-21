from cil_contracts.requests import ReportRequest
from cil_application.research.request_compiler import compile_request
from cil_integrations.research.capability_registry import CapabilityRegistry


def test_proposed_private_profile_and_unresolved_reference_require_input():
    request = ReportRequest.from_dict({'purpose': ['financial'], 'question': '비교', 'as_of': '2026-10-20T00:00:00Z', 'profile_ref': 'missing', 'argument_origins': [{'json_pointer': '/', 'origin': 'user_explicit'}, {'json_pointer': '/profile_ref', 'origin': 'ai_proposed'}]})
    result = compile_request(request, {'source_kind': 'fixture'}, CapabilityRegistry())
    assert result['status'] == 'NEEDS_INPUT'
    assert {'proposed_identity_or_eligibility_requires_evidence', 'saved_reference_not_found'} <= {g['reason'] for g in result['gaps']}
