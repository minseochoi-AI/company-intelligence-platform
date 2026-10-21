import json


def test_cluster_export_requires_explicit_snapshot_and_never_falls_back(
    tmp_path, capsys, proof
):
    from cil_cli.main import main

    code = proof.invoke(
        "AR-D01-contract",
        main,
        [
            "export-cluster-jobs",
            "--country",
            "SK",
            "--output",
            str(tmp_path / "jobs.xlsx"),
            "--json-output",
        ],
        checks={
            "input": lambda b, a, r, e: (
                "SK" in b["args"][0] and "--snapshot" not in b["args"][0]
            ),
            "return": lambda b, a, r, e: e is None and r == 2,
            "relation": lambda b, a, r, e: not a["state"] and b["state"] is False,
        },
        observe=lambda: (tmp_path / "jobs.xlsx").exists(),
    )
    assert code != 0
    assert not (tmp_path / "jobs.xlsx").exists()
    assert "NEEDS_INPUT" in capsys.readouterr().out
