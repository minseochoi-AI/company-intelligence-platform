#!/usr/bin/env python3
"""Compile all domain occupational track lattice diagrams to SVG and PNG using headless mmdc."""
import subprocess
import sys
from pathlib import Path

# Add src to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "src"))

from company_intel.lattice_domains import DOMAIN_REGISTRY, get_domain_graph
from company_intel.track_lattice import TrackLatticeEngine

out_dir = root_dir / ".runtime" / "diagrams"
out_dir.mkdir(parents=True, exist_ok=True)

mmdc_bin = root_dir / "tools" / "mermaid-renderer" / "node_modules" / ".bin" / "mmdc"
puppeteer_config = root_dir / "tools" / "mermaid-renderer" / "puppeteer.local.json"
mermaid_config = root_dir / "tools" / "mermaid-renderer" / "mermaid.config.json"

target_domains = [
    ("ict_data_ai", ""),  # default root names career.svg, etc.
    ("semiconductor_electronics", "semiconductor_"),
    ("mobility_robotics", "mobility_"),
    ("bio_pharma_healthcare", "bio_"),
    ("chemical_battery_energy", "battery_"),
    ("finance_investment_fintech", "finance_"),
    ("management_business_hr", "business_"),
    ("grand_unified", "macro_"),
]

print(f"Compiling diagrams for {len(target_domains)} domains to {out_dir} ...")

for domain_key, prefix in target_domains:
    print(f"\nProcessing domain: {domain_key} (prefix='{prefix}')")
    graph = get_domain_graph(domain_key)
    engine = TrackLatticeEngine(graph)

    projections = {
        "career": engine.project_career_view(),
        "consultant": engine.project_consultant_view(),
        "market": engine.project_market_view(),
        "venture": engine.project_venture_view(),
    }

    for persp, proj in projections.items():
        mmd_path = out_dir / f"{prefix}{persp}.mmd"
        svg_path = out_dir / f"{prefix}{persp}.svg"
        png_path = out_dir / f"{prefix}{persp}.png"

        mmd_path.write_text(proj["mermaid"], encoding="utf-8")

        # Compile SVG
        subprocess.run(
            [
                str(mmdc_bin),
                "-i", str(mmd_path),
                "-o", str(svg_path),
                "-p", str(puppeteer_config),
                "-c", str(mermaid_config),
            ],
            check=True,
            capture_output=True,
        )

        # Compile PNG
        subprocess.run(
            [
                str(mmdc_bin),
                "-i", str(mmd_path),
                "-o", str(png_path),
                "-p", str(puppeteer_config),
                "-c", str(mermaid_config),
                "-w", "1600",
                "-H", "1200",
            ],
            check=True,
            capture_output=True,
        )
        print(f"  [{persp.upper()}] SVG: {svg_path.stat().st_size:,} bytes | PNG: {png_path.stat().st_size:,} bytes")

print("\nAll diagrams successfully compiled!")
