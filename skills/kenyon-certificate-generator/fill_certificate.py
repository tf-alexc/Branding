#!/usr/bin/env python3
"""
Fill a Kenyon certificate template with recipient details.

Usage (import):
    from fill_certificate import fill_certificate
    output = fill_certificate("training", "John Smith", "12th June 2026", "Emergency Planning")
    print(output)  # path to saved PDF

Field positions are read from the template at runtime, so swapping in a new
version of "Certificate - Kenyon - Template.pdf" needs no code changes, as long
as the fill-in placeholders stay set in Titillium Web Regular.
"""

import fitz
import os
import re

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE   = os.path.join(SKILL_DIR, "Certificate - Kenyon - Template.pdf")
# Titillium Web Regular, bundled with this skill: the certificate artwork sets its
# fill-in fields in it, so filled text matches the template exactly. This overrides
# the house Open Sans rule for this template only, same as the ASIP webinar skill.
FONT_FILE  = os.path.join(SKILL_DIR, "TitilliumWeb-Regular.ttf")
OUTPUT_DIR = os.path.expanduser("~/Desktop")

SAPPHIRE = (0 / 255, 92 / 255, 167 / 255)  # #005CA7
WHITE    = (1.0, 1.0, 1.0)

PAGE_INDEX = {
    "training":         0,
    "academy training": 1,
    "acceptance":       2,
    "achievement":      3,
    "membership":       4,
}

# Types that carry a middle field, and what that field is called.
MIDDLE_FIELD = {
    "training":         "course",
    "academy training": "course",
    "achievement":      "incident",
    "acceptance":       None,
    "membership":       None,
}

# The template's placeholders are the only Titillium Web Regular text on a page.
PLACEHOLDER_FONT = "TitilliumWeb-Regular"

RIGHT_BOUND         = 810.0  # right edge available to inserted text
DEFAULT_ORDINAL_RISE = 8.0   # pt above the main baseline
DEFAULT_ORDINAL_RATIO = 14.0 / 24.0

_layout_cache = {}


def _placeholder_rows(page):
    """Group the page's placeholder spans into rows, top to bottom."""
    spans = []
    for block in page.get_text("dict")["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                if not span["text"].strip():
                    continue
                if not span["font"].startswith(PLACEHOLDER_FONT):
                    continue
                spans.append(span)

    rows = []
    for span in sorted(spans, key=lambda s: (s["origin"][1], s["origin"][0])):
        for row in rows:
            # Same row if the baselines sit within one line of each other.
            if abs(span["origin"][1] - row[0]["origin"][1]) < span["size"]:
                row.append(span)
                break
        else:
            rows.append([span])

    for row in rows:
        row.sort(key=lambda s: s["origin"][0])
    rows.sort(key=lambda r: min(s["origin"][1] for s in r))
    return rows


def _row_rect(page, row):
    """
    Redaction rect for a placeholder row: the row's own bounds, pulled in so it
    never touches neighbouring artwork. Template lines sit as little as 0.8pt
    apart, and redaction deletes anything the rect intersects.
    """
    x0 = min(s["bbox"][0] for s in row) - 1
    x1 = max(s["bbox"][2] for s in row) + 1
    y0 = min(s["bbox"][1] for s in row) - 1
    y1 = max(s["bbox"][3] for s in row) + 1

    for block in page.get_text("dict")["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                if span["font"].startswith(PLACEHOLDER_FONT) or not span["text"].strip():
                    continue
                bx0, by0, bx1, by1 = span["bbox"]
                if bx1 <= x0 or bx0 >= x1:      # no horizontal overlap, ignore
                    continue
                if by1 > y0 and by1 < y1:       # neighbour above, clip top
                    y0 = by1 + 0.1
                if by0 < y1 and by0 > y0:       # neighbour below, clip bottom
                    y1 = by0 - 0.1
    return fitz.Rect(x0, y0, x1, y1)


def _read_layout(page_idx):
    """
    Derive { field: {rect, x, baseline, size, ...} } for a template page.

    Rows run top to bottom: name first, date last, and the middle row (when the
    type has one) is the course or incident.
    """
    if page_idx in _layout_cache:
        return _layout_cache[page_idx]

    doc  = fitz.open(TEMPLATE)
    page = doc[page_idx]
    rows = _placeholder_rows(page)

    if len(rows) not in (2, 3):
        doc.close()
        raise RuntimeError(
            f"Template page {page_idx + 1} has {len(rows)} placeholder rows, expected 2 or 3. "
            "Check that the fill-in fields are still set in Titillium Web Regular."
        )

    def field(row):
        main = max(row, key=lambda s: s["size"])
        return {
            "rect":     _row_rect(page, row),
            "x":        row[0]["origin"][0],
            "baseline": main["origin"][1],
            "size":     main["size"],
        }

    layout = {"name": field(rows[0]), "date": field(rows[-1])}
    if len(rows) == 3:
        layout["middle"] = field(rows[1])

    # Superscript metrics, taken from the template's own ordinal where present.
    date_row = rows[-1]
    main = max(date_row, key=lambda s: s["size"])
    small = [s for s in date_row if s["size"] < main["size"]]
    if small:
        layout["date"]["ordinal_size"] = small[0]["size"]
        layout["date"]["ordinal_rise"] = main["origin"][1] - small[0]["origin"][1]
    else:
        layout["date"]["ordinal_size"] = main["size"] * DEFAULT_ORDINAL_RATIO
        layout["date"]["ordinal_rise"] = DEFAULT_ORDINAL_RISE

    doc.close()
    _layout_cache[page_idx] = layout
    return layout


def _auto_fontsize(font, text, max_size, max_width, min_size=10):
    size = max_size
    while size > min_size:
        if font.text_length(text, fontsize=size) <= max_width:
            return size
        size -= 1
    return min_size


def _insert_date(page, spec, date_str, font):
    """Render date string; raises ordinal suffix (st/nd/rd/th) as superscript."""
    x, baseline_y = spec["x"], spec["baseline"]
    size, sup_size, rise = spec["size"], spec["ordinal_size"], spec["ordinal_rise"]

    def draw(pos_x, pos_y, text, text_size):
        page.insert_text(fitz.Point(pos_x, pos_y), text,
                         fontsize=text_size, fontfile=FONT_FILE, fontname="ks_font",
                         color=SAPPHIRE)
        return font.text_length(text, fontsize=text_size)

    m = re.search(r'(\d+)(st|nd|rd|th)', date_str, re.IGNORECASE)
    if not m:
        draw(x, baseline_y, date_str, size)
        return

    before  = date_str[:m.start()] + m.group(1)  # e.g. "June 12"
    ordinal = m.group(2)                         # e.g. "th"
    after   = date_str[m.end():]                 # e.g. " 2026"

    x_cur = x
    if before:
        x_cur += draw(x_cur, baseline_y, before, size)
    x_cur += draw(x_cur, baseline_y - rise, ordinal, sup_size)
    if after:
        draw(x_cur, baseline_y, after, size)


def fill_certificate(cert_type, name, date, course_or_incident=None, output_path=None):
    """
    Generate a filled Kenyon certificate PDF.

    cert_type:            "training" | "academy training" | "acceptance"
                          | "achievement" | "membership"
    name:                 Recipient full name.
    date:                 Date string, e.g. "12th June 2026". Ordinal rendered as superscript.
                          On Membership this is the "valuable member since" date.
    course_or_incident:   Course title (training/academy training), incident name (achievement),
                          or None (acceptance/membership).
    output_path:          Full output path. Defaults to ~/Desktop/Certificate - Kenyon - ...pdf
    """
    key = cert_type.lower().strip()
    if key not in PAGE_INDEX:
        raise ValueError(f"Unknown cert type {cert_type!r}. Must be one of: {list(PAGE_INDEX)}")

    middle_field = MIDDLE_FIELD[key]
    if middle_field and not course_or_incident:
        raise ValueError(f"{key.title()} certificates need the {middle_field} field.")

    page_idx = PAGE_INDEX[key]
    layout   = _read_layout(page_idx)
    font     = fitz.Font(fontfile=FONT_FILE)

    doc  = fitz.open(TEMPLATE)
    page = doc[page_idx]

    # Clear the template placeholders
    page.add_redact_annot(layout["name"]["rect"], fill=WHITE)
    page.add_redact_annot(layout["date"]["rect"], fill=WHITE)
    if "middle" in layout:
        page.add_redact_annot(layout["middle"]["rect"], fill=WHITE)

    page.apply_redactions(
        images   = fitz.PDF_REDACT_IMAGE_NONE,
        graphics = fitz.PDF_REDACT_LINE_ART_NONE,
    )

    # Insert name
    nspec = layout["name"]
    page.insert_text(fitz.Point(nspec["x"], nspec["baseline"]), name,
                     fontsize=_auto_fontsize(font, name, nspec["size"], RIGHT_BOUND - nspec["x"]),
                     fontfile=FONT_FILE, fontname="ks_font",
                     color=SAPPHIRE)

    # Insert date
    _insert_date(page, layout["date"], date, font)

    # Insert course or incident
    if middle_field and "middle" in layout:
        mspec = layout["middle"]
        page.insert_text(fitz.Point(mspec["x"], mspec["baseline"]), course_or_incident,
                         fontsize=_auto_fontsize(font, course_or_incident, mspec["size"],
                                                 RIGHT_BOUND - mspec["x"]),
                         fontfile=FONT_FILE, fontname="ks_font",
                         color=SAPPHIRE)

    # Build output path
    if output_path is None:
        safe_name = re.sub(r'[/\\:*?"<>|]', "-", name)
        safe_type = key.replace(" ", "_")
        filename  = f"Certificate - Kenyon - {safe_type} - {safe_name}.pdf"
        output_path = os.path.join(OUTPUT_DIR, filename)

    out = fitz.open()
    out.insert_pdf(doc, from_page=page_idx, to_page=page_idx)
    out.save(output_path)
    out.close()
    doc.close()

    return output_path
