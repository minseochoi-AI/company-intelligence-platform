"""Deterministic XLSX projection. No network, databases, models or application IO."""

from __future__ import annotations
from io import BytesIO
from typing import Any
from xml.sax.saxutils import escape, quoteattr
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
import hashlib
import json
import math
import re

from cil_contracts.requests import canonical_bytes
from cil_contracts.sealed_research_bundle import WorkbookBuild

NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"


def _column(number: int) -> str:
    result = ""
    while number:
        number, part = divmod(number - 1, 26)
        result = chr(65 + part) + result
    return result


def _text(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _cell(address: str, value: Any, style: int = 1) -> str:
    if type(value) in (int, float):
        if not math.isfinite(value):
            raise ValueError("non-finite workbook value")
        return f'<c r="{address}" s="{style}" t="n"><v>{value}</v></c>'
    text = _text(value)
    # XML 1.0 control characters are encoded as OOXML escaped literals.
    text = re.sub(
        r"[\x00-\x08\x0b\x0c\x0e-\x1f]", lambda m: f"_x{ord(m[0]):04X}_", text
    )
    return f'<c r="{address}" s="{style}" t="inlineStr"><is><t xml:space="preserve">{escape(text)}</t></is></c>'


def render_research_workbook(
    tables: dict[str, list[dict[str, Any]]], *, max_rows_per_sheet: int = 1_048_575
) -> WorkbookBuild:
    if not 1 <= max_rows_per_sheet <= 1_048_575:
        raise ValueError("invalid XLSX sheet row capacity")
    files: dict[str, str] = {}
    sheets, cell_refs, overflows = [], [], {}
    names = set()
    for table_id, rows in tables.items():
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            raise ValueError("workbook datasets must be arrays of objects")
        columns = sorted({key for row in rows for key in row}) or [
            "_row_id",
            "status",
            "reason",
        ]
        if "_row_id" in columns:
            columns.remove("_row_id")
            columns.insert(0, "_row_id")
        row_ids = [
            row.get(
                "_row_id",
                hashlib.sha256(canonical_bytes([table_id, i, row])).hexdigest()[:20],
            )
            for i, row in enumerate(rows)
        ]
        if len(row_ids) != len(set(row_ids)):
            raise ValueError("duplicate dataset row identity")
        for offset in range(0, max(len(rows), 1), max_rows_per_sheet):
            page = offset // max_rows_per_sheet + 1
            suffix = "" if page == 1 else f"_{page}"
            name = re.sub(r"[\[\]:*?/\\]", "_", table_id)[: 31 - len(suffix)] + suffix
            if not name or name in names:
                raise ValueError("workbook sheet identity collision")
            names.add(name)
            sheet_index = len(sheets) + 1
            sheets.append((name, sheet_index))
            parts = [
                f'<worksheet xmlns="{NS}" xmlns:r="{REL}">',
                '<sheetViews><sheetView workbookViewId="0"><pane xSplit="2" ySplit="1" topLeftCell="C2" activePane="bottomRight" state="frozen"/></sheetView></sheetViews>',
                '<sheetFormatPr defaultRowHeight="32"/><cols>',
            ]
            parts.extend(
                f'<col min="{i}" max="{i}" width="{32 if i <= 2 else 48}" customWidth="1"/>'
                for i in range(1, len(columns) + 1)
            )
            parts += [
                '</cols><sheetData><row r="1">',
                *[_cell(_column(i) + "1", col, 2) for i, col in enumerate(columns, 1)],
                "</row>",
            ]
            links = []
            for j, row in enumerate(rows[offset : offset + max_rows_per_sheet], 2):
                row_id = row_ids[offset + j - 2]
                parts.append(f'<row r="{j}" ht="48" customHeight="1">')
                for k, column in enumerate(columns, 1):
                    address = _column(k) + str(j)
                    value = row.get(column)
                    if len(_text(value)) > 32767:
                        pointer = f"{table_id}/{row_id}/{column}"
                        overflows[pointer] = _text(value)
                        value = (
                            "@overflow:" + hashlib.sha256(pointer.encode()).hexdigest()
                        )
                    parts.append(_cell(address, value))
                    cell_refs.append(
                        {
                            "table_id": table_id,
                            "row_id": row_id,
                            "column_id": column,
                            "sheet": name,
                            "cell": address,
                        }
                    )
                    if isinstance(value, str) and re.fullmatch(
                        r"https?://[^\s]+", value
                    ):
                        links.append((address, value))
                parts.append("</row>")
            parts.append("</sheetData>")
            end = len(rows[offset : offset + max_rows_per_sheet]) + 1
            parts.append(f'<autoFilter ref="A1:{_column(len(columns))}{end}"/>')
            if links:
                parts.append("<hyperlinks>")
                parts.extend(
                    f'<hyperlink ref="{address}" r:id="rId{i}"/>'
                    for i, (address, _) in enumerate(links, 1)
                )
                parts.append("</hyperlinks>")
                files[f"xl/worksheets/_rels/sheet{sheet_index}.xml.rels"] = (
                    f'<Relationships xmlns="{PKG_REL}">'
                    + "".join(
                        f'<Relationship Id="rId{i}" Type="{REL}/hyperlink" Target={quoteattr(url)} TargetMode="External"/>'
                        for i, (_, url) in enumerate(links, 1)
                    )
                    + "</Relationships>"
                )
            parts.append("</worksheet>")
            files[f"xl/worksheets/sheet{sheet_index}.xml"] = "".join(parts)
    files["xl/workbook.xml"] = (
        f'<workbook xmlns="{NS}" xmlns:r="{REL}"><sheets>'
        + "".join(
            f'<sheet name={quoteattr(name)} sheetId="{i}" r:id="rId{i}"/>'
            for name, i in sheets
        )
        + "</sheets></workbook>"
    )
    files["xl/_rels/workbook.xml.rels"] = (
        f'<Relationships xmlns="{PKG_REL}">'
        + "".join(
            f'<Relationship Id="rId{i}" Type="{REL}/worksheet" Target="worksheets/sheet{i}.xml"/>'
            for _, i in sheets
        )
        + f'<Relationship Id="styles" Type="{REL}/styles" Target="styles.xml"/></Relationships>'
    )
    files["_rels/.rels"] = (
        f'<Relationships xmlns="{PKG_REL}"><Relationship Id="workbook" Type="{REL}/officeDocument" Target="xl/workbook.xml"/></Relationships>'
    )
    files["xl/styles.xml"] = (
        f'''<styleSheet xmlns="{NS}"><fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts><fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills><borders count="1"><border/></borders><cellStyleXfs count="1"><xf/></cellStyleXfs><cellXfs count="3"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/><xf numFmtId="0" fontId="0" fillId="0" borderId="0" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf><xf numFmtId="0" fontId="1" fillId="0" borderId="0" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>'''
    )
    files["[Content_Types].xml"] = (
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        + "".join(
            f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            for _, i in sheets
        )
        + "</Types>"
    )
    stream = BytesIO()
    with ZipFile(stream, "w", compression=ZIP_DEFLATED) as archive:
        for path, content in sorted(files.items()):
            info = ZipInfo(path, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, content.encode("utf-8"))
    return WorkbookBuild(stream.getvalue(), tuple(cell_refs), overflows)
