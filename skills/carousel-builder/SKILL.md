---
name: carousel-builder
description: Build LinkedIn carousel PDFs (multi-page social posts) by summarising an article or brief into 6 slides or fewer using a brand-specific PDF template. Use whenever the user asks for a "carousel", "LinkedIn carousel", "multi-page LinkedIn post", or similar.
---

# Carousel Builder

Heavily summarise an article, brief, or any source material into a short LinkedIn carousel using a brand-specific PDF template. The output must look identical to the template, only the text changes.

---

## Templates (one per brand, never modified)

Templates live **inside the skill folder** so the skill is fully self-contained — they ship with the upload.

### Carousel templates (one PDF per brand)

| Brand | Template path |
|-------|---------------|
| Baines Simmons | `~/.claude/skills/carousel-builder/Carousel - Baines Simmons - Template.pdf` |
| Redline | `~/.claude/skills/carousel-builder/Carousel - Redline - Template.pdf` |
| Kenyon | `~/.claude/skills/carousel-builder/Carousel - Kenyon - Template.pdf` |
| TrustFlight | `~/.claude/skills/carousel-builder/Carousel - TrustFlight - Template.pdf` |

### Blog image template (single multi-page PDF, one page per brand)

`~/.claude/skills/carousel-builder/Blog Image - Template.pdf` — pick the relevant page by brand:

| Brand | Page (1-indexed) | Page index (0-indexed) |
|-------|-----------------|------------------------|
| Baines Simmons | 1 | 0 |
| Redline | 2 | 1 |
| Kenyon | 3 | 2 |
| TrustFlight | 4 | 3 |

When generating a blog image, **extract only the relevant brand's page** from this PDF, render it, and export as **JPG**. Never include the other pages in the output.

All brand templates share the **same structure, layout, fonts, background graphics, and page geometry**. The only differences between brands are:
- The **header logo** (top-left)
- The **footer URLs** (e.g. `BAINESSIMMONS.COM • TRUSTFLIGHT.COM` vs. `REDLINEASSURED.COM • TRUSTFLIGHT.COM`, etc.)

This means the same coordinate map applies to every brand template.

**Output folder:** `/Users/alexcraiu/Desktop/Claude Playground/Carousel PDFs/Carousel - [Brand]/`  
**Output filename (carousel):** `Carousel - [Brand] - [Post Title].pdf`  
**Output filename (blog image):** `Blog Image - [Brand] - [Post Title].jpg` (saved in the same folder as the carousel it accompanies)

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

The carousel template (4 pages) sets the structure for every brand:

| Page | Role | Editable regions |
|------|------|-----------------|
| 1 | **Intro / Cover** | Subtitle pill, Post title (large), Description (paragraph under title) |
| 2 | **Content** | Subtitle pill, Page title (large), Description (short paragraph) |
| 3 | **Content** | Subtitle pill, Page title (large), Description (short paragraph) |
| 4 | **Outro / Closing** | Subtitle pill, Closing title (large), Final description (short), two **contact pills** (website + email) |

Every page shares the same anatomy: subtitle pill at the top-left, a large title underneath, and a description paragraph under that. Content pages 2 and 3 use a **page title + description**, not a single body paragraph — the new structure replaces the old body-block design.

Static elements (never edit): brand header logo, top-right line graphic, side-decoration line patterns, navy gradient background, footer URL strip, next-arrow circle (pages 1–3 only — outro has no arrow).

**Outro contact pills** are part of the template and must stay an exact match for the brand:
- Baines Simmons → `bainessimmons.com` / `hello@bainessimmons.com`
- Redline → (per Redline template, e.g. `redlineassured.com` / `hello@redlineassured.com`)
- Kenyon → (per Kenyon template, e.g. `kenyoninternational.com` / `hello@kenyoninternational.com`)
- TrustFlight → `trustflight.com` / `sales@trustflight.com`

Treat the outro contact pills as **template-fixed text**. Do not rewrite, shorten, or replace them — they ship inside the brand's template PDF as-is. Only the closing title, final description, and subtitle pill change on the outro.

---

## Blog Image Companion

A matching blog post image is **always generated alongside the carousel** — no y/n prompt, no opt-in. Every carousel run produces both a carousel PDF and a blog image JPG.

1. **Pick the brand's page** from `Blog Image - Template.pdf` using the page index table above. Do not touch other pages.
2. **Reuse the carousel cover's subtitle pill and post title verbatim** — same label, same title that already went onto the carousel's intro slide. The blog image and carousel cover share that copy block by design.
3. **Description must be no longer than 2 lines of text** on the rendered blog image. Three lines is too long, the visual gets cramped. If the carousel cover description is longer than 2 lines, write a **shorter, tighter version** specifically for the blog image — keep the same idea, drop or compress wording until it fits in 2 lines at the template's font size and column width. Don't truncate mid-sentence; rewrite.
4. **Apply the same subtitle pill hug-the-text rule** as the carousel (see "Subtitle Pill Sizing" below). Pill width = label width + symmetric padding, never shorter than the label.
5. **Cover-then-write** the placeholder text on the page, exactly like the carousel pipeline.
6. **Export as JPG** (not PDF). Render at high resolution suitable for LinkedIn / blog hero use — minimum 1500 px wide. Use PyMuPDF: `page.get_pixmap(matrix=fitz.Matrix(scale, scale))` with `scale` chosen so output width ≥ 1500 px, then `pix.save("...jpg", jpg_quality=92)`.
7. **Save** alongside the carousel in `Carousel PDFs/Carousel - [Brand]/Blog Image - [Brand] - [Post Title].jpg`.
8. **Confirm** in the reply: blog image path, dimensions, and whether the description was rewritten to fit the 2-line cap.

The blog image layout intentionally mirrors the carousel's intro slide (subtitle pill, post title, short description, same header logo, same line graphics), so when a user posts both, they read as a matched pair.

---

## Subtitle Pill Sizing — Hug The Text

The rounded-rectangle subtitle pill (top-left of every carousel slide **and** the blog image) must **hug the length of its text label** on each slide independently:

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
6. **Content slides** (pages 2 and 3): each carries a **page title** (large) and a **description** (short paragraph under the title). Page title = one punchy line, max 2 lines. Description = short paragraph, max 3 to 4 lines. Stay within the visible text area, do not push past the bottom edge of the column.
7. **Closing title + final description** (outro, last page): short closing line and a one-or-two-line wrap-up. Must not overlap or push into the contact pills below.
8. **Outro contact pills**: leave the template's two contact pills exactly as-is (website + email). They are brand-specific and baked into the template.
9. **Brand voice:** follow `skills/brand-framework/SKILL.md`. No em dashes (use comma, colon, or rewrite). "Visit our website" = `https://www.trustflight.com`. Open Sans only.
10. **Suggested LinkedIn caption:** after generating the PDF, propose a social media caption to go with the carousel post.
    - Length: medium — long enough to hook and summarise (roughly 3 to 6 short sentences or ~80 to 150 words), short enough to scan. Never a wall of text, never a one-liner.
    - Tone: professional, confident, informative. Not overly friendly, no hype, no "Hey everyone!" openers.
    - Emojis: use a few, sparingly and on-brand (e.g. ✈️ 🛡️ 📊 🔍). One in the opener and one or two more in the body is plenty. Avoid emoji-as-bullet runs.
    - Hashtags: suggest around five, all relevant to the topic and the brand (e.g. `#AviationSafety #JustCulture #SMS #SafetyCulture #BainesSimmons`). Place them on their own line at the end.
    - Output the caption block in the final reply, clearly labelled, so the user can copy it straight into LinkedIn.

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
        # Each content slide has a page title + short description (not a single body block).
        {
            "subtitle": "WHAT IT IS",
            "title": "Honest mistakes are learning opportunities",
            "description": "Just culture separates error from violation, so crews report freely.",
        },
        {
            "subtitle": "WHY IT MATTERS",
            "title": "Fear of blame hides hazards",
            "description": "Without reports, the operation loses its early warning system.",
        },
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
- `TITLE_RECT`, `DESCRIPTION_RECT` — shared across pages 1, 2, 3 (cover and content slides all use the same title + description layout).
- `CLOSING_TITLE_RECT`, `CLOSING_DESCRIPTION_RECT` — outro page only.
- **Do NOT** define rects for the outro contact pills; they stay as the template renders them.

---

## Execution Style — Be Fast, Stay Quiet

- **Minimal narration.** Do not describe what you are about to do, what you just did, or what you are thinking. The user does not want a play-by-play. State only: (a) one short line acknowledging the request, (b) the final report at the end. Nothing in between unless blocked.
- **No "Now I will..." / "Let me..." / "I'll start by..." sentences.** Cut them.
- **Batch everything.** Fetch the source, distil the slide map, render the carousel, and render the blog image in as few tool calls as possible. Use a single Python heredoc that opens PyMuPDF once, processes both the carousel and the blog image, and saves both — do not run a separate script per file.
- **Parallelise where independent.** WebFetch + reading any reference files at the start can go in one batched tool call.
- **No mid-task confirmations.** Only ask the user a question if (a) the brand is genuinely ambiguous, or (b) the editorial calls were so heavy you need a sanity check. Otherwise generate and report.
- **End-of-task report = 3 lines max.** Carousel path, blog image path, then the LinkedIn caption block. Skip "I have generated…" preambles.

---

## Step-by-Step

1. **Identify the source material** the user provided (article URL, brief, raw text). Fetch with `WebFetch` if it's a URL.
2. **Pick the brand** template based on the source.
3. **Distil to bullet points** — one core idea per content slide, max 4 content slides between intro and outro.
4. **Draft the slide map**: post title, description, subtitle pills, body text per page.
5. **Confirm with the user** before generating, especially if the source is ambiguous or you had to make heavy editorial calls.
6. **Run `build_carousel(...)`** — generates the PDF into `Carousel PDFs/Carousel - [Brand]/`.
7. **Always generate the blog image companion** — see "Blog Image Companion" above. Pick the brand's page from `Blog Image - Template.pdf`, reuse the carousel cover's subtitle pill + title, write a 2-line description, export as JPG into the same folder as the carousel. Never skip this step and never ask the user to opt in.
8. **Report back**: brand used, carousel page count, carousel PDF path, blog image JPG path. Then `open` the folder.
9. **Suggest a LinkedIn caption** (see Content Rule 10) — include the caption text and ~5 hashtags in the reply.

---

## Important Notes

- **Never modify the templates.** `fitz.open(template)` reads; `doc.save(output_path)` writes a new file.
- **Identical look.** The output PDF must be visually indistinguishable from the template except for the swapped text. Do not add new graphics, recolour anything, or move elements.
- **Open Sans only.** Embed Open Sans via `OpenSans-VariableFont_wdth,wght.ttf` for any inserted text. Match the weight visible in the template (header is semi-bold; subtitle pill is bold uppercase; title and body are regular).
- **Cover-then-write.** For each editable region, draw a rectangle filled with the local background colour (or use a transparent overlay technique) to wipe the placeholder, then insert the new text on top. Sample the navy at the text location — the template has a gradient, so a flat fill may leave a visible seam on light areas of pages 1 and 4.
- **Currently only the Baines Simmons template exists.** Until Redline, Kenyon, and TrustFlight templates are added, refuse to generate for those brands and tell the user the template is pending.
