import json


def test_minimal_routes_and_public_cli_saved_run(tmp_path, capsys, proof):
    from cil_application.research.request_compiler import selected_skills
    from cil_cli.main import main

    assert proof.invoke(
        "SK-D01-contract",
        selected_skills,
        ["financial"],
        checks={
            "input": lambda b, a, r, e: b["args"] == (["financial"],),
            "return": lambda b, a, r, e: e is None and r == ["S01", "S03", "S08"],
            "relation": lambda b, a, r, e: "S02" not in r and "S03" in r,
        },
    ) == ["S01", "S03", "S08"]
    request = {
        "purpose": ["financial"],
        "question": "증거 공백 확인",
        "as_of": "2026-10-20T00:00:00Z",
        "argument_origins": [{"json_pointer": "/", "origin": "user_explicit"}],
    }
    (tmp_path / "request.json").write_text(json.dumps(request))
    (tmp_path / "snapshot.json").write_text(
        json.dumps({"source_kind": "fixture", "postings": []})
    )
    code = main(
        [
            "research",
            "run",
            "--request",
            str(tmp_path / "request.json"),
            "--snapshot",
            str(tmp_path / "snapshot.json"),
            "--output",
            str(tmp_path / "runs"),
        ]
    )
    assert code == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "PARTIAL"
    assert (tmp_path / "runs" / result["run_id"] / "research.xlsx").is_file()


def test_api_saved_run_and_unknown_request_field(tmp_path, monkeypatch):
    import asyncio
    from cil_api.app import app

    monkeypatch.setenv("CIL_RESEARCH_ARTIFACT_ROOT", str(tmp_path))

    def post(payload):
        messages = []

        async def receive():
            return {
                "type": "http.request",
                "body": json.dumps(payload).encode(),
                "more_body": False,
            }

        async def send(message):
            messages.append(message)

        scope = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "method": "POST",
            "path": "/research/runs",
            "raw_path": b"/research/runs",
            "query_string": b"",
            "headers": [(b"content-type", b"application/json")],
            "scheme": "http",
            "server": ("test", 80),
            "client": ("test", 123),
        }
        asyncio.run(app(scope, receive, send))
        return messages[0]["status"], json.loads(
            b"".join(m.get("body", b"") for m in messages[1:])
        )

    request = {
        "purpose": ["financial"],
        "question": "비교",
        "as_of": "2026-10-20T00:00:00Z",
        "argument_origins": [{"json_pointer": "/", "origin": "user_explicit"}],
    }
    payload = {
        "request": request,
        "snapshot": {"source_kind": "fixture", "postings": []},
    }
    status, response = post(payload)
    assert status == 200
    assert response["source_kind"] == "fixture"
    payload["request"]["ignored"] = True
    assert post(payload)[0] == 422
