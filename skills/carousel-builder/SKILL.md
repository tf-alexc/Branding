---
name: carousel-builder
description: Build LinkedIn carousel PDFs (multi-page social posts) by summarising an article or brief into 6 slides or fewer using a brand-specific PDF template. Use whenever the user asks for a "carousel", "LinkedIn carousel", "multi-page LinkedIn post", or similar.
---

# Carousel Builder

Heavily summarise an article, brief, or any source material into a short LinkedIn carousel using a brand-specific PDF template. The output must look identical to the template, only the text changes.

---

## Templates (one per brand, never modified)

Templates live **inside the skill folder** so the skill is fully self-contained — they ship with the upload.

| Brand | Template path |
|-------|---------------|
| Baines Simmons | `~/.claude/skills/carousel-builder/Carousel - Baines Simmons - Template.pdf` |
| Redline | `~/.claude/skills/carousel-builder/Carousel - Redline - Template.pdf` |
| Kenyon | `~/.claude/skills/carousel-builder/Carousel - Kenyon - Template.pdf` |
| TrustFlight | `~/.claude/skills/carousel-builder/Carousel - TrustFlight - Template.pdf` |

All brand templates share the **same structure, layout, fonts, background graphics, and page geometry**. The only differences between brands are:
- The **header logo** (top-left)
- The **footer URLs** (e.g. `BAINESSIMMONS.COM • TRUSTFLIGHT.COM` vs. `REDLINEASSURED.COM • TRUSTFLIGHT.COM`, etc.)

This means the same coordinate map applies to every brand template.

**Output folder:** `/Users/alexcraiu/Desktop/Claude Playground/Carousel PDFs/Carousel - [Brand]/`  
**Output filename:** `Carousel - [Brand] - [Post Title].pdf`

---

## Brand Selection

Pick the template by matching the source material's owner:
- Article on `bainessimmons.com`, BSL course, or safety services topic → **Baines Simmons**
- Article on `redlineassured.com`, aviation security topic → **Redline**
- Article on `kenyoninternational.com`, emergency response topic → **Kenyon**
- Anything else, or generic TrustFlight product content (Centrik, TechLog, SmartSuite) → **TrustFlight**

If brand is ambiguous, ask the user.

---

## Page Anatomy

The Baines Simmons template (4 pages) sets the structure for every brand:

| Page | Role | Editable regions |
|------|------|-----------------|
| 1 | **Intro / Cover** | Subtitle pill, Post title (large), Description (paragraph under title) |
| 2 | **Content** | Subtitle pill, Body text (large, fills page) |
| 3 | **Content** | Subtitle pill, Body text (large, fills page) |
| 4 | **Outro / Closing** | Subtitle pill, Closing title (large), Final description (short), two **contact pills** (website + email) |

Static elements (never edit): brand header logo, top-right line graphic, side-decoration line patterns, navy gradient background, footer URL strip, next-arrow circle (pages 1–3 only — outro has no arrow).

**Outro contact pills** are part of the template and must stay an exact match for the brand:
- Baines Simmons → `bainessimmons.com` / `hello@bainessimmons.com`
- Redline → (per Redline template, e.g. `redlineassured.com` / `hello@redlineassured.com`)
- Kenyon → (per Kenyon template, e.g. `kenyoninternational.com` / `hello@kenyoninternational.com`)
- TrustFlight → (per TrustFlight template, e.g. `trustflight.com` / `hello@trustflight.com`)

Treat the outro contact pills as **template-fixed text**. Do not rewrite, shorten, or replace them — they ship inside the brand's template PDF as-is. Only the closing title, final description, and subtitle pill change on the outro.

---

## Subtitle Pill Sizing — Hug The Text

The rounded-rectangle subtitle pill (top-left of every page) must **hug the length of its text label** on each slide independently:

- Pill width = label text width + symmetric horizontal padding (match the padding used in the template's default pill, roughly the width of one tracked character on each side).
- Pill is **never shorter than the label** — the label must never visually touch or overflow the rounded ends.
- Pill height stays constant across all slides (matches the template).
- Pill corner radius stays constant (matches the template's rounded ends).
- Pill stroke colour, weight, and fill stay constant (matches the template).
- Pill anchor stays constant — left edge of the pill aligns with the left edge of the title/body text column on every slide.

Implementation: measure the rendered label width using the same font/size/letter-spacing as the template (Open Sans, bold, tracked uppercase), add 2× the padding, then draw the rounded rectangle at that width. Re-draw per page, since different slides will have different label widths.

---

## Content Rules

1. **Hard cap: 6 slides total**, intro and outro included. Never exceed.
2. **Heavily summarise.** Carousels are scan-friendly — strip everything to essentials. Each content page should communicate one idea.
3. **Subtitle pill** (`[VERY SHORT SUBTITLE LABEL]`): all caps, very short (max ~25 characters). Treat as a section/topic chip, not a sentence. Same label can repeat across pages or change per page — match the source material's flow. **The pill container must hug the label** — see "Subtitle Pill Sizing" above.
4. **Post title** (page 1): the carousel headline. Keep punchy, can wrap to 2 lines.
5. **Description** (page 1): short paragraph under the title — a teaser, can run a few lines.
6. **Body text** (content pages): heavy summary of one point per page. Stay within the visible text area defined by the template — do not push past the bottom edge of the column.
7. **Closing title + final description** (outro, last page): short closing line and a one-or-two-line wrap-up. Must not overlap or push into the contact pills below.
8. **Outro contact pills**: leave the template's two contact pills exactly as-is (website + email). They are brand-specific and baked into the template.
9. **Brand voice:** follow `skills/brand-framework/SKILL.md`. No em dashes (use comma, colon, or rewrite). "Visit our website" = `https://www.trustflight.com`. Open Sans only.

---

## Slide Count Logic

The Baines Simmons template ships with **4 pages**. The carousel cap is **6 pages**. Decide page count from the source material:

- If 3 distilled points fit cleanly: output 4 pages (1 intro + 2 content + 1 outro = use template as-is).
- If 4 distilled points: output 5 pages — duplicate one middle content page.
- If 5 distilled points: output 6 pages — duplicate two middle content pages.
- Never output fewer than 3 pages and never more than 6.

**Duplication rule** (when template is too short): duplicate one of the **inner content pages at random** (never the intro, never the outro). Insert the copy directly after the page it was cloned from, then fill it with the new content. This preserves the bookend pages while extending the middle.

---

## Generation Method

**Python + PyMuPDF** (mirrors `course-dates-generator`). Edits the brand template's PDF directly so all background graphics, fonts, and layout stay byte-identical to the template.

**Script:** `/Users/alexcraiu/.claude/skills/carousel-builder/fill_carousel_pdf.py` *(to be authored once all four brand templates exist — currently only Baines Simmons exists; coordinates need to be inspected with `page.get_text("dict")` and locked in once.)*

**Workflow once the script exists:**

```bash
python3 - << 'PYEOF'
import sys
sys.path.insert(0, "/Users/alexcraiu/.claude/skills/carousel-builder")
from fill_carousel_pdf import build_carousel

build_carousel(
    brand="Baines Simmons",          # "Baines Simmons" | "Redline" | "Kenyon" | "TrustFlight"
    cover={
        "subtitle": "JUST CULTURE",
        "title": "Building a Just Culture in Aviation Safety",
        "description": "Why blame-free reporting protects crews, exposes hazards, and saves lives.",
    },
    content=[
        # 2 to 4 content slides between cover and outro. Total slides incl. cover + outro must be <= 6.
        {"subtitle": "WHAT IT IS", "body": "Just culture treats honest mistakes as learning opportunities, not punishable offences."},
        {"subtitle": "WHY IT MATTERS", "body": "Crews who fear blame stop reporting. Without reports, hazards stay hidden."},
    ],
    outro={
        "subtitle": "GET IN TOUCH",
        "title": "Start your safety culture review",
        "description": "Talk to our team about a tailored review for your operation.",
        # Contact pills (website + email) are template-fixed per brand — never set here.
    },
)
PYEOF
```

**Coordinate inspection (one-off, when each new brand template lands):**

```bash
python3 - << 'PYEOF'
import fitz, os
doc = fitz.open(os.path.expanduser("~/.claude/skills/carousel-builder/Carousel - Baines Simmons - Template.pdf"))
for i, page in enumerate(doc):
    print(f"--- page {i+1} ---")
    print(page.get_text("dict"))
PYEOF
```

Use that dump to lock in per-page constants, then bake them into `fill_carousel_pdf.py`. Because every brand template shares geometry, one coordinate map covers all four brands. Required constants:

- `SUBTITLE_ANCHOR` — left edge x + baseline y for the subtitle pill (shared across pages 1–4).
- `SUBTITLE_PAD_X`, `SUBTITLE_HEIGHT`, `SUBTITLE_RADIUS`, `SUBTITLE_STROKE` — pill geometry for the hug-the-text logic.
- `TITLE_RECT` (page 1) and `DESCRIPTION_RECT` (page 1) — cover layout.
- `BODY_RECT` — content pages 2 and 3.
- `CLOSING_TITLE_RECT`, `CLOSING_DESCRIPTION_RECT` — outro page only.
- **Do NOT** define rects for the outro contact pills; they stay as the template renders them.

---

## Step-by-Step

1. **Identify the source material** the user provided (article URL, brief, raw text). Fetch with `WebFetch` if it's a URL.
2. **Pick the brand** template based on the source.
3. **Distil to bullet points** — one core idea per content slide, max 4 content slides between intro and outro.
4. **Draft the slide map**: post title, description, subtitle pills, body text per page.
5. **Confirm with the user** before generating, especially if the source is ambiguous or you had to make heavy editorial calls.
6. **Run `build_carousel(...)`** — generates the PDF into `Carousel PDFs/Carousel - [Brand]/`.
7. **Report back**: brand used, page count, output path. Then `open` the folder.

---

## Important Notes

- **Never modify the templates.** `fitz.open(template)` reads; `doc.save(output_path)` writes a new file.
- **Identical look.** The output PDF must be visually indistinguishable from the template except for the swapped text. Do not add new graphics, recolour anything, or move elements.
- **Open Sans only.** Embed Open Sans via `OpenSans-VariableFont_wdth,wght.ttf` for any inserted text. Match the weight visible in the template (header is semi-bold; subtitle pill is bold uppercase; title and body are regular).
- **Cover-then-write.** For each editable region, draw a rectangle filled with the local background colour (or use a transparent overlay technique) to wipe the placeholder, then insert the new text on top. Sample the navy at the text location — the template has a gradient, so a flat fill may leave a visible seam on light areas of pages 1 and 4.
- **Currently only the Baines Simmons template exists.** Until Redline, Kenyon, and TrustFlight templates are added, refuse to generate for those brands and tell the user the template is pending.
