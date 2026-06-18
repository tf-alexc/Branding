#!/usr/bin/env python3
"""
Fill a Kenyon certificate template with recipient details.

Usage (import):
    from fill_certificate import fill_certificate
    output = fill_certificate("training", "John Smith", "12th June 2026", "Emergency Planning")
    print(output)  # path to saved PDF
"""

import fitz
import os
import re

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE   = os.path.join(SKILL_DIR, "Certificate - Kenyon - Template.pdf")
FONT_FILE  = os.path.join(SKILL_DIR, "OpenSans-VariableFont_wdth,wght.ttf")
OUTPUT_DIR = os.path.expanduser("~/Desktop")

SAPPHIRE = (0 / 255, 92 / 255, 167 / 255)  # #005CA7
WHITE    = (1.0, 1.0, 1.0)

PAGE_INDEX = {
    "training":         0,
    "academy training": 1,
    "acceptance":       2,
    "achievement":      3,
}

# Layout: { field: (redact_rect, insert_x, insert_baseline_y) }
LAYOUT = {
    0: {  # Training
        "name":   (fitz.Rect(263, 266, 806, 317), 263.6, 305.0),
        "course": (fitz.Rect(263, 367, 810, 405), 263.6, 395.0),
        "date":   (fitz.Rect(263, 447, 430, 485), 263.6, 475.0),
    },
    1: {  # Academy Training
        "name":   (fitz.Rect(263, 266, 806, 317), 263.6, 305.0),
        "course": (fitz.Rect(263, 367, 810, 405), 263.6, 395.0),
        "date":   (fitz.Rect(263, 435, 430, 473), 263.6, 463.0),
    },
    2: {  # Acceptance — no course
        "name": (fitz.Rect(263, 266, 806, 317), 263.6, 305.0),
        "date": (fitz.Rect(263, 435, 430, 473), 263.6, 463.0),
    },
    3: {  # Achievement — incident field, not course
        "name":     (fitz.Rect(263, 266, 806, 317), 263.6, 305.0),
        "incident": (fitz.Rect(263, 384, 810, 422), 263.6, 412.0),
        "date":     (fitz.Rect(263, 483, 430, 521), 263.6, 511.0),
    },
}

SUPERSCRIPT_RISE = 22.0  # pt above the main baseline


def _auto_fontsize(font, text, max_size, max_width, min_size=10):
    size = max_size
    while size > min_size:
        if font.text_length(text, fontsize=size) <= max_width:
            return size
        size -= 1
    return min_size


def _insert_date(page, x, baseline_y, date_str, font):
    """Render date string; raises ordinal suffix (st/nd/rd/th) as superscript."""
    m = re.search(r'(\d+)(st|nd|rd|th)', date_str, re.IGNORECASE)
    if m:
        before  = date_str[:m.start()] + m.group(1)  # e.g. "June 12"
        ordinal = m.group(2)                           # e.g. "th"
        after   = date_str[m.end():]                   # e.g. " 2026"

        x_cur = x
        if before:
            page.insert_text(fitz.Point(x_cur, baseline_y), before,
                             fontsize=24, fontfile=FONT_FILE, fontname="ks_font",
                             color=SAPPHIRE)
            x_cur += font.text_length(before, fontsize=24)

        page.insert_text(fitz.Point(x_cur, baseline_y - SUPERSCRIPT_RISE), ordinal,
                         fontsize=14, fontfile=FONT_FILE, fontname="ks_font",
                         color=SAPPHIRE)
        x_cur += font.text_length(ordinal, fontsize=14)

        if after:
            page.insert_text(fitz.Point(x_cur, baseline_y), after,
                             fontsize=24, fontfile=FONT_FILE, fontname="ks_font",
                             color=SAPPHIRE)
    else:
        page.insert_text(fitz.Point(x, baseline_y), date_str,
                         fontsize=24, fontfile=FONT_FILE, fontname="ks_font",
                         color=SAPPHIRE)


def fill_certificate(cert_type, name, date, course_or_incident=None, output_path=None):
    """
    Generate a filled Kenyon certificate PDF.

    cert_type:            "training" | "academy training" | "acceptance" | "achievement"
    name:                 Recipient full name.
    date:                 Date string, e.g. "12th June 2026". Ordinal rendered as superscript.
    course_or_incident:   Course title (training/academy training), incident name (achievement),
                          or None (acceptance).
    output_path:          Full output path. Defaults to ~/Desktop/Certificate - Kenyon - ...pdf
    """
    key = cert_type.lower().strip()
    if key not in PAGE_INDEX:
        raise ValueError(f"Unknown cert type {cert_type!r}. Must be one of: {list(PAGE_INDEX)}")

    page_idx = PAGE_INDEX[key]
    layout   = LAYOUT[page_idx]
    font     = fitz.Font(fontfile=FONT_FILE)

    doc  = fitz.open(TEMPLATE)
    page = doc[page_idx]

    # Redact placeholder fields
    page.add_redact_annot(layout["name"][0], fill=WHITE)
    page.add_redact_annot(layout["date"][0], fill=WHITE)
    if "course" in layout and course_or_incident:
        page.add_redact_annot(layout["course"][0], fill=WHITE)
    if "incident" in layout and course_or_incident:
        page.add_redact_annot(layout["incident"][0], fill=WHITE)

    page.apply_redactions(
        images   = fitz.PDF_REDACT_IMAGE_NONE,
        graphics = fitz.PDF_REDACT_LINE_ART_NONE,
    )

    # Insert name
    _, nx, ny = layout["name"]
    name_size = _auto_fontsize(font, name, 34, 806 - nx)
    page.insert_text(fitz.Point(nx, ny), name,
                     fontsize=name_size,
                     fontfile=FONT_FILE, fontname="ks_font",
                     color=SAPPHIRE)

    # Insert date
    _, dx, dy = layout["date"]
    _insert_date(page, dx, dy, date, font)

    # Insert course or incident
    if course_or_incident:
        field_key = "course" if "course" in layout else "incident"
        _, fx, fy = layout[field_key]
        ci_size = _auto_fontsize(font, course_or_incident, 24, 810 - fx)
        page.insert_text(fitz.Point(fx, fy), course_or_incident,
                         fontsize=ci_size,
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
