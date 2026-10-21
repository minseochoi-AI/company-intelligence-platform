from cil_integrations.providers.job_records import from_kr_public_job_record


def test_raw_nested_fields_are_copied_out_without_loss_or_description_truncation():
    raw = {'idx': 'id', 'url': 'https://example.test/id', 'insttNm': 'Example', 'title': 'Role', 'description': '가' * 1000, 'employment_type': '비정규직', 'salary_min': 0, 'new_field': {'x': [False, None, 0]}}
    record = from_kr_public_job_record(raw)
    serialized = record.to_dict()
    assert serialized['description'] == raw['description'] and serialized['raw_attributes'] == raw
    serialized['raw_attributes']['new_field']['x'].clear()
    assert record.raw_attributes['new_field']['x'] == [False, None, 0]
