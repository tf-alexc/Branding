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
        output_dir="/Users/alexcraiu/Desktop/Claude Playground/Carousel PDFs",
    )

Templates and fonts are bundled inside this skill folder. Do NOT search the
filesystem for them — they live next to this script.
"""
from __future__ import annotations

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
CAROUSEL_DESC_SIZES = (80, 72, 64, 56)

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


def _track(label: str) -> str:
    """JUST CULTURE -> J U S T  C U L T U R E (double space between words)."""
    return "  ".join(" ".join(w) for w in label.upper().split())


def _sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|]', "-", name).strip()


def _pad_rect(bbox, p: float = 2.0) -> fitz.Rect:
    r = fitz.Rect(bbox)
    return fitz.Rect(r.x0 - p, r.y0 - p, r.x1 + p, r.y1 + p)


def _fit_text(page, rect, text, sizes, color):
    """Insert text into rect, shrinking until it fits. Returns final font size."""
    for size in sizes:
        rc = page.insert_textbox(
            rect, text,
            fontname="osL", fontfile=FONT_LIGHT, fontsize=size,
            color=color, align=0,
        )
        if rc >= 0:
            return size
    raise ValueError(f"Text did not fit at any size: {text!r}")


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
    """Redact the original pill drawing and the title + description text. Uses
    transparent redaction so the gradient under the pill stays intact and the
    new (hug-fit) pill draws cleanly with no seam. Contact pills (size 39.28)
    and footer URLs (size 20) are left untouched."""
    spans = [s for blk in page.get_text("dict")["blocks"] if blk.get("type") == 0
             for line in blk["lines"] for s in line["spans"]]
    # Pill: full removal (vector + tracked text). PILL_COVER matches the
    # original pill bounds tightly so the redaction does not touch surrounding
    # decoration paths.
    page.add_redact_annot(PILL_COVER, fill=None)
    # Title (size 120.85) and description (size 80) text only. Leave anything
    # else (subtitle 26.15 which we already covered, contact 39.28, footer 20)
    # alone.
    for s in spans:
        sz = s["size"]
        if "S U B T I T L E" in s["text"]:
            continue
        if 70 < sz < 90 or sz > 100:
            page.add_redact_annot(_pad_rect(s["bbox"]), fill=None)
    page.apply_redactions()


def _fill_carousel_page(page, *, subtitle, title, description):
    _redact_carousel_placeholders(page)
    _draw_pill(
        page, subtitle,
        pill_left=PILL_LEFT, pill_top=PILL_TOP, pill_h=PILL_HEIGHT,
        pad_x=PILL_PAD_X, fontsize=PILL_FONTSIZE,
        fill=CAROUSEL_PILL_FILL, stroke=CAROUSEL_PILL_STROKE,
    )
    _fit_text(page, CAROUSEL_TITLE_RECT, title, CAROUSEL_TITLE_SIZES, WHITE)
    _fit_text(page, CAROUSEL_DESC_RECT, description, CAROUSEL_DESC_SIZES, DESC_COLOR)


def _redact_blog_placeholders(page):
    """Same approach as the carousel: redact the original pill drawing and
    placeholder text spans, leave the rest of the template untouched."""
    spans = [s for blk in page.get_text("dict")["blocks"] if blk.get("type") == 0
             for line in blk["lines"] for s in line["spans"]]
    page.add_redact_annot(BLOG_PILL_COVER, fill=None)
    for s in spans:
        if "S U B T I T L E" in s["text"]:
            continue
        page.add_redact_annot(_pad_rect(s["bbox"]), fill=None)
    page.apply_redactions()


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


def build(
    *,
    brand: str,
    cover: dict,
    content: list,
    outro: dict,
    blog_description: str | None = None,
    output_dir: str | Path,
):
    """Generate the carousel PDF and the matching blog image JPG.

    Args:
        brand: One of "Baines Simmons", "Redline", "Kenyon", "TrustFlight".
        cover: {"subtitle", "title", "description"} for page 1.
        content: list of 1..4 dicts, each {"subtitle", "title", "description"}.
                 Total slides incl. cover + outro <= 6. If `content` has fewer
                 entries than the template's content pages, the extra template
                 pages are dropped. If more, content pages are cloned.
        outro: {"subtitle", "title", "description"} for the final page.
        blog_description: 2-line description specifically for the blog image.
                          Defaults to cover["description"] if not provided.
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

    output_dir = Path(output_dir)
    brand_dir = output_dir / f"Carousel - {brand}"
    brand_dir.mkdir(parents=True, exist_ok=True)

    safe_title = _sanitize_filename(cover["title"])
    carousel_path = brand_dir / f"Carousel - {brand} - {safe_title}.pdf"
    blog_path = brand_dir / f"Blog Image - {brand} - {safe_title}.jpg"

    # --- Carousel ---
    doc = fitz.open(str(CAROUSEL_TEMPLATES[brand]))
    # Template has 4 pages: cover, 2 content, outro. Adjust the content section.
    # Pages are 0-indexed: 0=cover, 1=content, 2=content, 3=outro.
    template_content_pages = 2
    needed_content_pages = len(content)
    if needed_content_pages < template_content_pages:
        # Drop excess content pages (delete from page index 1 forward).
        for _ in range(template_content_pages - needed_content_pages):
            doc.delete_page(1)
    elif needed_content_pages > template_content_pages:
        # Clone page 1 (a content page) to grow the deck.
        for _ in range(needed_content_pages - template_content_pages):
            doc.copy_page(1, to=2)

    # Re-index outro after content adjustments.
    outro_idx = 1 + needed_content_pages

    _fill_carousel_page(doc[0], **cover)
    for i, slide in enumerate(content):
        _fill_carousel_page(doc[1 + i], **slide)
    _fill_carousel_page(doc[outro_idx], **outro)

    # garbage=0: aggressive cleanup wipes shared font glyphs used by the outro
    # contact pills (size 39.28 OpenSans-Regular). Default save preserves them.
    doc.save(str(carousel_path), deflate=True)
    doc.close()

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
