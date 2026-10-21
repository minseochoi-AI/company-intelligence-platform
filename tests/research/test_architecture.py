"""Ownership assertions complement runtime tests; they do not prove all dispatch."""

import ast
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def architecture_findings(root):
    global ROOT
    assert root == ROOT
    allowed = {
        "contracts": {"cil_contracts"},
        "domain": {"cil_contracts", "cil_domain"},
        "application": {"cil_contracts", "cil_domain", "cil_application"},
        "reporting": {"cil_contracts", "cil_domain", "cil_reporting"},
        "integrations": {
            "cil_contracts",
            "cil_domain",
            "cil_application",
            "cil_integrations",
        },
    }
    problems = []
    for owner, internal in allowed.items():
        for path in (ROOT / "packages" / owner / "src").rglob("*.py"):
            for node in ast.walk(ast.parse(path.read_text())):
                names = (
                    ([node.module] if node.module else [])
                    if isinstance(node, ast.ImportFrom)
                    else [n.name for n in node.names]
                    if isinstance(node, ast.Import)
                    else []
                )
                for name in names:
                    top = name.split(".")[0]
                    if (
                        top.startswith(("cil_", "company_intel"))
                        and top not in internal
                    ):
                        problems.append((str(path.relative_to(ROOT)), name))
                    if (
                        owner == "contracts"
                        and top
                        not in sys.stdlib_module_names | internal | {"__future__"}
                    ):
                        problems.append((str(path.relative_to(ROOT)), name))
            assert "sys.path.insert" not in path.read_text()
    return problems


def test_compatibility_types_share_canonical_identity():
    pairs = [
        ("company_intel.classification", "CanonicalJobRecord", "cil_contracts.jobs"),
        (
            "company_intel.classification",
            "ClusterSignature",
            "cil_domain.clusters.signature",
        ),
        ("company_intel.config", "Settings", "cil_integrations.runtime.settings"),
        ("company_intel.api", "app", "cil_api.app"),
        ("company_intel.cli", "main", "cil_cli.main"),
        ("company_intel.report_request", "ReportRequest", "cil_contracts.requests"),
    ]
    for old, symbol, new in pairs:
        assert getattr(importlib.import_module(old), symbol) is getattr(
            importlib.import_module(new), symbol
        )


def test_internal_consumers_do_not_use_compatibility_or_source_path_injection():
    for group in ("packages", "apps", "scripts"):
        paths = (ROOT / group).rglob("*.py")
        for path in paths:
            if "build" in path.parts:
                continue
            text = path.read_text()
            tree = ast.parse(text)
            assert not any(
                isinstance(n, ast.ImportFrom)
                and (n.module or "").startswith("company_intel")
                for n in ast.walk(tree)
            ), str(path)
            assert "sys.path.insert" not in text, str(path)


def test_dependency_direction_and_contract_standard_library_boundary(proof):
    assert (
        proof.invoke(
            "MR-D07-contract",
            architecture_findings,
            ROOT,
            checks={
                "input": lambda b, a, r, e: (
                    b["args"][0] == ROOT
                    and (ROOT / "packages/contracts/src/cil_contracts").is_dir()
                ),
                "return": lambda b, a, r, e: e is None and r == [],
                "relation": lambda b, a, r, e: (
                    r == []
                    and (
                        ROOT
                        / "packages/application/src/cil_application/ports/__init__.py"
                    ).is_file()
                ),
            },
        )
        == []
    )
