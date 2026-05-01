"""Fill a course dates PDF template using content-stream blanking + full-font text insertion."""
import fitz
import re
import os

FONT   = "/Users/alexcraiu/Library/Fonts/OpenSans-VariableFont_wdth,wght.ttf"
OUTPUT = "/Users/alexcraiu/Desktop/Claude Playground/Course PDFs"

TEMPLATES = {
    "Redline":        f"{OUTPUT}/Courses - Redline - Template.pdf",
    "Baines Simmons": f"{OUTPUT}/Courses - Baines Simmons - Template.pdf",
    "Kenyon":         f"{OUTPUT}/Courses - Kenyon - Template.pdf",
}

# Xrefs discovered by scanning each template. Positions are PDF-native Y-up coords.
# PyMuPDF baseline Y = page_height - native_Y  (page_height = 1400 for all three)
XREF_MAP = {
    "Redline": {
        "title_xref":     15,   # ([Course Title])Tj
        "left_pill_xref": 13,   # [(Initial Course)0.5 ( Dates)]TJ
        "right_pill_xref":10,   # [(Re)0.5 (curre)...s]TJ  (also contains left pill bg path)
        "dates_xref":      9,   # all date BT block
        # XObjects to clear for single-column
        "right_pill_bg":  346,  # right pill rounded-rect
        "right_cal_icon": 348,  # right calendar icon
        "right_sep1":     389,  # right separator after row 1
        "right_sep2":     329,  # right separator after row 2
        # Left separator after row 2 (hide when only one date)
        "left_sep2":      382,
    },
}

# Text insertion positions (PyMuPDF coords: Y-down from top, baseline)
# Derived from Tm commands: PyMuPDF_y = 1400 - native_y
POS = {
    "title":        (73.0,       272.2),   # 75.5231 0 0 75.5231 73 1127.791 Tm
    "left_pill":    (164.35,     451.31),  # 35 0 0 35 164.3545 948.6865 Tm
    "right_pill":   (699.90,     451.31),  # 35 0 0 35 699.8984 948.6865 Tm
    "date_left_1":  (167.78,     545.59),  # 35 0 0 35 167.7778 854.4131 Tm
    "date_left_2":  (167.78,     625.59),  # 35 0 0 35 167.7778 774.4131 Tm
    "date_right_1": (692.78,     545.59),
    "date_right_2": (692.78,     625.59),
}


def _blank_bt(stream_bytes, count=1):
    """Replace the first `count` BT...ET blocks with empty BT ET."""
    s = stream_bytes.decode("latin-1")
    s = re.sub(r'BT\b.*?\bET\b', "BT\nET", s, count=count, flags=re.DOTALL)
    return s.encode("latin-1")


def fill_course(brand, course_name, left_dates, col_type="generic",
                left_label="Upcoming Dates", right_label="Recurrent Course Dates",
                right_dates=None):
    xrefs  = XREF_MAP[brand]
    dates_l = left_dates if isinstance(left_dates, list) else [left_dates]
    dates_r = (right_dates or []) if col_type == "both" else []

    doc  = fitz.open(TEMPLATES[brand])
    page = doc[0]

    # ── Phase 1: blank original text in content streams ───────────────────────

    # Course title — target only the [Course Title] Tj, leave BOOK NOW intact
    s = doc.xref_stream(xrefs["title_xref"]).decode("latin-1")
    s = re.sub(r'\(\[Course Title\]\)Tj', "( )Tj", s)
    doc.update_stream(xrefs["title_xref"], s.encode("latin-1"))

    # Left pill label
    s = doc.xref_stream(xrefs["left_pill_xref"]).decode("latin-1")
    s = re.sub(r'\[.*?Initial Course.*?\]TJ', "( )Tj", s, flags=re.DOTALL)
    doc.update_stream(xrefs["left_pill_xref"], s.encode("latin-1"))

    # All date rows
    doc.update_stream(xrefs["dates_xref"],
                      _blank_bt(doc.xref_stream(xrefs["dates_xref"])))

    # Right column
    if col_type != "both":
        # Blank right pill text (preserve rest of stream — it also holds left pill bg path)
        s = doc.xref_stream(xrefs["right_pill_xref"]).decode("latin-1")
        s = re.sub(r'BT\b.*?\bET\b', "BT\nET", s, count=1, flags=re.DOTALL)
        doc.update_stream(xrefs["right_pill_xref"], s.encode("latin-1"))

        # Clear right pill shape, calendar icon, separator lines
        for key in ("right_pill_bg", "right_cal_icon", "right_sep1", "right_sep2"):
            doc.update_stream(xrefs[key], b"")

    # Hide left separator after row 2 when only one date
    if len(dates_l) < 2:
        doc.update_stream(xrefs["left_sep2"], b"")

    # ── Phase 2: insert new text using full Open Sans ─────────────────────────

    def txt(pos_key, text, size, color):
        page.insert_text(fitz.Point(*POS[pos_key]), text,
                         fontfile=FONT, fontsize=size, color=color)

    # Title: auto-size down from 75.5pt until it fits within the text area
    title_rect  = fitz.Rect(73, 190, 1150, 340)
    title_size  = 75.5
    title_color = (0.800, 0.835, 1.0)
    while title_size >= 30:
        rc = page.insert_textbox(title_rect, course_name,
                                 fontfile=FONT, fontsize=title_size,
                                 color=title_color, align=0)
        if rc >= 0:
            break
        title_size -= 2
    txt("left_pill", left_label,   35.0, (1.0, 1.0, 1.0))

    date_keys = ["date_left_1", "date_left_2"]
    for i, date in enumerate(dates_l[:2]):
        txt(date_keys[i], date, 35.0, (1.0, 1.0, 1.0))

    if col_type == "both":
        txt("right_pill", right_label, 35.0, (1.0, 1.0, 1.0))
        right_keys = ["date_right_1", "date_right_2"]
        for i, date in enumerate(dates_r[:2]):
            txt(right_keys[i], date, 35.0, (1.0, 1.0, 1.0))

    # ── Save ──────────────────────────────────────────────────────────────────
    safe = re.sub(r'[/\\:*?"<>|]', "-", course_name)
    out  = os.path.join(OUTPUT, f"Course - {brand} - {safe}.pdf")
    doc.save(out, garbage=4, deflate=True)
    doc.close()
    return out


if __name__ == "__main__":
    courses = [
        {"name": "Risk Management Workshop (RMW)",   "dates": ["13 - 17 April 2026"]},
        {"name": "National Inspectors Course",        "dates": ["12 - 20 October 2026"]},
        {"name": "Crisis Management Workshop (CMW)", "dates": ["23 - 27 November 2026"]},
    ]
    for c in courses:
        print("Saved:", fill_course("Redline", c["name"], c["dates"]))
