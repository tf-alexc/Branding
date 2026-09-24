#!/usr/bin/env python3
"""
Fill a Kenyon certificate template with recipient details.

Usage (command line, from any working directory):
    python3 "<skill_dir>/fill_certificate.py" --type training --name "John Smith" \
        --date "12th June 2026" --course "Emergency Planning"

    python3 "<skill_dir>/fill_certificate.py" --word-template

Usage (import):
    from fill_certificate import fill_certificate
    pdf = fill_certificate("training", "John Smith", "12th June 2026", "Emergency Planning")

Outputs never go into the user's own folders. Everything is written to a
delivery folder (claude.ai's outputs folder, or a temporary folder elsewhere)
so it can be shared into the chat, where the user downloads it themselves.

Every path is resolved from this file's own location, so the skill runs the
same on any machine or sandbox it is installed in.

Field positions are read from the template at runtime, so swapping in a new
version of "Certificate - Kenyon - Template.pdf" needs no code changes, as long
as the fill-in placeholders stay set in Titillium Web Regular.
"""

import argparse
import os
import re
import shutil
import sys
import tempfile

try:
    import fitz
except ImportError:
    sys.exit("PyMuPDF is not installed. Run: pip install pymupdf "
             "(add --break-system-packages if pip refuses), then rerun.")

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE   = os.path.join(SKILL_DIR, "Certificate - Kenyon - Template.pdf")
WORD_TEMPLATE = os.path.join(SKILL_DIR, "Certificate - Kenyon - Membership - Word Template.docx")
# Titillium Web Regular, bundled with this skill: the certificate artwork sets its
# fill-in fields in it, so filled text matches the template exactly. This overrides
# the house Open Sans rule for this template only, same as the ASIP webinar skill.
FONT_FILE  = os.path.join(SKILL_DIR, "TitilliumWeb-Regular.ttf")

# claude.ai surfaces files saved here to the user in the chat.
CHAT_OUTPUT_DIR = "/mnt/user-data/outputs"
# Everywhere else: a temporary folder, never the user's Desktop or documents.
TEMP_OUTPUT_DIR = os.path.join(tempfile.gettempdir(), "kenyon-certificates")

PREVIEW_DPI = 150

SAPPHIRE = (0 / 255, 92 / 255, 167 / 255)  # #005CA7
# Redactions remove the placeholder text only. No fill: a white box would paint
# over the underline rules and line patterns that sit behind the fields.
NO_FILL  = False

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


def normalise_type(cert_type):
    """'Academy_Training', 'academy-training' and 'academy training' all match."""
    return re.sub(r"[\s_-]+", " ", str(cert_type)).strip().lower()


def delivery_dir():
    """
    The only place outputs are written. claude.ai's outputs folder when it
    exists, since files there reach the user in the chat. Otherwise a temporary
    folder, which is where the chat's file-sharing tool picks them up from.
    """
    folder = CHAT_OUTPUT_DIR if os.path.isdir(CHAT_OUTPUT_DIR) else TEMP_OUTPUT_DIR
    os.makedirs(folder, exist_ok=True)
    return folder


def preview_path(pdf_path):
    """PNG preview saved next to the PDF, for chats that cannot preview PDFs."""
    return os.path.splitext(pdf_path)[0] + " - preview.png"


def _unique(path):
    """Never overwrite an earlier certificate the user may not have downloaded yet."""
    if not os.path.exists(path):
        return path
    stem, ext = os.path.splitext(path)
    n = 2
    while os.path.exists(f"{stem} ({n}){ext}"):
        n += 1
    return f"{stem} ({n}){ext}"


def _check_glyphs(font, text, field):
    """
    Refuse text the brand font cannot draw. Titillium Web covers Latin scripts
    only, so Greek, Cyrillic, Arabic or CJK letters would print as blanks.
    """
    missing = sorted({c for c in text if not c.isspace() and not font.has_glyph(ord(c))})
    if missing:
        raise ValueError(
            f"The {field} contains characters the certificate font (Titillium Web) cannot "
            f"print: {' '.join(missing)}. Ask the user for a Latin-alphabet spelling."
        )


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
    apart, and redaction deletes any text the rect intersects.
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

    m = re.search(r'(\d+)(st|nd|rd|th)\b', date_str, re.IGNORECASE)
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


def fill_certificate(cert_type, name, date, course_or_incident=None, preview=True):
    """
    Generate a filled Kenyon certificate PDF in the delivery folder and return its path.

    cert_type:            "training" | "academy training" | "acceptance"
                          | "achievement" | "membership"
    name:                 Recipient full name.
    date:                 Date string, e.g. "12th June 2026". Ordinal rendered as superscript.
                          On Membership this is the "valuable member since" date.
    course_or_incident:   Course title (training/academy training), incident name (achievement),
                          or None (acceptance/membership).
    preview:              Also save a PNG of the page next to the PDF (see preview_path()).
    """
    key = normalise_type(cert_type)
    if key not in PAGE_INDEX:
        raise ValueError(f"Unknown cert type {cert_type!r}. Must be one of: {list(PAGE_INDEX)}")

    name = (name or "").strip()
    date = (date or "").strip()
    course_or_incident = (course_or_incident or "").strip() or None
    if not name:
        raise ValueError("The name is empty.")
    if not date:
        raise ValueError("The date is empty.")

    middle_field = MIDDLE_FIELD[key]
    if middle_field and not course_or_incident:
        raise ValueError(f"{key.title()} certificates need the {middle_field} field.")

    font = fitz.Font(fontfile=FONT_FILE)
    _check_glyphs(font, name, "name")
    _check_glyphs(font, date, "date")
    if middle_field:
        _check_glyphs(font, course_or_incident, middle_field)

    page_idx = PAGE_INDEX[key]
    layout   = _read_layout(page_idx)

    doc  = fitz.open(TEMPLATE)
    page = doc[page_idx]

    # Clear the template placeholders
    page.add_redact_annot(layout["name"]["rect"], fill=NO_FILL)
    page.add_redact_annot(layout["date"]["rect"], fill=NO_FILL)
    if "middle" in layout:
        page.add_redact_annot(layout["middle"]["rect"], fill=NO_FILL)

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

    safe_name = re.sub(r'[/\\:*?"<>|\x00-\x1f]', "-", name)
    safe_type = key.replace(" ", "_")
    filename  = f"Certificate - Kenyon - {safe_type} - {safe_name}.pdf"
    output_path = _unique(os.path.join(delivery_dir(), filename))

    out = fitz.open()
    out.insert_pdf(doc, from_page=page_idx, to_page=page_idx)
    out.save(output_path, garbage=3, deflate=True)
    if preview:
        out[0].get_pixmap(dpi=PREVIEW_DPI).save(preview_path(output_path))
    out.close()
    doc.close()

    return output_path


def word_template():
    """Copy the embedded Word Membership template into the delivery folder for sharing."""
    dest = _unique(os.path.join(delivery_dir(), os.path.basename(WORD_TEMPLATE)))
    shutil.copyfile(WORD_TEMPLATE, dest)
    return dest


def main():
    parser = argparse.ArgumentParser(
        description="Fill a Kenyon certificate. Output goes to the delivery folder only.")
    parser.add_argument("--type", type=normalise_type, choices=list(PAGE_INDEX),
                        help="Certificate type.")
    parser.add_argument("--name", help="Recipient full name.")
    parser.add_argument("--date", help='e.g. "12th June 2026". On Membership, the member-since date.')
    parser.add_argument("--course", help="Course title (Training, Academy Training).")
    parser.add_argument("--incident", help="Incident name (Achievement).")
    parser.add_argument("--word-template", action="store_true",
                        help="Copy the editable Word Membership template for sharing, then exit.")
    args = parser.parse_args()

    if args.word_template:
        print(f"DOCX: {word_template()}")
        return

    if not (args.type and args.name and args.date):
        parser.error("--type, --name and --date are required.")

    try:
        pdf = fill_certificate(args.type, args.name, args.date, args.course or args.incident)
    except ValueError as err:
        sys.exit(f"ERROR: {err}")
    print(f"PDF: {pdf}")
    print(f"PREVIEW: {preview_path(pdf)}")


if __name__ == "__main__":
    main()
