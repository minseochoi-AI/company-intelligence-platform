import pytest

from cil_domain.taxonomy.tree import SelectionSession, advance_selection, backtrack_selection, branches_for_selection, preview_selection


def test_counts_recompute_after_selection_and_backtracking() -> None:
    rows = [{"country": "KR", "job": "data"}, {"country": "CZ", "job": "data"}, {"country": "KR", "job": "legal"}]
    session = advance_selection(SelectionSession("current_jobs"), rows, "country", "KR")
    assert preview_selection(rows, session)["count"] == 2
    assert {branch.value for branch in branches_for_selection(rows, session, "job")} == {"data", "legal"}
    assert backtrack_selection(session).selections == ()


def test_disabled_branch_is_not_compiled() -> None:
    with pytest.raises(ValueError, match="invalid_selection"):
        advance_selection(SelectionSession(), [{"country": "KR"}], "country", "CZ")
