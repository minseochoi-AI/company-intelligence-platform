def test_collection_requires_explicit_authority_and_reports_empty_error_and_partial(
    proof,
):
    from cil_application.collection.service import CollectionService

    class Source:
        def __init__(self):
            self.calls = 0

        def fetch_page(self, parameters, cursor):
            self.calls += 1
            return {"records": [], "payload": {}, "next_cursor": "next"}

    source = Source()
    service = CollectionService()
    assert (
        proof.invoke(
            "AR-D04-contract",
            service.collect,
            source,
            {},
            checks={
                "input": lambda b, a, r, e: (
                    b["args"][1] == {} and not b["kwargs"].get("authorized", False)
                ),
                "return": lambda b, a, r, e: (
                    e is None and r["status"] == "NEEDS_AUTHORIZATION"
                ),
                "relation": lambda b, a, r, e: (
                    r["provider_calls"] == 0 and b["state"] == a["state"] == 0
                ),
            },
            observe=lambda: source.calls,
        )["status"]
        == "NEEDS_AUTHORIZATION"
    )
    assert source.calls == 0
    result = service.collect(source, {}, authorized=True, max_pages=1)
    assert result["status"] == "PARTIAL" and result["complete"] is False

    class Broken:
        def fetch_page(self, parameters, cursor):
            raise OSError("secret")

    result = service.collect(Broken(), {}, authorized=True)
    assert result["status"] == "ERROR" and "secret" not in str(result)
