from cil_cli.guides import guide_payload


def test_cluster_help_has_current_input_requirements_without_fixed_api_claims():
    item = guide_payload('export-cluster-jobs')['명령'][0]
    assert '--snapshot' in item['방식'] and '--as-of' in item['방식']
    item = guide_payload('cluster-spec')['명령'][0]
    assert 'operation' in item['목적'] and '28대' not in item['목적']
