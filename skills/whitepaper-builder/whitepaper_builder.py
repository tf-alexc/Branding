#!/usr/bin/env python3
"""
TrustFlight Whitepaper Builder
Builds a branded whitepaper from the master Whitepaper template.

Usage: python3 whitepaper_builder.py <data.json>

The master template carries the cover layout, TOC layout, body-page header/
footer chrome, and a static back cover. This script:

  1. Opens the template.
  2. Fills the cover placeholders.
  3. Builds the TOC entries.
  4. Emits one section per body page using named styles.
  5. Writes `doc_title` into every body section's footer (bottom-left).
  6. Leaves the final section (back cover) untouched.
"""

import sys
import json
import copy
from pathlib import Path
from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn, nsmap
from docx.oxml import OxmlElement

TEMPLATE = '/Users/alexcraiu/Desktop/Documents/Word templates/Whitepaper Template.docx'

NAVY = '062955'
CYAN = '16C2EE'
AZURE = '479FF8'
INK = '242D41'
RULE_BLUE = '1E5BB5'
CALLOUT_BG = '0A2A5A'
SIDE_CALLOUT_BG = 'E4ECF7'


# ---------------------------------------------------------------------------
# Placeholder replacement (cover + footer)
# ---------------------------------------------------------------------------

def _replace_in_paragraph(paragraph, mapping):
    """Replace {{KEY}} tokens across a paragraph's runs, preserving the first
    run's formatting. Tokens may span multiple runs."""
    text = ''.join(run.text for run in paragraph.runs)
    if not any(f'{{{{{k}}}}}' in text for k in mapping):
        return False
    for key, val in mapping.items():
        text = text.replace(f'{{{{{key}}}}}', val or '')
    for run in paragraph.runs[1:]:
        run.text = ''
    if paragraph.runs:
        paragraph.runs[0].text = text
    else:
        paragraph.add_run(text)
    return True


def replace_in_document_body(doc, mapping):
    for paragraph in doc.paragraphs:
        _replace_in_paragraph(paragraph, mapping)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    _replace_in_paragraph(paragraph, mapping)


def replace_in_headers_footers(doc, mapping, skip_last=True):
    """Replace tokens in headers/footers for every section except the last
    (which is the back cover and must stay intact)."""
    sections = list(doc.sections)
    last_idx = len(sections) - 1
    for i, section in enumerate(sections):
        if skip_last and i == last_idx:
            continue
        for part in (section.header, section.footer,
                     section.first_page_header, section.first_page_footer,
                     section.even_page_header, section.even_page_footer):
            for paragraph in part.paragraphs:
                _replace_in_paragraph(paragraph, mapping)
            for table in part.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for paragraph in cell.paragraphs:
                            _replace_in_paragraph(paragraph, mapping)


# ---------------------------------------------------------------------------
# Document structure
# ---------------------------------------------------------------------------

def _style(doc, name, fallback='Normal'):
    """Return a named style if present, else fall back. Keeps the script
    resilient if the template is missing a style — the visual will be off
    but the build will not crash."""
    try:
        return doc.styles[name]
    except KeyError:
        return doc.styles[fallback]


def find_back_cover_anchor(doc):
    """Locate the first paragraph of the back-cover section so we can insert
    body content BEFORE it. The back cover is the last section; its first
    paragraph is the first body-paragraph after the previous section's sectPr.
    Returns the element to insert before."""
    body = doc.element.body
    children = list(body)
    section_breaks = [el for el in children
                      if el.tag == qn('w:p')
                      and el.find('.//' + qn('w:sectPr')) is not None]
    if not section_breaks:
        return body.find(qn('w:sectPr'))
    last_break = section_breaks[-1]
    idx = children.index(last_break)
    if idx + 1 < len(children):
        return children[idx + 1]
    return body.find(qn('w:sectPr'))


def _new_para(style, text=''):
    p = OxmlElement('w:p')
    pPr = OxmlElement('w:pPr')
    pStyle = OxmlElement('w:pStyle')
    pStyle.set(qn('w:val'), style)
    pPr.append(pStyle)
    p.append(pPr)
    if text:
        r = OxmlElement('w:r')
        t = OxmlElement('w:t')
        t.text = text
        t.set(qn('xml:space'), 'preserve')
        r.append(t)
        p.append(r)
    return p


def _new_section_break(cols=1):
    """Build a paragraph with an embedded sectPr (a section break)."""
    p = OxmlElement('w:p')
    pPr = OxmlElement('w:pPr')
    sectPr = OxmlElement('w:sectPr')
    cols_el = OxmlElement('w:cols')
    cols_el.set(qn('w:num'), str(cols))
    cols_el.set(qn('w:space'), '708')
    sectPr.append(cols_el)
    pPr.append(sectPr)
    p.append(pPr)
    return p


def _page_break_para():
    p = OxmlElement('w:p')
    r = OxmlElement('w:r')
    br = OxmlElement('w:br')
    br.set(qn('w:type'), 'page')
    r.append(br)
    p.append(r)
    return p


# ---------------------------------------------------------------------------
# Body inserter
# ---------------------------------------------------------------------------

class BodyBuilder:
    def __init__(self, doc):
        self.doc = doc
        self.anchor = find_back_cover_anchor(doc)
        self.body = doc.element.body

    def _insert(self, element):
        self.anchor.addprevious(element)

    def para(self, style, text):
        if text is None:
            return
        self._insert(_new_para(style, text))

    def bullet(self, text):
        self._insert(_new_para('Whitepaper Bullet', text))

    def page_break(self):
        self._insert(_page_break_para())

    def image(self, path, width_cm):
        """Insert an image paragraph by going through python-docx, then move
        the new paragraph into position before the anchor."""
        if not path or not Path(path).expanduser().exists():
            return
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(str(Path(path).expanduser()), width=Cm(width_cm))
        self.body.remove(p._p)
        self._insert(p._p)


# ---------------------------------------------------------------------------
# Layout renderers
# ---------------------------------------------------------------------------

def render_toc(bld, entries):
    bld.para('Whitepaper TOC Title', 'Table of Contents')
    for entry in entries:
        line = f"{entry['page']}   {entry['title']}"
        bld.para('Whitepaper TOC Entry', line)
    bld.page_break()


def render_hero(bld, page):
    bld.image(page.get('hero_image'), width_cm=21.0)
    bld.para('Whitepaper Title', page['title'])
    if intro := page.get('intro'):
        bld.para('Whitepaper Lead', intro)
    if subintro := page.get('subintro'):
        bld.para('Whitepaper Body', subintro)
    for text in page.get('body', []):
        bld.para('Whitepaper Body', text)
    if callout := page.get('callout'):
        bld.para('Whitepaper Callout Title', callout['title'])
        bld.para('Whitepaper Callout Body', callout['body'])
    bld.page_break()


def render_content(bld, page):
    if eyebrow := page.get('eyebrow'):
        bld.para('Whitepaper Eyebrow', eyebrow)
    bld.para('Whitepaper Title', page['title'])
    if lead := page.get('lead'):
        bld.para('Whitepaper Lead', lead)
    for text in page.get('body', []):
        bld.para('Whitepaper Body', text)
    for sub in page.get('subsections', []):
        render_subsection(bld, sub)
    bld.page_break()


def render_content_image(bld, page):
    if eyebrow := page.get('eyebrow'):
        bld.para('Whitepaper Eyebrow', eyebrow)
    bld.para('Whitepaper Title', page['title'])
    bld.image(page.get('image'), width_cm=8.5)
    if lead := page.get('lead'):
        bld.para('Whitepaper Lead', lead)
    for text in page.get('body', []):
        bld.para('Whitepaper Body', text)
    for sub in page.get('subsections', []):
        render_subsection(bld, sub)
    bld.page_break()


def render_subsection(bld, sub):
    if sub.get('layout') == 'two_column':
        render_two_column(bld, sub['columns'])
        return
    if heading := sub.get('heading'):
        bld.para('Whitepaper H2', heading)
    if lead := sub.get('lead'):
        bld.para('Whitepaper Lead', lead)
    if intro := sub.get('intro'):
        bld.para('Whitepaper Body', intro)
    for text in sub.get('body', []):
        bld.para('Whitepaper Body', text)
    for text in sub.get('bullets', []):
        bld.bullet(text)


def render_two_column(bld, columns):
    """Render two columns using a two-column section break. Content between
    a column-start break and a column-end break lays out in columns."""
    if len(columns) != 2:
        raise ValueError('two_column layout requires exactly 2 columns')
    bld._insert(_new_section_break(cols=2))
    left, right = columns
    is_side_callout = left.get('side_callout', False)
    for col_idx, col in enumerate((left, right)):
        if col_idx == 0 and is_side_callout:
            if lead := col.get('lead'):
                bld.para('Whitepaper Side Callout Title', lead)
            for text in col.get('body', []):
                bld.para('Whitepaper Side Callout Body', text)
        else:
            if lead := col.get('lead'):
                bld.para('Whitepaper Lead', lead)
            for text in col.get('body', []):
                bld.para('Whitepaper Body', text)
            for text in col.get('bullets', []):
                bld.bullet(text)
        if col_idx == 0:
            # column break
            p = OxmlElement('w:p')
            r = OxmlElement('w:r')
            br = OxmlElement('w:br')
            br.set(qn('w:type'), 'column')
            r.append(br)
            p.append(r)
            bld._insert(p)
    bld._insert(_new_section_break(cols=1))


LAYOUTS = {
    'hero': render_hero,
    'content': render_content,
    'content_image': render_content_image,
}


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build(data):
    doc = Document(TEMPLATE)

    cover = data.get('cover', {})
    doc_title = data.get('doc_title', '')

    replace_in_document_body(doc, {
        'EYEBROW': cover.get('eyebrow', ''),
        'TITLE': cover.get('title', ''),
        'OVERVIEW': cover.get('overview', ''),
        'DATE': cover.get('date', ''),
    })
    replace_in_headers_footers(doc, {'DOC_TITLE': doc_title}, skip_last=True)

    bld = BodyBuilder(doc)

    if toc := data.get('toc'):
        render_toc(bld, toc)

    for page in data.get('pages', []):
        layout = page.get('layout')
        renderer = LAYOUTS.get(layout)
        if renderer is None:
            raise ValueError(f"Unknown layout: {layout!r}. "
                             f"Use one of: {sorted(LAYOUTS)}")
        renderer(bld, page)

    out = data['output_path']
    doc.save(out)
    print(f'Saved: {out}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 whitepaper_builder.py <data.json>')
        sys.exit(1)
    with open(sys.argv[1]) as f:
        build(json.load(f))
