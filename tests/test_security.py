from company_intel.security import redact_body, redact_url


def test_url_secrets_are_redacted():
    value = redact_url(
        "https://example.test/path-secret/data?series=x&api_key=secret&UserID=other", ["path-secret"]
    )
    assert "secret" not in value
    assert "other" not in value
    assert value.count("%3Credacted%3E") == 2


def test_json_body_secrets_are_redacted():
    body, changed = redact_body(b'{"Request":{"UserID":"secret"},"value":1}', ["secret"], "application/json")
    assert changed is True
    assert b"secret" not in body
    assert b"redacted" in body


def test_body_without_secret_is_byte_exact():
    original = b'{"compact":true}'
    body, changed = redact_body(original, ["unrelated-secret"], "application/json")
    assert changed is False
    assert body == original
