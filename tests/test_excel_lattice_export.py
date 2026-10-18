from __future__ import annotations

from pathlib import Path
import openpyxl
import pytest

from company_intel.excel_lattice_export import (
    build_occupational_lattice_workbook,
    load_raw_isco_unit_groups,
)


def test_load_raw_isco_unit_groups():
    groups = load_raw_isco_unit_groups()
    assert len(groups) == 436
    codes = {g["isco_code"] for g in groups}
    assert "2512" in codes  # Software Developers
    assert "2152" in codes  # Electronics Engineers
    assert "1111" in codes  # Legislators
    assert "0110" in codes  # Commissioned Armed Forces


def test_build_occupational_lattice_workbook(tmp_path: Path):
    target_xlsx = tmp_path / "test_occupational_lattice.xlsx"
    out_path = build_occupational_lattice_workbook(target_xlsx)

    assert out_path.exists()
    assert out_path.stat().st_size > 50000

    wb = openpyxl.load_workbook(out_path, data_only=False)
    expected_sheets = [
        "00_Navigator",
        "01_Master_Taxonomy",
        "02_Career_Lattice_DAG",
        "03_Consultant_ValueChain",
        "04_Market_Dynamics_ROI",
        "05_Venture_B2BSaaS",
        "06_Data_Dictionary",
        "07_Time_Series_Warehouse",
        "08_Temporal_Comparative_Table",
        "09_Cross_Elasticity_Trends",
    ]
    assert wb.sheetnames == expected_sheets

    # Verify Master Taxonomy completeness
    ws_tax = wb["01_Master_Taxonomy"]
    assert ws_tax.max_row == 437  # 1 header + 436 ISCO unit groups
    assert ws_tax.max_column == 12

    # Check headers
    headers = [cell.value for cell in ws_tax[1]]
    assert "ISCO_08_Code" in headers
    assert "KR_NCS_Code" in headers
    assert "US_ONET_Code" in headers
    assert "CZ_ISCO_Code" in headers

    # Verify Navigator formulas & links
    ws_nav = wb["00_Navigator"]
    assert "XLOOKUP" in str(ws_nav["D4"].value)
    assert ws_nav["C4"].value == "2512"
    assert ws_nav["C32"].hyperlink is not None

    # Verify DAG sheet
    ws_dag = wb["02_Career_Lattice_DAG"]
    assert ws_dag.max_row >= 28

    # Verify Market sheet
    ws_mkt = wb["04_Market_Dynamics_ROI"]
    assert ws_mkt.max_row >= 40

    # Verify Time Series Warehouse sheet
    ws_ts = wb["07_Time_Series_Warehouse"]
    assert ws_ts.max_row >= 50
    assert ws_ts.cell(row=1, column=1).value == "Category"

    # Verify Temporal Comparative Table sheet
    ws_comp = wb["08_Temporal_Comparative_Table"]
    assert ws_comp.max_row >= 30
    # Check formula in row 6 column 8 (delta) and column 9 (pct change)
    assert "=G6-F6" in str(ws_comp.cell(row=6, column=8).value)
    assert "IFERROR" in str(ws_comp.cell(row=6, column=9).value)

    # Verify Cross Elasticity & Methodologies sheet
    ws_elas = wb["09_Cross_Elasticity_Trends"]
    assert ws_elas.max_row >= 20
    assert "IFERROR" in str(ws_elas.cell(row=6, column=6).value)
    # Check 7 methodologies are listed
    meth_values = [str(ws_elas.cell(row=r, column=3).value) for r in range(17, 24)]
    assert any("상관분석" in v for v in meth_values)
    assert any("고용탄력성" in v for v in meth_values)
    assert any("민감도" in v for v in meth_values)
    assert any("사건연구" in v for v in meth_values)
    assert any("이중차분법" in v for v in meth_values)
    assert any("DCF" in v for v in meth_values)
    assert any("로버스트-Z" in v for v in meth_values)
