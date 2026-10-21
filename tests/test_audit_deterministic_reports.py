def test_arbitrary_workbook_is_not_certified_from_its_own_cells(tmp_path):
    import openpyxl
    from cil_integrations.validation.workbooks import ExcelProvenanceValidator
    workbook = openpyxl.Workbook()
    workbook.active.append(['job_id', 'claimed_status'])
    workbook.active.append(['invented', 'PASS'])
    path = tmp_path / 'unknown.xlsx'
    workbook.save(path)
    result = ExcelProvenanceValidator(path, project_root=tmp_path, raw_structure_path=tmp_path/'absent', atomic_tasks_path=tmp_path/'absent', market_registry_path=tmp_path/'absent').verify_all_matrices()
    assert result.passed_matrices == 0
    assert all(matrix.status == 'UNVERIFIED' for matrix in result.matrix_results)
