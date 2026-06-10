---
name: carousel-builder
description: Build LinkedIn carousel PDFs (multi-page social posts) by summarising an article or brief into 6 slides or fewer using a brand-specific PDF template. Use whenever the user asks for a "carousel", "LinkedIn carousel", "multi-page LinkedIn post", or similar.
---

# Carousel Builder

Heavily summarise an article, brief, or any source material into a short LinkedIn carousel using a brand-specific PDF template. The output must look identical to the template, only the text changes.

---

## How To Run This Skill (read this first)

**Do not search the filesystem for templates, fonts, or the fill script.** They are all bundled inside this skill folder at `~/.claude/skills/carousel-builder/`. The `build()` function knows where to find them — just import and call it.

**Never** run `find`, `Glob`, or directory listings looking for `Carousel - *.pdf`, `Blog Image - *.pdf`, `OpenSans-*.ttf`, or `fill_carousel_pdf.py`. They are right next to `SKILL.md`. Searching wastes seconds per run and there is nothing to find that isn't already here.

**The canonical workflow is a single Python call:**

```bash
python3 - << 'PYEOF'
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/carousel-builder"))
from fill_carousel_pdf import build

result = build(
    brand="Baines Simmons",          # "Baines Simmons" | "Redline" | "Kenyon" | "TrustFlight"
    cover={
        "subtitle": "Just Culture",
        "title": "Building a Just Culture in Aviation Safety",
        "description": "Why blame-free reporting protects crews, exposes hazards, and saves lives.",
    },
    content=[
        # 1 to 4 content slides. Total slides (cover + content + outro) must be <= 6.
        {"subtitle": "What it is",
         "title": "Honest mistakes are learning opportunities",
         "description": "Just culture separates error from violation, so crews report freely."},
        {"subtitle": "Why it matters",
         "title": "Fear of blame hides hazards",
         "description": "Without reports, the operation loses its early warning system."},
    ],
    outro={
        "subtitle": "Get in touch",
        "title": "Start your safety culture review",
        "description": "Talk to our team about a tailored review for your operation.",
    },
    blog_description="Why blame-free reporting protects crews and saves lives.",  # 2 lines max
    output_dir=os.path.expanduser("~/Desktop/Claude Playground/Carousel PDFs"),
)
print(result)
PYEOF
```

This single call produces **both** the carousel PDF and the matching blog image JPG, hugged subtitle pills, fitted titles, and an open output folder path. After that, write the LinkedIn caption directly into the reply (see Content Rule 10).

`build()` handles, with no further instruction needed:
- Picking the right brand template.
- Cloning or dropping content pages so the deck matches `len(content)`.
- Hug-the-text subtitle pill on every page (carousel and blog).
- Auto-shrinking the title font when copy is long.
- Leaving the brand-specific outro contact pills intact.
- Rendering the blog JPG from the correct brand page of the bundled multi-brand template.
- Sanitising the post title for the filename.

---

## Templates (one per brand, never modified)

All four brand templates and the multi-brand blog template ship inside this skill folder. The script reads them via `Path(__file__).parent` — no path configuration required.

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
- Article on `trustredline.co.uk`, aviation security topic → **Redline**
- Article on `kenyoninternational.com`, emergency response / crisis topic → **Kenyon**
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
- Redline → `trustredline.co.uk` / `sales@trustredline.co.uk`
- Kenyon → `kenyoninternational.com` / `kenyon@kenyoninternational.com`
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
4. **Post title** (page 1): the carousel headline. **Keep it short — aim for 5 to 8 words, hard cap at 10.** One punchy line is the goal, two if absolutely necessary. Cut adjectives, hedges, and explanatory clauses. "Where annual audits trip up real Manex 19 implementation" is too wordy; "Why annual audits miss the gap" is better.
5. **Description** (page 1): short paragraph under the title — a teaser, can run a few lines.
6. **Content slides** (pages 2 and 3): each carries a **page title** (large) and a **description** (short paragraph under the title). **Page title = 4 to 8 words, hard cap at 10.** One punchy line, never more than two. Description = short paragraph, max 3 to 4 lines. Stay within the visible text area, do not push past the bottom edge of the column.
7. **Closing title + final description** (outro, last page): closing title = 4 to 8 words. Final description = one or two lines. Must not overlap or push into the contact pills below.
8. **Outro contact pills**: leave the template's two contact pills exactly as-is (website + email). They are brand-specific and baked into the template.
9. **No duplicate slides.** Every content slide must carry a distinct idea — distinct subtitle pill, distinct title, distinct description. Near-duplicates (two slides saying the same thing in different words) are forbidden. If you only have N genuinely distinct points, output N + 2 slides (cover + N content + outro). Better to ship a 3-slide carousel than to pad with repeats. If `content` would end up with fewer than 1 distinct slide, ask the user for more source material before generating.
10. **Brand voice:** follow `skills/brand-framework/SKILL.md`. No em dashes (use comma, colon, or rewrite). "Visit our website" = `https://www.trustflight.com`. Open Sans only.
11. **Suggested LinkedIn caption:** after generating the PDF, propose a social media caption to go with the carousel post.
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

**Python + PyMuPDF (`fitz`).** The bundled `fill_carousel_pdf.py` does all the work. Coordinates, fonts, pill geometry, and brand-specific outro pills are already baked into the script — no inspection or coordinate hunting on every run.

Under the hood, for each filled page the script:
1. Redacts the original pill drawing (vector + tracked text) with transparent fill — the gradient flows through cleanly, no seam.
2. Redacts the title + description placeholder text spans.
3. Draws a new pill whose width = label text width + symmetric padding (the hug-the-text rule).
4. Inserts the new title with auto-shrink, and the new description with auto-shrink.
5. Leaves the brand-specific outro contact pills (`bainessimmons.com` / `hello@…` etc.) untouched.

If something looks wrong (e.g. coordinates shift after a new template upload), inspect with:

```bash
python3 -c "import fitz, os; d=fitz.open(os.path.expanduser('~/.claude/skills/carousel-builder/Carousel - Baines Simmons - Template.pdf')); [print(i, p.get_text('dict')) for i, p in enumerate(d)]"
```

and update the constants at the top of `fill_carousel_pdf.py`. Do **not** rewrite the fill logic from scratch — just adjust the rect / colour constants.

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

1. Fetch the source (WebFetch on a URL, or use the brief the user pasted).
2. Pick the brand from the source.
3. Distil the slide map in your head (cover + 1–4 content + outro, ≤ 6 total). For each slide: subtitle label, page title, short description.
4. Write a tight 2-line `blog_description` derived from the cover description.
5. Run **one** `build(...)` call (see "How To Run This Skill" at the top). It produces the carousel PDF and the blog image JPG together.
6. Reply in 3 short lines: carousel PDF path, blog image JPG path, then the LinkedIn caption + ~5 hashtags. Nothing else.

---

## Important Notes

- **Never modify the templates.** `fill_carousel_pdf.py` opens them read-only and saves new files into the user's output folder.
- **Don't improvise on geometry.** All rects, font sizes, pill dimensions, and brand colours are baked into the script. Use `build()` — do not write per-call drawing logic in a heredoc.
- **Open Sans is bundled** (Light / Regular / Bold / SemiBold `.ttf` files sit alongside `SKILL.md`). The script references them via `Path(__file__).parent`. No system font lookup, no font search, no re-upload.
- **All four brand templates are live** (Baines Simmons, Redline, Kenyon, TrustFlight) and bundled with the skill.
