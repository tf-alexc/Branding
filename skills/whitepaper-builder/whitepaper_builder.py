#!/usr/bin/env python3
"""
TrustFlight Whitepaper Builder

Builds a branded whitepaper PDF from the bundled master template PDF.

Usage: python3 whitepaper_builder.py <data.json>

The template is `Whitepaper Template.pdf` (bundled alongside this script).
It carries 7 layouts (cover, TOC, hero, content, content side-callout,
content with image, back cover). For each requested page, the script:

  1. Copies the matching layout page from the template.
  2. Redacts the placeholder text within the layout's content regions.
  3. Overlays the new content in Open Sans at the brand colours and sizes.
  4. Writes `doc_title` into the bottom-left footer and the page number
     into the bottom-right footer.

The static back cover (page 7) is appended verbatim and never modified.
"""

import json
import sys
from pathlib import Path

import fitz  # PyMuPDF

# ---------------------------------------------------------------------------
# Paths and brand constants
# ---------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / 'Whitepaper Template.pdf'
FONT_FILE = Path('/Users/alexcraiu/Library/Fonts/OpenSans-VariableFont_wdth,wght.ttf')

# Layout index in the bundled template
LAYOUT_PAGE = {
    'cover': 0,
    'toc': 1,
    'hero': 2,
    'content': 3,
    'content_side_callout': 4,
    'content_image': 5,
    'back_cover': 6,
}

# Brand colours (0-1 RGB tuples for PyMuPDF)
def rgb(hex_str):
    h = hex_str.lstrip('#')
    return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))

NAVY = rgb('062955')
INK = rgb('242D41')
CYAN = rgb('16C2EE')
RULE_BLUE = rgb('1E5BB5')
WHITE = rgb('FFFFFF')
CALLOUT_BG = rgb('0A2A5A')
SIDE_CALLOUT_BG = rgb('E4ECF7')
FOOTER_GREY = rgb('7A8AA8')

# Page geometry (US Letter — matches the template's 8.5 x 11 in @ 72dpi)
PAGE_W, PAGE_H = 612, 792

# Content regions — approximate rectangles measured from the template.
# These are the redaction + overlay zones for each layout. Tune in-place
# after running once against a real spec.
REGIONS = {
    'cover': {
        'eyebrow':  fitz.Rect(72, 470, 540, 500),
        'title':    fitz.Rect(72, 500, 540, 620),
        'overview': fitz.Rect(72, 660, 540, 690),
        'date':     fitz.Rect(72, 720, 540, 745),
    },
    'toc': {
        'title':   fitz.Rect(54, 220, 540, 290),
        'entries': fitz.Rect(54, 320, 540, 740),
    },
    'header': {
        'eyebrow_right': fitz.Rect(360, 38, 580, 60),  # "WHERE AEROSPACE PLACES ITS TRUST"
    },
    'footer': {
        'doc_title':  fitz.Rect(54, 752, 300, 772),
        'page_num':   fitz.Rect(540, 752, 580, 772),
    },
    'hero': {
        'image_band': fitz.Rect(0, 70, PAGE_W, 380),
        'title':      fitz.Rect(54, 400, 558, 460),
        'intro':      fitz.Rect(54, 470, 558, 510),
        'subintro':   fitz.Rect(54, 512, 558, 530),
        'body':       fitz.Rect(54, 555, 558, 650),
        'callout':    fitz.Rect(54, 660, 558, 740),
    },
    'content': {
        'eyebrow': fitz.Rect(54, 100, 558, 120),
        'title':   fitz.Rect(54, 122, 558, 200),
        'lead':    fitz.Rect(54, 210, 558, 260),
        'body':    fitz.Rect(54, 265, 558, 740),
    },
    'content_side_callout': {
        'title':       fitz.Rect(54, 100, 558, 180),
        'body':        fitz.Rect(54, 195, 558, 740),
        'callout_col': fitz.Rect(54, 400, 200, 740),
    },
    'content_image': {
        'eyebrow': fitz.Rect(54, 100, 558, 120),
        'title':   fitz.Rect(54, 122, 558, 200),
        'image':   fitz.Rect(330, 215, 558, 430),
        'lead':    fitz.Rect(54, 210, 320, 260),
        'body':    fitz.Rect(54, 265, 558, 740),
    },
}

FONT_ALIAS = 'opensans'


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _register_font(page):
    """Try to register Open Sans on a page. Returns the font alias or None
    on failure (caller should fall back to 'helv')."""
    if not FONT_FILE.exists():
        return None
    try:
        page.insert_font(fontname=FONT_ALIAS, fontfile=str(FONT_FILE))
        return FONT_ALIAS
    except Exception:
        return None


def _fontname(page):
    return _register_font(page) or 'helv'


def _redact(page, rect, fill=WHITE):
    """White-box a region so we can overlay new content cleanly."""
    page.add_redact_annot(rect, fill=fill)
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,
                          graphics=fitz.PDF_REDACT_LINE_ART_NONE)


def _draw_text(page, rect, text, *, size, color, bold=False, align=0):
    """Insert text inside a rect using HTML so we can flow long content."""
    if not text:
        return
    weight = 700 if bold else 400
    font_family = 'Open Sans' if FONT_FILE.exists() else 'Helvetica'
    css = (f"font-family: '{font_family}'; font-size: {size}pt; "
           f"font-weight: {weight}; color: rgb({int(color[0]*255)},"
           f"{int(color[1]*255)},{int(color[2]*255)}); "
           f"line-height: 1.4;")
    html = f'<div style="{css}">{text}</div>'
    try:
        page.insert_htmlbox(rect, html)
    except Exception:
        # Fallback: plain insert_textbox without HTML
        page.insert_textbox(rect, text, fontsize=size, color=color,
                            fontname=_fontname(page), align=align)


def _draw_html(page, rect, html):
    try:
        page.insert_htmlbox(rect, html)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Layout renderers
# ---------------------------------------------------------------------------

def render_cover(page, cover):
    r = REGIONS['cover']
    for region in r.values():
        _redact(page, region, fill=NAVY)

    _draw_text(page, r['eyebrow'], cover.get('eyebrow', ''),
               size=14, color=CYAN, bold=True)
    _draw_text(page, r['title'], cover.get('title', ''),
               size=44, color=WHITE)
    _draw_text(page, r['overview'], cover.get('overview', ''),
               size=12, color=NAVY, bold=True)
    _draw_text(page, r['date'], cover.get('date', ''),
               size=10, color=NAVY, bold=True)


def render_toc(page, entries):
    r = REGIONS['toc']
    _redact(page, r['entries'], fill=WHITE)

    rows_html = []
    for entry in entries:
        rows_html.append(
            f'<div style="display:flex; padding:14px 0; border-bottom:1px solid #DDE4F1;">'
            f'<span style="font-size:24pt; color:#16C2EE; width:60px; '
            f'font-weight:300;">{entry["page"]}</span>'
            f'<span style="font-size:12pt; color:#242D41; padding-top:8px;">'
            f'{entry["title"]}</span>'
            f'</div>'
        )
    family = 'Open Sans' if FONT_FILE.exists() else 'Helvetica'
    _draw_html(page, r['entries'],
               f'<div style="font-family:\'{family}\';">{"".join(rows_html)}</div>')


def render_hero(page, spec):
    r = REGIONS['hero']
    for region in (r['title'], r['intro'], r['subintro'], r['body'], r['callout']):
        _redact(page, region, fill=NAVY if region is r['title'] else WHITE)

    if img := spec.get('hero_image'):
        if Path(img).expanduser().exists():
            page.insert_image(r['image_band'], filename=str(Path(img).expanduser()),
                              keep_proportion=True)

    _draw_text(page, r['title'], spec.get('title', ''),
               size=32, color=WHITE)
    _draw_text(page, r['intro'], spec.get('intro', ''),
               size=10, color=WHITE, bold=True)
    _draw_text(page, r['subintro'], spec.get('subintro', ''),
               size=10, color=WHITE)
    _draw_text(page, r['body'], _join_body(spec.get('body', [])),
               size=10, color=INK)

    if callout := spec.get('callout'):
        page.draw_rect(r['callout'], color=None, fill=CALLOUT_BG)
        family = 'Open Sans' if FONT_FILE.exists() else 'Helvetica'
        html = (f'<div style="font-family:\'{family}\'; padding:14px;">'
                f'<div style="font-size:14pt; color:#16C2EE; font-weight:600; '
                f'margin-bottom:6px;">{callout["title"]}</div>'
                f'<div style="font-size:10pt; color:#FFFFFF;">{callout["body"]}</div>'
                f'</div>')
        _draw_html(page, r['callout'], html)


def render_content(page, spec):
    r = REGIONS['content']
    for region in r.values():
        _redact(page, region, fill=WHITE)

    if eyebrow := spec.get('eyebrow'):
        _draw_text(page, r['eyebrow'], eyebrow, size=11, color=NAVY, bold=True)
    _draw_text(page, r['title'], spec.get('title', ''),
               size=32, color=NAVY)
    if lead := spec.get('lead'):
        _draw_text(page, r['lead'], lead, size=10, color=INK, bold=True)
    _draw_text(page, r['body'],
               _render_body_html(spec.get('body', []), spec.get('subsections', [])),
               size=10, color=INK)


def render_content_side_callout(page, spec):
    r = REGIONS['content_side_callout']
    _redact(page, r['title'], fill=WHITE)
    _redact(page, r['body'], fill=WHITE)

    _draw_text(page, r['title'], spec.get('title', ''),
               size=32, color=NAVY)

    subs = spec.get('subsections', [])
    callout_sub = next((s for s in subs if s.get('layout') == 'two_column'), None)
    if callout_sub:
        page.draw_rect(r['callout_col'], color=None, fill=SIDE_CALLOUT_BG)
        cols = callout_sub.get('columns', [{}, {}])
        family = 'Open Sans' if FONT_FILE.exists() else 'Helvetica'
        left_html = (f'<div style="font-family:\'{family}\'; padding:14px; '
                     f'color:#1E5BB5; font-size:14pt; font-weight:600;">'
                     f'{cols[0].get("lead", "")}</div>')
        _draw_html(page, r['callout_col'], left_html)

    _draw_text(page, r['body'],
               _render_body_html(spec.get('body', []), subs),
               size=10, color=INK)


def render_content_image(page, spec):
    r = REGIONS['content_image']
    for key, region in r.items():
        if key != 'image':
            _redact(page, region, fill=WHITE)

    if eyebrow := spec.get('eyebrow'):
        _draw_text(page, r['eyebrow'], eyebrow, size=11, color=NAVY, bold=True)
    _draw_text(page, r['title'], spec.get('title', ''),
               size=32, color=NAVY)

    if img := spec.get('image'):
        if Path(img).expanduser().exists():
            page.insert_image(r['image'], filename=str(Path(img).expanduser()),
                              keep_proportion=True)

    if lead := spec.get('lead'):
        _draw_text(page, r['lead'], lead, size=10, color=INK, bold=True)
    _draw_text(page, r['body'],
               _render_body_html(spec.get('body', []), spec.get('subsections', [])),
               size=10, color=INK)


# ---------------------------------------------------------------------------
# Body HTML rendering
# ---------------------------------------------------------------------------

def _join_body(paragraphs):
    return '<br/><br/>'.join(paragraphs or [])


def _render_body_html(body, subsections):
    family = 'Open Sans' if FONT_FILE.exists() else 'Helvetica'
    parts = [f'<div style="font-family:\'{family}\'; font-size:10pt; color:#242D41;">']
    for p in body or []:
        parts.append(f'<p style="margin:0 0 10px 0;">{p}</p>')
    for sub in subsections or []:
        if sub.get('layout') == 'two_column':
            parts.append(_render_two_column_html(sub))
            continue
        if h := sub.get('heading'):
            parts.append(f'<div style="font-size:14pt; color:#1E5BB5; '
                         f'font-weight:600; margin:14px 0 8px 0;">{h}</div>')
        if lead := sub.get('lead'):
            parts.append(f'<p style="font-weight:700; margin:0 0 8px 0;">{lead}</p>')
        if intro := sub.get('intro'):
            parts.append(f'<p style="margin:0 0 8px 0;">{intro}</p>')
        for p in sub.get('body', []):
            parts.append(f'<p style="margin:0 0 8px 0;">{p}</p>')
        if bullets := sub.get('bullets'):
            parts.append('<ul style="margin:4px 0 8px 16px; padding:0;">')
            for b in bullets:
                parts.append(f'<li style="margin:0 0 4px 0;">{b}</li>')
            parts.append('</ul>')
    parts.append('</div>')
    return ''.join(parts)


def _render_two_column_html(sub):
    cols = sub.get('columns', [{}, {}])
    family = 'Open Sans' if FONT_FILE.exists() else 'Helvetica'
    html = (f'<table style="width:100%; font-family:\'{family}\'; '
            f'font-size:10pt; color:#242D41; margin-top:10px;">'
            f'<tr style="vertical-align:top;">')
    for i, col in enumerate(cols):
        html += '<td style="width:50%; padding:0 8px;">'
        if lead := col.get('lead'):
            html += f'<p style="font-weight:700; margin:0 0 8px 0;">{lead}</p>'
        for p in col.get('body', []):
            html += f'<p style="margin:0 0 8px 0;">{p}</p>'
        for b in col.get('bullets', []):
            html += f'<p style="margin:0 0 4px 16px;">{b}</p>'
        html += '</td>'
    html += '</tr></table>'
    return html


# ---------------------------------------------------------------------------
# Footer (doc title + page number) — applied to every body page
# ---------------------------------------------------------------------------

def write_footer(page, doc_title, page_num):
    r = REGIONS['footer']
    _redact(page, r['doc_title'], fill=NAVY if page_num == 'cover' else WHITE)
    _redact(page, r['page_num'], fill=WHITE)
    if doc_title:
        _draw_text(page, r['doc_title'], doc_title,
                   size=9, color=FOOTER_GREY)
    if isinstance(page_num, int):
        _draw_text(page, r['page_num'], str(page_num),
                   size=9, color=FOOTER_GREY, align=2)


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

LAYOUTS = {
    'hero': render_hero,
    'content': render_content,
    'content_side_callout': render_content_side_callout,
    'content_image': render_content_image,
}


def _copy_layout(out_pdf, src_pdf, layout_key):
    src_idx = LAYOUT_PAGE[layout_key]
    out_pdf.insert_pdf(src_pdf, from_page=src_idx, to_page=src_idx)
    return out_pdf[-1]


def build(data):
    if not TEMPLATE.exists():
        raise FileNotFoundError(f'Bundled template not found: {TEMPLATE}')
    if not FONT_FILE.exists():
        print(f'WARNING: Open Sans not found at {FONT_FILE}. '
              f'Falling back to Helvetica.', file=sys.stderr)

    src = fitz.open(str(TEMPLATE))
    out = fitz.open()

    doc_title = data.get('doc_title', '')

    # Cover
    cover_page = _copy_layout(out, src, 'cover')
    render_cover(cover_page, data.get('cover', {}))

    # TOC
    page_counter = 2
    if entries := data.get('toc'):
        toc_page = _copy_layout(out, src, 'toc')
        render_toc(toc_page, entries)
        write_footer(toc_page, doc_title, page_counter)
        page_counter += 1

    # Body pages
    for spec in data.get('pages', []):
        layout = spec.get('layout')
        if layout not in LAYOUTS:
            raise ValueError(f"Unknown layout: {layout!r}. "
                             f"Use one of: {sorted(LAYOUTS)}")
        body_page = _copy_layout(out, src, layout)
        LAYOUTS[layout](body_page, spec)
        write_footer(body_page, doc_title, page_counter)
        page_counter += 1

    # Static back cover — appended verbatim
    _copy_layout(out, src, 'back_cover')

    output_path = data['output_path']
    out.save(output_path, garbage=4, deflate=True)
    out.close()
    src.close()
    print(f'Saved: {output_path}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 whitepaper_builder.py <data.json>')
        sys.exit(1)
    with open(sys.argv[1]) as f:
        build(json.load(f))
