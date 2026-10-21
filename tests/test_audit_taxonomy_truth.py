from cil_domain.taxonomy.mapping import map_occupation


def test_unmapped_and_many_to_many_occupation_relations_are_preserved():
    rows = [{'from_system': 'ISCO', 'from_code': '2512', 'to_system': 'target', 'to_code': x, 'version': 'r1', 'source_id': 'declared', 'relation': 'overlap'} for x in ('A', 'B')]
    assert len(map_occupation('2512', 'ISCO', 'target', rows, version='r1')['mappings']) == 2
    unknown = map_occupation('2512', 'ISCO', 'target', rows, version='r2')
    assert unknown['status'] == 'UNKNOWN' and unknown['mappings'] == []
