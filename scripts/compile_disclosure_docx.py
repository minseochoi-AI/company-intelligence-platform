"""
Script: compile_disclosure_docx.py
Purpose: Compile the technical disclosure markdown into a professional DOCX artifact
using Python standard library (zipfile, ElementTree) and valid OpenXML schema.
"""

import os
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT_ROOT = Path('/home/ubuntu/root/company-intelligence-platform')
MD_PATH = PROJECT_ROOT / 'docs/원자력_기저부하_섹터커플링_멀티에이전트_기술교대서_20261016.md'
DOCX_OUT = PROJECT_ROOT / 'docs/원자력_기저부하_섹터커플링_멀티에이전트_기술교대서_20261016.docx'
TEMPLATE_DOCX = PROJECT_ROOT / 'docs/99. 진로계획서_backup.docx'

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ET.register_namespace('w', W_NS)


def make_p(text: str, bold=False, size_pt=10, align='left', color=None, space_after=80, italic=False):
    p = ET.Element(f'{{{W_NS}}}p')
    pPr = ET.SubElement(p, f'{{{W_NS}}}pPr')
    if align != 'left':
        jc = ET.SubElement(pPr, f'{{{W_NS}}}jc')
        jc.attrib[f'{{{W_NS}}}val'] = align
    sp = ET.SubElement(pPr, f'{{{W_NS}}}spacing')
    sp.attrib[f'{{{W_NS}}}after'] = str(space_after)
    sp.attrib[f'{{{W_NS}}}line'] = '240'
    sp.attrib[f'{{{W_NS}}}lineRule'] = 'auto'

    r = ET.SubElement(p, f'{{{W_NS}}}r')
    rPr = ET.SubElement(r, f'{{{W_NS}}}rPr')
    fonts = ET.SubElement(rPr, f'{{{W_NS}}}rFonts')
    fonts.attrib[f'{{{W_NS}}}ascii'] = 'Malgun Gothic'
    fonts.attrib[f'{{{W_NS}}}eastAsia'] = 'Malgun Gothic'
    fonts.attrib[f'{{{W_NS}}}hAnsi'] = 'Malgun Gothic'
    if bold:
        ET.SubElement(rPr, f'{{{W_NS}}}b')
    if italic:
        ET.SubElement(rPr, f'{{{W_NS}}}i')
    sz = ET.SubElement(rPr, f'{{{W_NS}}}sz')
    sz.attrib[f'{{{W_NS}}}val'] = str(int(size_pt * 2))
    if color:
        c = ET.SubElement(rPr, f'{{{W_NS}}}color')
        c.attrib[f'{{{W_NS}}}val'] = color
    t = ET.SubElement(r, f'{{{W_NS}}}t')
    t.text = text
    return p


def build_docx():
    lines = MD_PATH.read_text(encoding='utf-8').splitlines()

    # Read base template docx to inherit styles and theme
    with zipfile.ZipFile(TEMPLATE_DOCX, 'r') as zin:
        all_files = {item.filename: zin.read(item.filename) for item in zin.infolist()}
        doc_xml = zin.read('word/document.xml')

    tree = ET.fromstring(doc_xml)
    body = tree.find('.//w:body', {'w': W_NS})
    sectPr = body.find('w:sectPr', {'w': W_NS})

    # Clear existing body contents except sectPr
    children = list(body)
    for ch in children:
        if ch != sectPr:
            body.remove(ch)

    # Convert markdown lines to OpenXML paragraphs
    in_code_block = False
    for line in lines:
        s = line.strip()
        if s.startswith('```'):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            body.append(make_p(line, size_pt=8.5, color='333333', space_after=30))
            continue

        if not s:
            continue

        if s.startswith('# '):
            body.append(make_p(s[2:], bold=True, size_pt=16, color='1F4E78', space_after=140))
        elif s.startswith('## '):
            body.append(make_p(s[3:], bold=True, size_pt=13, color='2E75B6', space_after=100))
        elif s.startswith('### '):
            body.append(make_p(s[4:], bold=True, size_pt=11, color='1F4E78', space_after=80))
        elif s.startswith('**') and s.endswith('**'):
            body.append(make_p(s.replace('**', ''), bold=True, size_pt=10, space_after=60))
        elif s.startswith('|') and s.endswith('|'):
            # Table row text
            body.append(make_p(s, size_pt=8.0, space_after=30))
        elif s.startswith('$$') and s.endswith('$$'):
            body.append(make_p(s, bold=True, size_pt=9.5, align='center', color='1F4E78', space_after=80))
        else:
            clean_text = s.replace('**', '').replace('*', '')
            body.append(make_p(clean_text, size_pt=9.5, space_after=60))

    # Re-insert sectPr at the very end
    body.append(sectPr)

    new_xml = ET.tostring(tree, encoding='utf-8', xml_declaration=True)
    all_files['word/document.xml'] = new_xml

    with zipfile.ZipFile(DOCX_OUT, 'w', zipfile.ZIP_DEFLATED) as zout:
        for fname, data in all_files.items():
            zout.writestr(fname, data)

    print(f"Successfully compiled {DOCX_OUT} ({DOCX_OUT.stat().st_size} bytes)")


if __name__ == '__main__':
    build_docx()
