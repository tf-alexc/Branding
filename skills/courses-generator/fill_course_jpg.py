#!/usr/bin/env python3
"""
Generate a course JPG for LinkedIn from a sub-brand template using PyMuPDF.

Templates live in `Course PDFs/courses-generator/` and each has two pages:
  Page 0 — two-column layout  → used when column_type == "both"
  Page 1 — single-column layout → used for all other column types

The template includes a BOOK NOW button + website footer (visual only, not edited).
The script fills title + pill labels + dates over the template, then rasterises
the chosen page to a high-resolution JPG suitable for LinkedIn posting.
"""

import fitz, os, re

TEMPLATE_DIR = "/Users/alexcraiu/Desktop/Claude Playground/Course PDFs/courses-generator"
OUTPUT_BASE  = "/Users/alexcraiu/Desktop/Claude Playground/Course PDFs"
FONT_FILE    = "/Users/alexcraiu/Library/Fonts/OpenSans-VariableFont_wdth,wght.ttf"

RENDER_ZOOM = 2.0          # 1200x1400 template → 2400x2800 JPG
JPG_QUALITY = 92

NAVY        = (0.0, 0.07499809563159943, 0.2239871770143509)
WHITE       = (1.0, 1.0, 1.0)
TITLE_COLOR = (204/255, 213/255, 255/255)
ELECTRIC    = (3/255, 212/255, 255/255)

BRAND_TEMPLATES = {
    "Baines Simmons": "Courses - Baines Simmons - Template.pdf",
    "Redline":        "Courses - Redline - Template.pdf",
    "Kenyon":         "Courses - Kenyon - Template.pdf",
}

BRAND_FROM_DOMAIN = {
    "kenyoninternational.com":   "Kenyon",
    "trustredline.co.uk":        "Redline",
    "redlineassuredsecurity.com":"Redline",
    "bainessimmons.com":         "Baines Simmons",
}

# ── shared layout (matches v1 fill_course_pdf.py — upper region unchanged) ────

TITLE_RECT      = fitz.Rect(73, 193, 1135, 385)
PREFIX_FONTSIZE = 42
_TITLE_REDACT   = fitz.Rect(68, 188, 1140, 388)

SEP_COLOR = (0.0, 0.30, 0.54)

# ── page 0 layout (two-column, column_type == "both") ─────────────────────────

LEFT_PILL_X    = 164
RIGHT_PILL_X   = 700
PILL_Y         = 452
PILL_FONTSIZE  = 35

LEFT_DATE_X    = 168
RIGHT_DATE_X   = 693
DATES_Y_START  = 545
DATES_Y_STEP   = 80
DATES_FONTSIZE = 35

SEP_LEFT_X0,  SEP_LEFT_X1  = 157, 510
SEP_RIGHT_X0, SEP_RIGHT_X1 = 692, 1045
SEP_Y_OFFSET  = 27

_P0_L_PILL_REDACT  = fitz.Rect(160, 412,  545, 463)
_P0_L_DATES_REDACT = fitz.Rect(155, 495,  628, 735)
_P0_R_PILL_REDACT  = fitz.Rect(695, 412, 1135, 463)
_P0_R_DATES_REDACT = fitz.Rect(685, 495, 1140, 735)

# ── page 1 layout (single-column, all other column types) ─────────────────────

P1_PILL_X       = 203
P1_PILL_Y       = 478
P1_PILL_FONTSIZE = 50

P1_DATE_X        = 208
P1_DATES_Y_START = 614
P1_DATES_Y_STEP  = 116
P1_DATES_FONTSIZE = 50

P1_SEP_X0       = 200
P1_SEP_X1       = 638
P1_SEP_Y_OFFSET = 40

_P1_PILL_REDACT  = fitz.Rect(198, 418, 668, 496)
_P1_DATES_REDACT = fitz.Rect(200, 545, 640, 755)

# ── Form XObject stream patterns (page 0, applied BEFORE apply_redactions) ────

_SEP_XOBJS = re.compile(
    rb'q\n[^\n]*\n/GS\d+[^\n]*\n[^\n]*/Fm(?:7|8|9|10) Do\n[^\n]*\n'
)


# ── helpers ───────────────────────────────────────────────────────────────────

def _strip_year(s):
    return re.sub(r'\s*\b\d{4}\b\s*$', '', s.strip()).rstrip(' ,-')


def _safe_name(s):
    for ch in r'/\:*?"<>|':
        s = s.replace(ch, '-')
    return s


def _split_title(name):
    """Return (prefix, subtitle) if name contains ' - ', else (None, name)."""
    if ' - ' in name:
        prefix, subtitle = name.split(' - ', 1)
        return prefix, subtitle
    return None, name


def _strip_xobjs(doc, page, pattern):
    for xref in page.get_contents():
        raw      = doc.xref_stream(xref)
        modified = pattern.sub(b'', raw)
        if modified != raw:
            doc.update_stream(xref, modified)


def brand_from_url(url):
    """Match a course page URL to its sub-brand. Raises if no match."""
    u = url.lower()
    for domain, brand in BRAND_FROM_DOMAIN.items():
        if domain in u:
            return brand
    raise ValueError(
        f"Could not detect brand from URL: {url!r}. "
        f"Expected one of: {sorted(BRAND_FROM_DOMAIN)}"
    )


# ── main ──────────────────────────────────────────────────────────────────────

def fill_course(brand, course_name, left_label, left_dates,
                right_dates=None, column_type="generic"):
    """
    brand        : "Baines Simmons" | "Redline" | "Kenyon"
    course_name  : full course title string
    left_label   : pill label ("Upcoming Dates", "Initial Course Dates", etc.)
    left_dates   : list of date strings (years stripped automatically)
    right_dates  : list of date strings for right column (column_type="both" only)
    column_type  : "both" | "initial" | "recurrent" | "generic"

    Returns: output JPG path.
    """
    template_path = os.path.join(TEMPLATE_DIR, BRAND_TEMPLATES[brand])
    output_dir    = os.path.join(OUTPUT_BASE, f"Course JPGs - {brand}")
    os.makedirs(output_dir, exist_ok=True)
    output_path   = os.path.join(output_dir, f"Course - {brand} - {_safe_name(course_name)}.jpg")

    left_dates  = [_strip_year(d) for d in left_dates]
    right_dates = [_strip_year(d) for d in (right_dates or [])]

    doc      = fitz.open(template_path)
    page_idx = 0 if column_type == "both" else 1
    page     = doc[page_idx]

    if column_type == "both":
        # ── Page 0: two-column ────────────────────────────────────────────────
        _strip_xobjs(doc, page, _SEP_XOBJS)

        page.add_redact_annot(_TITLE_REDACT,       fill=())
        page.add_redact_annot(_P0_L_PILL_REDACT,   fill=())
        page.add_redact_annot(_P0_L_DATES_REDACT,  fill=())
        page.add_redact_annot(_P0_R_PILL_REDACT,   fill=())
        page.add_redact_annot(_P0_R_DATES_REDACT,  fill=())
        page.apply_redactions(
            images=fitz.PDF_REDACT_IMAGE_NONE,
            graphics=fitz.PDF_REDACT_LINE_ART_NONE,
            text=fitz.PDF_REDACT_TEXT_REMOVE,
        )

        _insert_title(page, course_name)

        page.insert_text(
            (LEFT_PILL_X, PILL_Y), left_label,
            fontname="opensans", fontfile=FONT_FILE,
            fontsize=PILL_FONTSIZE, color=WHITE,
        )
        _insert_dates(page, LEFT_DATE_X, DATES_Y_START, DATES_Y_STEP,
                      DATES_FONTSIZE, SEP_LEFT_X0, SEP_LEFT_X1, SEP_Y_OFFSET,
                      left_dates)

        page.insert_text(
            (RIGHT_PILL_X, PILL_Y), "Recurrent Course Dates",
            fontname="opensans", fontfile=FONT_FILE,
            fontsize=PILL_FONTSIZE, color=WHITE,
        )
        _insert_dates(page, RIGHT_DATE_X, DATES_Y_START, DATES_Y_STEP,
                      DATES_FONTSIZE, SEP_RIGHT_X0, SEP_RIGHT_X1, SEP_Y_OFFSET,
                      right_dates)

    else:
        # ── Page 1: single-column ─────────────────────────────────────────────
        page.add_redact_annot(_TITLE_REDACT,      fill=())
        page.add_redact_annot(_P1_PILL_REDACT,    fill=())
        page.add_redact_annot(_P1_DATES_REDACT,   fill=())
        page.apply_redactions(
            images=fitz.PDF_REDACT_IMAGE_NONE,
            graphics=fitz.PDF_REDACT_LINE_ART_NONE,
            text=fitz.PDF_REDACT_TEXT_REMOVE,
        )

        _insert_title(page, course_name)

        page.insert_text(
            (P1_PILL_X, P1_PILL_Y), left_label,
            fontname="opensans", fontfile=FONT_FILE,
            fontsize=P1_PILL_FONTSIZE, color=WHITE,
        )
        _insert_dates(page, P1_DATE_X, P1_DATES_Y_START, P1_DATES_Y_STEP,
                      P1_DATES_FONTSIZE, P1_SEP_X0, P1_SEP_X1, P1_SEP_Y_OFFSET,
                      left_dates)

    # Rasterise the filled page to JPG (native PyMuPDF JPEG encoder, no Pillow needed)
    pix = page.get_pixmap(matrix=fitz.Matrix(RENDER_ZOOM, RENDER_ZOOM), alpha=False)
    with open(output_path, "wb") as f:
        f.write(pix.tobytes("jpg", jpg_quality=JPG_QUALITY))
    doc.close()
    print(f"Saved: {output_path}")
    return output_path


def fill_course_from_url(url, course_name, left_label, left_dates,
                         right_dates=None, column_type="generic"):
    """Convenience wrapper — detects brand from a course page URL."""
    brand = brand_from_url(url)
    return fill_course(brand, course_name, left_label, left_dates,
                       right_dates=right_dates, column_type=column_type)


def _insert_title(page, course_name):
    prefix, subtitle = _split_title(course_name)
    if prefix is not None:
        prefix_baseline = 193 + PREFIX_FONTSIZE
        page.insert_text(
            (73, prefix_baseline), prefix,
            fontname="opensans", fontfile=FONT_FILE,
            fontsize=PREFIX_FONTSIZE, color=ELECTRIC,
        )
        subtitle_top  = prefix_baseline + 15
        subtitle_rect = fitz.Rect(73, subtitle_top, 1135, 385)
        fontsize = 65
        while fontsize >= 35:
            rc = page.insert_textbox(
                subtitle_rect, subtitle,
                fontname="opensans", fontfile=FONT_FILE,
                fontsize=fontsize, color=TITLE_COLOR, align=0,
            )
            if rc >= 0:
                break
            fontsize -= 5
    else:
        fontsize = 70
        while fontsize >= 35:
            rc = page.insert_textbox(
                TITLE_RECT, subtitle,
                fontname="opensans", fontfile=FONT_FILE,
                fontsize=fontsize, color=TITLE_COLOR, align=0,
            )
            if rc >= 0:
                break
            fontsize -= 5


def _insert_dates(page, date_x, y_start, y_step, fontsize,
                  sep_x0, sep_x1, sep_y_offset, dates):
    y = y_start
    for i, d in enumerate(dates):
        page.insert_text(
            (date_x, y), d,
            fontname="opensans", fontfile=FONT_FILE,
            fontsize=fontsize, color=WHITE,
        )
        if i < len(dates) - 1:
            page.draw_line(
                fitz.Point(sep_x0, y + sep_y_offset),
                fitz.Point(sep_x1, y + sep_y_offset),
                color=SEP_COLOR, width=1,
            )
        y += y_step


if __name__ == "__main__":
    fill_course_from_url(
        url="https://www.bainessimmons.com/training-courses/risk-management-workshop",
        course_name="Risk Management Workshop (RMW)",
        left_label="Upcoming Dates",
        left_dates=["13 - 17 April", "07 - 11 September"],
        column_type="generic",
    )
