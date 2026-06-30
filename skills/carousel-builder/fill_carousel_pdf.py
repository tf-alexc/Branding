"""Carousel + blog image generator. One call, both outputs.

Usage:
    from fill_carousel_pdf import build
    build(
        brand="Baines Simmons",
        cover={"subtitle": "JUST CULTURE", "title": "...", "description": "..."},
        content=[
            {"subtitle": "WHAT IT IS", "title": "...", "description": "..."},
            {"subtitle": "WHY IT MATTERS", "title": "...", "description": "..."},
        ],
        outro={"subtitle": "GET IN TOUCH", "title": "...", "description": "..."},
        blog_description="Short 2-line version for the blog image.",
        source_url="https://example.com/article",   # v2 BSL only — drives the QR
        output_dir="/Users/alexcraiu/Desktop/Claude Playground/Carousel PDFs",
    )

Templates and fonts are bundled inside this skill folder. Do NOT search the
filesystem for them — they live next to this script.
"""
from __future__ import annotations

import io
import re
from pathlib import Path

import fitz

SKILL_DIR = Path(__file__).resolve().parent

CAROUSEL_TEMPLATES = {
    "Baines Simmons": SKILL_DIR / "Carousel - Baines Simmons - Template.pdf",
    "Redline":        SKILL_DIR / "Carousel - Redline - Template.pdf",
    "Kenyon":         SKILL_DIR / "Carousel - Kenyon - Template.pdf",
    "TrustFlight":    SKILL_DIR / "Carousel - TrustFlight - Template.pdf",
}

BLOG_TEMPLATE = SKILL_DIR / "Blog Image - Template.pdf"
BLOG_PAGE_INDEX = {"Baines Simmons": 0, "Redline": 1, "Kenyon": 2, "TrustFlight": 3}

FONT_LIGHT = str(SKILL_DIR / "OpenSans-Light.ttf")
FONT_BOLD = str(SKILL_DIR / "OpenSans-Bold.ttf")

NAVY = (0, 0, 26 / 255)
WHITE = (1, 1, 1)
DESC_COLOR = (199 / 255, 213 / 255, 1.0)
# Electric — TrustFlight brand colour #03D4FF. Used for the outro QR code.
ELECTRIC = (3 / 255, 212 / 255, 255 / 255)
# Pill fill matches the original template pill interior exactly — sampled from
# the template's vector drawing. Using this avoids any visible seam when we
# cover the old pill before redrawing a new (narrower) one.
CAROUSEL_PILL_FILL = (0.0, 0.075, 0.224)
CAROUSEL_PILL_STROKE = (0.278, 0.788, 0.973)
BLOG_PILL_FILL = (0.0, 0.078, 0.231)
BLOG_PILL_STROKE = (0.0, 0.796, 0.988)

# Carousel page is 1200 x 1500 portrait.
# PILL_COVER matches the original pill outline tightly so the navy cover
# only touches area the pill was already occupying (no gradient seam).
PILL_COVER = fitz.Rect(72, 225, 698, 308)
PILL_LEFT = 73.0
PILL_TOP = 225.79
PILL_HEIGHT = 80.66
PILL_PAD_X = 50.0
PILL_FONTSIZE = 26.0

CAROUSEL_TITLE_RECT = fitz.Rect(70, 320, 1170, 630)
CAROUSEL_DESC_RECT = fitz.Rect(70, 660, 1170, 1130)
CAROUSEL_TITLE_SIZES = (120, 110, 100, 90, 80, 70, 60)
CAROUSEL_DESC_SIZES = (88, 80, 74, 68, 62, 58)

# Blog image is 1920 x 1080 landscape.
BLOG_PILL_COVER = fitz.Rect(72, 318, 752, 406)
BLOG_PILL_LEFT = 73.0
BLOG_PILL_TOP = 318.21
BLOG_PILL_HEIGHT = 87.71
BLOG_PILL_PAD_X = 55.0
BLOG_PILL_FONTSIZE = 28.5

BLOG_TITLE_RECT = fitz.Rect(70, 410, 1850, 720)
BLOG_DESC_RECT = fitz.Rect(70, 730, 1850, 920)
BLOG_TITLE_SIZES = (120, 110, 100, 90, 80, 70, 60)
BLOG_DESC_SIZES = (80, 72, 64, 56)

_FONT_BOLD_OBJ = fitz.Font(fontfile=FONT_BOLD)
_FONT_LIGHT_OBJ = fitz.Font(fontfile=FONT_LIGHT)

LINE_HEIGHT_FACTOR = 1.2
# insert_textbox tacks on roughly 0.3 * fontsize of ascender padding above the
# first line on top of (n_lines * size * lineheight). Account for it so our
# fit prediction matches PyMuPDF's actual rendering.
ASCENT_OVERHEAD = 0.3


def _track(label: str) -> str:
    """JUST CULTURE -> J U S T  C U L T U R E (double space between words)."""
    return "  ".join(" ".join(w) for w in label.upper().split())


def _sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|]', "-", name).strip()


def _pad_rect(bbox, p: float = 2.0) -> fitz.Rect:
    r = fitz.Rect(bbox)
    return fitz.Rect(r.x0 - p, r.y0 - p, r.x1 + p, r.y1 + p)


_SENTENCE_SPLIT = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9"\'(])')


def _format_sentences(text: str, max_per_block: int = 2) -> str:
    """Lay text out for readability instead of as one dense block:
    - one sentence per line (line break between sentences)
    - a blank line after every `max_per_block` sentences, so no block of text
      runs longer than two sentences

    Returns a string with embedded '\\n'. If the text is already a single
    sentence, it comes back unchanged."""
    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(text.strip()) if s.strip()]
    if len(sentences) <= 1:
        return text.strip()
    out_lines: list[str] = []
    for i, sentence in enumerate(sentences):
        if i and i % max_per_block == 0:
            out_lines.append("")          # blank line = new block
        out_lines.append(sentence)
    return "\n".join(out_lines)


def _wrap_lines(font: fitz.Font, text: str, fontsize: float, max_width: float):
    """Greedy word wrap that respects explicit newlines. Returns
    (lines, longest_word_width). Each '\\n' forces a hard break, and blank
    lines (from sentence-block separators) are preserved so the height
    prediction matches what insert_textbox actually renders."""
    space_w = font.text_length(" ", fontsize=fontsize)
    lines: list[str] = []
    longest_word = 0.0
    for source_line in text.split("\n"):
        words = source_line.split()
        if not words:
            lines.append("")             # preserve blank separator line
            continue
        cur: list[str] = []
        cur_w = 0.0
        for w in words:
            ww = font.text_length(w, fontsize=fontsize)
            longest_word = max(longest_word, ww)
            if not cur:
                cur = [w]
                cur_w = ww
            elif cur_w + space_w + ww <= max_width:
                cur.append(w)
                cur_w += space_w + ww
            else:
                lines.append(" ".join(cur))
                cur = [w]
                cur_w = ww
        if cur:
            lines.append(" ".join(cur))
    if not lines:
        return [""], 0.0
    return lines, longest_word


def _pick_fitting_size(font: fitz.Font, text: str, rect: fitz.Rect, sizes) -> float:
    """Largest size from `sizes` whose wrapped layout fits inside `rect`."""
    for size in sizes:
        lines, longest_word = _wrap_lines(font, text, size, rect.width)
        if longest_word > rect.width:
            continue  # a single word overflows — must shrink
        total_h = (len(lines) * LINE_HEIGHT_FACTOR + ASCENT_OVERHEAD) * size
        if total_h <= rect.height:
            return size
    return sizes[-1]


def _fit_text(page, rect, text, sizes, color):
    """Insert text into rect at the largest size that wraps cleanly inside it.
    The fit is computed BEFORE any drawing happens, so we never leave ghost
    glyphs from oversized attempts on the page."""
    size = _pick_fitting_size(_FONT_LIGHT_OBJ, text, rect, sizes)
    page.insert_textbox(
        rect, text,
        fontname="osL", fontfile=FONT_LIGHT, fontsize=size,
        color=color, align=0, lineheight=LINE_HEIGHT_FACTOR,
    )
    return size


def _draw_pill(page, label, *, pill_left, pill_top, pill_h, pad_x, fontsize, fill, stroke):
    """Draw a new pill that hugs the label exactly. Caller is responsible for
    covering / clearing the original pill before calling this."""
    tracked = _track(label)
    text_w = _FONT_BOLD_OBJ.text_length(tracked, fontsize=fontsize)
    pill_w = text_w + 2 * pad_x
    pill_rect = fitz.Rect(pill_left, pill_top, pill_left + pill_w, pill_top + pill_h)
    page.draw_rect(pill_rect, color=stroke, fill=fill, width=1.0, radius=0.5)
    baseline_y = pill_top + pill_h / 2 + fontsize / 3
    page.insert_text(
        fitz.Point(pill_left + pad_x, baseline_y),
        tracked,
        fontname="osB", fontfile=FONT_BOLD, fontsize=fontsize,
        color=WHITE,
    )


def _redact_carousel_placeholders(page):
    """Two-pass clean-up:
    1. Fully remove the original pill drawing (fill + stroke) with aggressive
       line-art removal — otherwise the pill's stroke survives the default
       redaction and shows as a doubled outline next to the new (hugged) pill.
    2. Remove the title + description placeholder text spans without touching
       line art (gradient waves, decoration stripes) or the arrow image (which
       lives at the bottom of the page and would otherwise be clipped by the
       last description line's redaction box, leaving a grey bar)."""
    # Pass 1 — pill: nuke vectors inside the pill rect, leave images alone.
    page.add_redact_annot(PILL_COVER, fill=None)
    page.apply_redactions(
        images=fitz.PDF_REDACT_IMAGE_NONE,
        graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_TOUCHED,
    )
    # Pass 2 — title + description text only. Spare images and line art.
    spans = [s for blk in page.get_text("dict")["blocks"] if blk.get("type") == 0
             for line in blk["lines"] for s in line["spans"]]
    for s in spans:
        sz = s["size"]
        if "S U B T I T L E" in s["text"]:
            continue
        if 70 < sz < 90 or sz > 100:
            page.add_redact_annot(_pad_rect(s["bbox"]), fill=None)
    page.apply_redactions(
        images=fitz.PDF_REDACT_IMAGE_NONE,
        graphics=fitz.PDF_REDACT_LINE_ART_NONE,
    )


def _fill_carousel_page(page, *, subtitle, title, description):
    _redact_carousel_placeholders(page)
    _draw_pill(
        page, subtitle,
        pill_left=PILL_LEFT, pill_top=PILL_TOP, pill_h=PILL_HEIGHT,
        pad_x=PILL_PAD_X, fontsize=PILL_FONTSIZE,
        fill=CAROUSEL_PILL_FILL, stroke=CAROUSEL_PILL_STROKE,
    )
    _fit_text(page, CAROUSEL_TITLE_RECT, title, CAROUSEL_TITLE_SIZES, WHITE)
    _fit_text(page, CAROUSEL_DESC_RECT, _format_sentences(description),
              CAROUSEL_DESC_SIZES, DESC_COLOR)


def _redact_blog_placeholders(page):
    """Same two-pass approach as the carousel: aggressive vector removal for
    the pill, conservative text-only removal for the placeholders."""
    page.add_redact_annot(BLOG_PILL_COVER, fill=None)
    page.apply_redactions(
        images=fitz.PDF_REDACT_IMAGE_NONE,
        graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_TOUCHED,
    )
    spans = [s for blk in page.get_text("dict")["blocks"] if blk.get("type") == 0
             for line in blk["lines"] for s in line["spans"]]
    for s in spans:
        if "S U B T I T L E" in s["text"]:
            continue
        page.add_redact_annot(_pad_rect(s["bbox"]), fill=None)
    page.apply_redactions(
        images=fitz.PDF_REDACT_IMAGE_NONE,
        graphics=fitz.PDF_REDACT_LINE_ART_NONE,
    )


def _fill_blog_page(page, *, subtitle, title, description):
    _redact_blog_placeholders(page)
    _draw_pill(
        page, subtitle,
        pill_left=BLOG_PILL_LEFT, pill_top=BLOG_PILL_TOP, pill_h=BLOG_PILL_HEIGHT,
        pad_x=BLOG_PILL_PAD_X, fontsize=BLOG_PILL_FONTSIZE,
        fill=BLOG_PILL_FILL, stroke=BLOG_PILL_STROKE,
    )
    _fit_text(page, BLOG_TITLE_RECT, title, BLOG_TITLE_SIZES, WHITE)
    _fit_text(page, BLOG_DESC_RECT, description, BLOG_DESC_SIZES, DESC_COLOR)


def _build_v1_carousel(*, brand, cover, content, outro, carousel_path):
    """v1 pipeline: 4-page template with two interchangeable content pages.
    Used by Redline, Kenyon, and TrustFlight. Content slides all have the
    same title + description shape.

    Built via insert_pdf so each output page has its own content stream —
    doc.copy_page() left clones sharing the source stream, causing later
    fills to bleed into earlier pages (every content slide ended up showing
    the same — usually the last — title and description)."""
    src = fitz.open(str(CAROUSEL_TEMPLATES[brand]))
    doc = fitz.open()
    doc.insert_pdf(src, from_page=0, to_page=0)  # cover
    for _ in content:
        # v1 has interchangeable content pages 1 and 2. Use page 1 as the
        # source for every content slide — they have identical layouts.
        doc.insert_pdf(src, from_page=1, to_page=1)
    doc.insert_pdf(src, from_page=3, to_page=3)  # outro
    src.close()

    _fill_carousel_page(doc[0], **cover)
    for i, slide in enumerate(content):
        _fill_carousel_page(doc[1 + i], **slide)
    _fill_carousel_page(doc[-1], **outro)

    doc.save(str(carousel_path), deflate=True)
    doc.close()


# ============================================================================
# v2 (new Baines Simmons template): typed content slides + CTA pills
# ----------------------------------------------------------------------------
# The new BSL template is six pages with four specialised content layouts.
# Pages: 0=cover, 1=paragraph, 2=bullets, 3=checklist, 4=quote, 5=outro.
# Each content slide takes a `type` discriminator picking which template page.
# The cover and outro both have a template-fixed CTA pill ("CONTINUE READING"
# / "READ THE FULL ARTICLE") that we leave untouched.
# ============================================================================

V2_BRANDS = {"Baines Simmons"}

V2_TYPE_PAGE = {
    "paragraph": 1,
    "bullets":   2,
    "checklist": 3,
    "quote":     4,
}
V2_COVER_PAGE = 0
V2_OUTRO_PAGE = 5

# Shared geometry — title at 120pt fits in this rect on cover, bullets,
# checklist, and outro pages.
V2_TITLE_RECT_120 = fitz.Rect(70, 320, 1170, 630)
V2_TITLE_SIZES_120 = (120, 110, 100, 90, 80, 70, 60)

# Cover + outro description (tighter than v1 because the CTA pill sits below).
V2_COVER_DESC_RECT = fitz.Rect(70, 660, 1170, 970)
V2_COVER_DESC_SIZES = (88, 80, 74, 68, 62, 58)

# Paragraph slide — smaller title (90pt), big body block.
V2_PARAGRAPH_TITLE_RECT = fitz.Rect(70, 340, 1170, 590)
V2_PARAGRAPH_TITLE_SIZES = (90, 80, 70, 60)
V2_PARAGRAPH_BODY_RECT = fitz.Rect(70, 620, 1170, 1200)
V2_PARAGRAPH_BODY_SIZES = (90, 82, 74, 68, 62, 56, 52)

# List items (bullets + checklist share container geometry).
V2_LIST_CONTAINERS = [
    fitz.Rect(56.5, 655.5, 1154.0, 768.0),
    fitz.Rect(56.5, 794.0, 1154.0, 907.0),
    fitz.Rect(56.5, 932.5, 1154.0, 1045.0),
    fitz.Rect(56.5, 1069.4, 1154.0, 1182.0),
]
V2_LIST_TEXT_X = 167.0      # text starts after the icon
V2_LIST_TEXT_RIGHT = 1120.0
V2_LIST_TEXT_WIDTH = V2_LIST_TEXT_RIGHT - V2_LIST_TEXT_X  # 953
V2_LIST_ITEM_SIZES = (51, 46, 41, 36, 32)


def _fit_single_line(page, *, x, baseline_y, max_width, text, sizes, color, fontfile, fontname):
    """Insert `text` on ONE line, shrinking from sizes[0] until it fits the
    given width. Raises if even the smallest size overflows — the caller
    (or the user upstream) needs to shorten the item, since two rows per
    list item is explicitly forbidden by the content rules."""
    font = _FONT_LIGHT_OBJ if fontfile == FONT_LIGHT else _FONT_BOLD_OBJ
    for size in sizes:
        if font.text_length(text, fontsize=size) <= max_width:
            page.insert_text(
                fitz.Point(x, baseline_y + size / 3),
                text,
                fontname=fontname, fontfile=fontfile, fontsize=size,
                color=color,
            )
            return size
    raise ValueError(
        f"List item too long to fit on one row at any size: {text!r}. "
        f"Max width is {max_width:.0f}pt; shorten the item."
    )


# Quote slide — title 100pt, indented quote 78pt, attribution under.
V2_QUOTE_TITLE_RECT = fitz.Rect(70, 340, 1170, 610)
V2_QUOTE_TITLE_SIZES = (100, 90, 80, 70, 60)
V2_QUOTE_RECT = fitz.Rect(190, 620, 1130, 1010)
V2_QUOTE_SIZES = (78, 70, 62, 54, 46)
V2_QUOTE_ATTR_RECT = fitz.Rect(190, 1050, 1130, 1190)
V2_QUOTE_ATTR_SIZES = (60, 50, 42, 36, 30)

# Outro QR-code placeholder (the red square on the source template).
V2_OUTRO_QR_RECT = fitz.Rect(783, 1033, 1050, 1300)


# Electric (#03D4FF) as a hex string for segno's `dark` argument.
ELECTRIC_HEX = "#03D4FF"


def _make_qr_png_bytes(url: str) -> bytes:
    """Generate a high-error-correction QR code PNG for the given URL.

    Modules are always rendered in Electric (#03D4FF), the TrustFlight brand
    colour, on a transparent background so the navy gradient shows through."""
    import segno
    qr = segno.make(url, error="h")
    buf = io.BytesIO()
    # scale=20 yields plenty of resolution for the 267x268 placement rect.
    qr.save(buf, kind="png", scale=20, dark=ELECTRIC_HEX, light=None, border=2)
    return buf.getvalue()


def _redact_v2_pill_only(page):
    """Two-pass pill clearance plus optional extra rect (used for unused list
    container removal)."""
    page.add_redact_annot(PILL_COVER, fill=None)
    page.apply_redactions(
        images=fitz.PDF_REDACT_IMAGE_NONE,
        graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_TOUCHED,
    )


def _redact_v2_text_spans(page, size_ranges):
    """Redact placeholder text whose font size falls inside any (lo, hi) range.
    Leaves vector decorations and images untouched."""
    spans = [s for blk in page.get_text("dict")["blocks"] if blk.get("type") == 0
             for line in blk["lines"] for s in line["spans"]]
    for s in spans:
        if "S U B T I T L E" in s["text"]:
            continue
        sz = s["size"]
        if any(lo <= sz <= hi for lo, hi in size_ranges):
            page.add_redact_annot(_pad_rect(s["bbox"]), fill=None)
    page.apply_redactions(
        images=fitz.PDF_REDACT_IMAGE_NONE,
        graphics=fitz.PDF_REDACT_LINE_ART_NONE,
    )


def _draw_v2_pill(page, label):
    _draw_pill(
        page, label,
        pill_left=PILL_LEFT, pill_top=PILL_TOP, pill_h=PILL_HEIGHT,
        pad_x=PILL_PAD_X, fontsize=PILL_FONTSIZE,
        fill=CAROUSEL_PILL_FILL, stroke=CAROUSEL_PILL_STROKE,
    )


def _fill_v2_cover(page, *, subtitle, title, description):
    """Page 0 of the v2 template. Title 120pt, description 80pt. The CTA pill
    ("CONTINUE READING") at size 42.57pt is template-fixed and left intact."""
    _redact_v2_pill_only(page)
    _redact_v2_text_spans(page, [(115, 125), (75, 85)])
    _draw_v2_pill(page, subtitle)
    _fit_text(page, V2_TITLE_RECT_120, title, V2_TITLE_SIZES_120, WHITE)
    _fit_text(page, V2_COVER_DESC_RECT, _format_sentences(description),
              V2_COVER_DESC_SIZES, DESC_COLOR)


def _fill_v2_paragraph(page, *, subtitle, title, body):
    """Title 90pt, body 72pt. Use this layout when the slide is one prose
    paragraph that should breathe. The body is reflowed to one sentence per
    line with a blank line after every two sentences, so it never reads as a
    dense block."""
    _redact_v2_pill_only(page)
    _redact_v2_text_spans(page, [(85, 95), (70, 75)])
    _draw_v2_pill(page, subtitle)
    _fit_text(page, V2_PARAGRAPH_TITLE_RECT, title, V2_PARAGRAPH_TITLE_SIZES, WHITE)
    _fit_text(page, V2_PARAGRAPH_BODY_RECT, _format_sentences(body),
              V2_PARAGRAPH_BODY_SIZES, DESC_COLOR)


def _fill_v2_list_slide(page, *, subtitle, title, items):
    """Shared logic for bullets and checklist. 1 to 4 items. The list-item
    icons (cyan dot or green check) ship as embedded images inside a form
    XObject that PyMuPDF's `apply_redactions` cannot reach — so the container
    vector is redacted, and the icon area is painted over with a flat navy
    that matches the gradient at that position."""
    if not 1 <= len(items) <= 4:
        raise ValueError(f"List slide needs 1 to 4 items, got {len(items)}")
    # Pass 1: pill + unused container vectors (touched-removal kills the
    # rounded-rect drawing entirely). Images stay untouched.
    page.add_redact_annot(PILL_COVER, fill=None)
    for i in range(len(items), 4):
        page.add_redact_annot(V2_LIST_CONTAINERS[i], fill=None)
    page.apply_redactions(
        images=fitz.PDF_REDACT_IMAGE_NONE,
        graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_TOUCHED,
    )
    # Cover any orphan icon image (icons live at x≈75-155 inside each slot).
    # Use a fill close to the gradient at that y-band so the patch is subtle.
    ICON_COVER_FILL = (0.0, 13 / 255, 70 / 255)
    for i in range(len(items), 4):
        container = V2_LIST_CONTAINERS[i]
        icon_cover = fitz.Rect(70, container.y0 + 16, 160, container.y1 - 16)
        page.draw_rect(icon_cover, color=None, fill=ICON_COVER_FILL, overlay=True)
    # Pass 2: title (120pt) + item text (51pt) placeholders.
    _redact_v2_text_spans(page, [(115, 125), (48, 54)])
    _draw_v2_pill(page, subtitle)
    _fit_text(page, V2_TITLE_RECT_120, title, V2_TITLE_SIZES_120, WHITE)
    # Single-line per item. The script raises if an item is too long even at
    # the smallest size — content rule forbids two-row items.
    for i, item in enumerate(items):
        container = V2_LIST_CONTAINERS[i]
        baseline_y = container.y0 + container.height / 2
        _fit_single_line(
            page,
            x=V2_LIST_TEXT_X, baseline_y=baseline_y,
            max_width=V2_LIST_TEXT_WIDTH,
            text=item, sizes=V2_LIST_ITEM_SIZES, color=WHITE,
            fontfile=FONT_LIGHT, fontname="osL",
        )


def _fill_v2_bullets(page, *, subtitle, title, items):
    """Page 2 — items shown with cyan bullet dots in rounded containers."""
    _fill_v2_list_slide(page, subtitle=subtitle, title=title, items=items)


def _fill_v2_checklist(page, *, subtitle, title, items):
    """Page 3 — items shown with green checkmarks in rounded containers."""
    _fill_v2_list_slide(page, subtitle=subtitle, title=title, items=items)


def _fill_v2_quote(page, *, subtitle, title, quote, attribution=None):
    """Page 4 — large quote with optional attribution line."""
    _redact_v2_pill_only(page)
    # Title 100pt, quote 77.66pt. Attribution placeholder is also 77.66pt and
    # gets caught by the same range, which is what we want.
    _redact_v2_text_spans(page, [(95, 105), (75, 82)])
    _draw_v2_pill(page, subtitle)
    _fit_text(page, V2_QUOTE_TITLE_RECT, title, V2_QUOTE_TITLE_SIZES, WHITE)
    _fit_text(page, V2_QUOTE_RECT, quote, V2_QUOTE_SIZES, DESC_COLOR)
    if attribution:
        _fit_text(page, V2_QUOTE_ATTR_RECT, attribution, V2_QUOTE_ATTR_SIZES, DESC_COLOR)


def _fill_v2_outro(page, *, subtitle, title, description, source_url=None):
    """Page 5 — title + final description. The CTA pill ("READ THE FULL
    ARTICLE") at size 31.78pt is template-fixed and left intact. The new BSL
    outro has no contact pills (replaced by the CTA).

    The red rectangle in the bottom-right of the template is a QR code
    placeholder. If `source_url` is provided, we redact the red rectangle and
    overlay a QR code that links to the source article. If not provided, we
    redact it anyway so the empty page doesn't ship with a giant red square."""
    # Pass 0: remove the red QR placeholder. Done first so the redaction does
    # not interact with the pill / text passes below.
    page.add_redact_annot(V2_OUTRO_QR_RECT, fill=None)
    page.apply_redactions(
        images=fitz.PDF_REDACT_IMAGE_NONE,
        graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_TOUCHED,
    )
    _redact_v2_pill_only(page)
    _redact_v2_text_spans(page, [(115, 125), (75, 85)])
    _draw_v2_pill(page, subtitle)
    _fit_text(page, V2_TITLE_RECT_120, title, V2_TITLE_SIZES_120, WHITE)
    _fit_text(page, V2_COVER_DESC_RECT, _format_sentences(description),
              V2_COVER_DESC_SIZES, DESC_COLOR)
    if source_url:
        page.insert_image(V2_OUTRO_QR_RECT, stream=_make_qr_png_bytes(source_url))


def _build_v2_carousel(*, brand, cover, content, outro, carousel_path, source_url=None):
    """Generate the v2 BSL carousel. Content entries pick which template page
    to use via a `type` field. The selected pages are stitched in order
    between the cover and the outro. `source_url` drives the QR code rendered
    over the red placeholder on the outro page.

    NOTE: we build the deck via insert_pdf, not doc.select(), because select()
    with a repeated source index produces pages that share the same content
    stream — filling one would bleed into the others (two paragraph slides
    would end up showing the same body). insert_pdf gives each output page an
    independent content stream so fills stay isolated."""
    src = fitz.open(str(CAROUSEL_TEMPLATES[brand]))
    doc = fitz.open()  # empty target
    doc.insert_pdf(src, from_page=V2_COVER_PAGE, to_page=V2_COVER_PAGE)
    for c in content:
        t = c.get("type")
        if t not in V2_TYPE_PAGE:
            raise ValueError(
                f"Unknown slide type {t!r}. Use one of {sorted(V2_TYPE_PAGE)}"
            )
        idx = V2_TYPE_PAGE[t]
        doc.insert_pdf(src, from_page=idx, to_page=idx)
    doc.insert_pdf(src, from_page=V2_OUTRO_PAGE, to_page=V2_OUTRO_PAGE)
    src.close()

    _fill_v2_cover(doc[0], **cover)
    for i, c in enumerate(content):
        page = doc[1 + i]
        t = c["type"]
        if t == "paragraph":
            _fill_v2_paragraph(page, subtitle=c["subtitle"], title=c["title"],
                               body=c["body"])
        elif t == "bullets":
            _fill_v2_bullets(page, subtitle=c["subtitle"], title=c["title"],
                             items=c["items"])
        elif t == "checklist":
            _fill_v2_checklist(page, subtitle=c["subtitle"], title=c["title"],
                               items=c["items"])
        elif t == "quote":
            _fill_v2_quote(page, subtitle=c["subtitle"], title=c["title"],
                           quote=c["quote"], attribution=c.get("attribution"))
    _fill_v2_outro(doc[-1], **outro, source_url=source_url)

    doc.save(str(carousel_path), deflate=True)
    doc.close()


def build(
    *,
    brand: str,
    cover: dict,
    content: list,
    outro: dict,
    blog_description: str | None = None,
    source_url: str | None = None,
    output_dir: str | Path,
):
    """Generate the carousel PDF and the matching blog image JPG.

    Args:
        brand: One of "Baines Simmons", "Redline", "Kenyon", "TrustFlight".
        cover: {"subtitle", "title", "description"} for page 1.
        content: 1..4 dicts. v1 brands take {"subtitle", "title", "description"};
                 v2 Baines Simmons takes a `type` discriminator plus the fields
                 that type needs (paragraph: body; bullets/checklist: items;
                 quote: quote + optional attribution).
        outro: {"subtitle", "title", "description"} for the final page.
        blog_description: 2-line description specifically for the blog image.
                          Defaults to cover["description"] if not provided.
        source_url: URL of the source article. On v2 Baines Simmons this is
                    encoded into a QR code overlaid on the red placeholder on
                    the outro. Ignored on v1 brands. If omitted on v2 BSL, the
                    red placeholder is redacted but no QR is rendered.
        output_dir: parent folder. A subfolder `Carousel - [Brand]/` is created.

    Returns:
        dict with keys "carousel_pdf", "blog_image_jpg", "pages".
    """
    if brand not in CAROUSEL_TEMPLATES:
        raise ValueError(f"Unknown brand: {brand}")
    if len(content) < 1:
        raise ValueError("Need at least 1 content slide between cover and outro.")
    total_slides = 1 + len(content) + 1
    if total_slides > 6:
        raise ValueError(f"Too many slides: {total_slides} > 6 cap.")

    # No-duplicate guard: every content slide must carry a distinct idea.
    # Keys on the title only, since the v1 and v2 schemas have different
    # supporting fields (description / body / items / quote) but always
    # include a title.
    titles_seen: dict[str, int] = {}
    for i, slide in enumerate(content):
        t = slide["title"].strip().lower()
        if t in titles_seen:
            raise ValueError(
                f"Duplicate content slide titles at index {titles_seen[t]} "
                f"and {i}: {slide['title']!r}. Every content slide must carry "
                "a distinct idea."
            )
        titles_seen[t] = i

    output_dir = Path(output_dir)
    brand_dir = output_dir / f"Carousel - {brand}"
    brand_dir.mkdir(parents=True, exist_ok=True)

    safe_title = _sanitize_filename(cover["title"])
    carousel_path = brand_dir / f"Carousel - {brand} - {safe_title}.pdf"
    blog_path = brand_dir / f"Blog Image - {brand} - {safe_title}.jpg"

    # --- Carousel ---
    if brand in V2_BRANDS:
        _build_v2_carousel(
            brand=brand, cover=cover, content=content, outro=outro,
            carousel_path=carousel_path, source_url=source_url,
        )
    else:
        _build_v1_carousel(
            brand=brand, cover=cover, content=content, outro=outro,
            carousel_path=carousel_path,
        )

    # --- Blog image ---
    blog_doc = fitz.open(str(BLOG_TEMPLATE))
    brand_page_idx = BLOG_PAGE_INDEX[brand]
    # Keep only the relevant brand page.
    keep = [brand_page_idx]
    blog_doc.select(keep)

    _fill_blog_page(
        blog_doc[0],
        subtitle=cover["subtitle"],
        title=cover["title"],
        description=blog_description or cover["description"],
    )

    # Render to JPG. Target width >= 1500 px. Source width is 1920, so scale = 1.0 gives 1920 wide.
    pix = blog_doc[0].get_pixmap(matrix=fitz.Matrix(1.0, 1.0))
    pix.save(str(blog_path), jpg_quality=92)
    blog_doc.close()

    return {
        "carousel_pdf": str(carousel_path),
        "blog_image_jpg": str(blog_path),
        "pages": total_slides,
    }
