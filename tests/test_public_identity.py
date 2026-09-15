from company_intel.public_identity import link_mpm_alio, link_mpsv_ares


def test_mpsv_ico_exact_ares_join() -> None:
    link = link_mpsv_ares({"ico": "12345678"}, {"ico": "12345678"})
    assert link.status == "linked"
    assert link.method == "ico_exact"


def test_mpm_name_candidate_is_not_auto_linked() -> None:
    link = link_mpm_alio({"institution_name": "기관 A"}, {"title": "기관 A"})
    assert link.status == "candidate"
    assert link.canonical_entity_id is None


def test_conflicting_ico_is_preserved() -> None:
    assert link_mpsv_ares({"ico": "1"}, {"ico": "2"}).status == "conflict"
