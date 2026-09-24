#!/usr/bin/env python3
"""
Maintenance script: rebuild the embedded Word version of the Membership certificate.

Run it only after replacing "Certificate - Kenyon - Template.pdf", so the Word
file picks up the new artwork. It is not part of generating certificates for
users, and it writes nothing outside this skill folder and a temporary folder.

    python3 build_word_template.py      (needs: pip install python-docx)

Background = page 5 of the burned-in template with its placeholders cleared,
dropped in at full bleed. Name and Date sit on top as editable text boxes,
positioned from the same coordinates the PDF generator reads off the template.
"""

import os
import sys
import tempfile

import fitz
from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION_START
from docx.oxml import parse_xml
from docx.shared import Pt

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SKILL_DIR)
import fill_certificate as fc  # noqa: E402

DPI     = 300
EMU_PT  = 12700

SAPPHIRE_HEX = "005CA7"
FONT_NAME    = "Titillium Web"

# Word puts the first baseline one ascent below the text-box top.
ASCENT_RATIO = 1.133  # Titillium Web hhea ascent / unitsPerEm

NS = (
    'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
    'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
    'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture" '
    'xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape"'
)


def emu(points):
    return int(round(points * EMU_PT))


def clean_background(page_idx, out_png):
    """Render the template page with its fill-in placeholders removed."""
    layout = fc._read_layout(page_idx)
    doc  = fitz.open(fc.TEMPLATE)
    page = doc[page_idx]
    for spec in layout.values():
        page.add_redact_annot(spec["rect"], fill=fc.NO_FILL)
    page.apply_redactions(
        images=fitz.PDF_REDACT_IMAGE_NONE,
        graphics=fitz.PDF_REDACT_LINE_ART_NONE,
    )
    page.get_pixmap(dpi=DPI).save(out_png)
    rect = fitz.Rect(page.rect)
    doc.close()
    return layout, rect


def background_xml(rid, page_rect):
    """Full-bleed picture, anchored to the page corner, behind the text."""
    cx, cy = emu(page_rect.width), emu(page_rect.height)
    return parse_xml(
        f'<w:p {NS}><w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/>'
        f'<w:rPr><w:sz w:val="2"/></w:rPr></w:pPr><w:r><w:drawing>'
        f'<wp:anchor distT="0" distB="0" distL="0" distR="0" simplePos="0" relativeHeight="1" '
        f'behindDoc="1" locked="0" layoutInCell="1" allowOverlap="1">'
        f'<wp:simplePos x="0" y="0"/>'
        f'<wp:positionH relativeFrom="page"><wp:posOffset>0</wp:posOffset></wp:positionH>'
        f'<wp:positionV relativeFrom="page"><wp:posOffset>0</wp:posOffset></wp:positionV>'
        f'<wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
        f'<wp:wrapNone/><wp:docPr id="100" name="Certificate background"/>'
        f'<wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>'
        f'<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        f'<pic:pic><pic:nvPicPr><pic:cNvPr id="100" name="Certificate background"/><pic:cNvPicPr/></pic:nvPicPr>'
        f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
        f'</pic:pic></a:graphicData></a:graphic></wp:anchor></w:drawing></w:r></w:p>'
    )


def textbox_xml(shape_id, name, spec, runs, width_pt, page_rect):
    """
    Floating, transparent text box whose first baseline lands on the
    template's own baseline for that field.
    """
    size   = spec["size"]
    left   = spec["x"]
    top    = spec["baseline"] - ASCENT_RATIO * size
    height = size * 1.6
    half   = int(round(size * 2))  # w:sz is in half-points

    run_xml = ""
    for text, superscript in runs:
        va = '<w:vertAlign w:val="superscript"/>' if superscript else ""
        run_xml += (
            f'<w:r><w:rPr>'
            f'<w:rFonts w:ascii="{FONT_NAME}" w:hAnsi="{FONT_NAME}" w:cs="{FONT_NAME}"/>'
            f'<w:color w:val="{SAPPHIRE_HEX}"/><w:sz w:val="{half}"/><w:szCs w:val="{half}"/>{va}'
            f'</w:rPr><w:t xml:space="preserve">{text}</w:t></w:r>'
        )

    return parse_xml(
        f'<w:p {NS}><w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/>'
        f'<w:rPr><w:sz w:val="2"/></w:rPr></w:pPr><w:r><w:drawing>'
        f'<wp:anchor distT="0" distB="0" distL="0" distR="0" simplePos="0" relativeHeight="{shape_id}" '
        f'behindDoc="0" locked="0" layoutInCell="1" allowOverlap="1">'
        f'<wp:simplePos x="0" y="0"/>'
        f'<wp:positionH relativeFrom="page"><wp:posOffset>{emu(left)}</wp:posOffset></wp:positionH>'
        f'<wp:positionV relativeFrom="page"><wp:posOffset>{emu(top)}</wp:posOffset></wp:positionV>'
        f'<wp:extent cx="{emu(width_pt)}" cy="{emu(height)}"/>'
        f'<wp:effectExtent l="0" t="0" r="0" b="0"/><wp:wrapNone/>'
        f'<wp:docPr id="{shape_id}" name="{name}"/><wp:cNvGraphicFramePr/>'
        f'<a:graphic><a:graphicData uri="http://schemas.microsoft.com/office/word/2010/wordprocessingShape">'
        f'<wps:wsp><wps:cNvSpPr txBox="1"/>'
        f'<wps:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{emu(width_pt)}" cy="{emu(height)}"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></wps:spPr>'
        f'<wps:txbx><w:txbxContent>'
        f'<w:p><w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr>{run_xml}</w:p>'
        f'</w:txbxContent></wps:txbx>'
        f'<wps:bodyPr rot="0" spcFirstLastPara="0" vertOverflow="overflow" horzOverflow="overflow" '
        f'vert="horz" wrap="square" lIns="0" tIns="0" rIns="0" bIns="0" numCol="1" anchor="t" '
        f'anchorCtr="0" upright="0"><a:noAutofit/></wps:bodyPr>'
        f'</wps:wsp></a:graphicData></a:graphic></wp:anchor></w:drawing></w:r></w:p>'
    )


def build(out_docx, name_text="[Full Name]", date_runs=(("[Member since date]", False),)):
    png = os.path.join(tempfile.mkdtemp(), "membership-bg.png")
    layout, page_rect = clean_background(fc.PAGE_INDEX["membership"], png)

    document = Document()
    section = document.sections[0]
    section.start_type      = WD_SECTION_START.NEW_PAGE
    section.orientation     = WD_ORIENT.LANDSCAPE
    section.page_width      = Pt(page_rect.width)
    section.page_height     = Pt(page_rect.height)
    for attr in ("left_margin", "right_margin", "top_margin", "bottom_margin",
                 "header_distance", "footer_distance", "gutter"):
        setattr(section, attr, Pt(0))

    # Background lives in the header so it cannot be nudged while typing.
    header = section.header
    header.is_linked_to_previous = False
    rid, _ = header.part.get_or_add_image(png)
    header_p = header.paragraphs[0]._p
    header_p.addnext(background_xml(rid, page_rect))
    header_p.getparent().remove(header_p)

    body_p = (document.paragraphs[0] if document.paragraphs else document.add_paragraph())._p
    right_bound = fc.RIGHT_BOUND

    name_box = textbox_xml(101, "Name", layout["name"],
                           [(name_text, False)],
                           right_bound - layout["name"]["x"], page_rect)
    date_box = textbox_xml(102, "Date", layout["date"],
                           list(date_runs),
                           right_bound - layout["date"]["x"], page_rect)
    body_p.addprevious(name_box)
    body_p.addprevious(date_box)

    pPr = parse_xml(f'<w:pPr {NS}><w:spacing w:after="0" w:line="240" w:lineRule="auto"/>'
                    f'<w:rPr><w:sz w:val="2"/></w:rPr></w:pPr>')
    body_p.insert(0, pPr)

    document.save(out_docx)
    return out_docx, layout


if __name__ == "__main__":
    path, layout = build(fc.WORD_TEMPLATE)
    print("saved:", path)
    for k, v in layout.items():
        print(f"  {k}: x={v['x']:.1f} baseline={v['baseline']:.1f} size={v['size']}")
