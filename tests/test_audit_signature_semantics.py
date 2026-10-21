import pytest
from cil_domain.requests.validation import cohort_verdict, predicate_verdict


def test_missing_or_source_all_is_unknown_and_false_is_distinct_from_zero():
    assert cohort_verdict('KR:PRIVATE:ALL:ALL:ALL', 'KR:ALL:ALL:ALL:ALL') == 'unknown'
    assert predicate_verdict({'flag': False}, {'field_id': 'flag', 'operator': 'eq', 'value': 0}) == 'no_match'
    with pytest.raises(ValueError):
        cohort_verdict('KR:ALL:ALL:ALL:ALL:discarded', 'KR:ALL:ALL:ALL:ALL')
