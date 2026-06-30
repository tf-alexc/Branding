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

**Dependencies:** `PyMuPDF` (a.k.a. `fitz`) and `segno` (QR codes for the v2 BSL outro). If a run fails with `ModuleNotFoundError: No module named 'segno'`, install it once with `pip install segno`. PyMuPDF is already in use for the existing course-dates skill.

**Two flavours, dispatched by brand:**

- **Baines Simmons** runs the new **v2** template with four specialised content layouts (`paragraph`, `bullets`, `checklist`, `quote`). Each content slide carries a `type` field that picks the layout. The outro has no contact pills — a template-fixed CTA pill ("READ THE FULL ARTICLE") sits at the bottom instead. The cover has a "CONTINUE READING" CTA pill that also stays template-fixed.
- **Redline, Kenyon, TrustFlight** run the legacy **v1** template — every content slide is `title + description`, and the outro keeps its two brand-specific contact pills.

`build()` picks the right pipeline from the `brand` argument. You never call v1/v2 directly.

### v2 Baines Simmons example

```bash
python3 - << 'PYEOF'
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/carousel-builder"))
from fill_carousel_pdf import build

result = build(
    brand="Baines Simmons",
    cover={
        "subtitle": "Just Culture",
        "title": "Building a Just Culture",
        "description": "Why blame-free reporting protects crews, exposes hazards, and saves lives.",
    },
    content=[
        # Mix and match any combination of paragraph / bullets / checklist / quote.
        # Total slides (cover + content + outro) must be <= 6, so up to 4 content slides.
        {"type": "paragraph",
         "subtitle": "What it is",
         "title": "Honest mistakes are learning",
         "body": "Just culture separates error from violation. Crews report freely. The operation learns from near misses instead of hiding them."},
        {"type": "bullets",
         "subtitle": "Three signals",
         "title": "Three early warnings",
         "items": ["Reporting rate dropping",
                   "Same hazards recurring",
                   "Findings closed without fix",
                   "Audit fatigue"]},                       # 1 to 4 items
        {"type": "checklist",
         "subtitle": "Where to start",
         "title": "Your first 90 days",
         "items": ["Run a culture survey",
                   "Map decision lines",
                   "Brief crews on the policy"]},
        {"type": "quote",
         "subtitle": "On reporting",
         "title": "A safer way to learn",
         "quote": "The crew who hides the mistake denies us the lesson.",
         "attribution": "Capt. M. Walsh, Safety Director"},  # attribution is optional
    ],
    outro={
        "subtitle": "Get in touch",
        "title": "Start your safety culture review",
        "description": "Talk to our team about a tailored review for your operation.",
    },
    blog_description="Why blame-free reporting protects crews and saves lives.",  # 2 lines max
    source_url="https://www.bainessimmons.com/insights/just-culture-aviation",   # drives the outro QR code
    output_dir=os.path.expanduser("~/Desktop/Claude Playground/Carousel PDFs"),
)
print(result)
PYEOF
```

### v1 Redline / Kenyon / TrustFlight example

```python
result = build(
    brand="TrustFlight",  # or "Redline" / "Kenyon"
    cover={"subtitle": "...", "title": "...", "description": "..."},
    content=[
        # Every content slide is plain title + description on v1 brands.
        {"subtitle": "...", "title": "...", "description": "..."},
        {"subtitle": "...", "title": "...", "description": "..."},
    ],
    outro={"subtitle": "...", "title": "...", "description": "..."},
    blog_description="2-line tighter version for the blog image.",
    output_dir="...",
)
```

### Slide-type picker (BSL only)

When generating a BSL carousel, **Claude picks the `type` for each content slide.**

**Default to bullets and checklists — actively prefer them, even when the source document is all prose.** Most ideas can be reshaped into a tight list, and lists are far more scannable than paragraphs on a LinkedIn carousel. Do not wait for the source to "have a list"; create one. A multi-sentence point about "the three drivers of X" becomes a 3-item `bullets` slide; "what to do next" becomes a `checklist`. Aim for **at least one bullets or checklist slide in every carousel**, and prefer them over paragraph slides whenever the content can be itemised at all.

- **bullets** — 2 to 4 short parallel items that share a structure ("three signs of...", "key drivers", "what changes"). **Preferred default.**
- **checklist** — 2 to 4 short action items the reader could tick off ("steps to take", "do today", "before the audit"). **Preferred for anything actionable.**
- **paragraph** — use sparingly, only when a point genuinely cannot be itemised without losing meaning. Never more than one paragraph slide per carousel if you can help it.
- **quote** — a memorable one-liner with attribution. Use sparingly; one quote slide per carousel is the ceiling.

Show the user the draft slide map (subtitle / title / type / body or items) before generation and let them override.

`build()` handles, with no further instruction needed:
- Picking the right brand template (v1 vs v2).
- Picking and ordering the right template content pages for v2 BSL based on slide types.
- Cloning or dropping content pages so the deck matches `len(content)` on v1 brands.
- Hug-the-text subtitle pill on every page (carousel and blog).
- Auto-shrinking title / body / item fonts when copy is long.
- Leaving the brand-specific outro contact pills (v1) or CTA pills (v2 BSL) intact.
- Rendering the blog JPG from the correct brand page of the bundled multi-brand template.
- Sanitising the post title for the filename.
- Raising a `ValueError` if two content slides share a title (no-duplicate guard).

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

### v2 Baines Simmons (6 source pages, 4 specialised content layouts)

| Source page | Role | Editable fields | Static elements (do not touch) |
|------|------|-----------------|-------------------------------|
| 0 | **Cover** | subtitle, title (120pt), description (80pt) | Header logo, "CONTINUE READING ›" CTA pill, footer URLs |
| 1 | **Content — paragraph** | subtitle, title (90pt), body (72pt, multi-paragraph) | Header, next-arrow image, footer |
| 2 | **Content — bullets** | subtitle, title (120pt), 1–4 items in rounded pills with cyan dots | Header, next-arrow, footer |
| 3 | **Content — checklist** | subtitle, title (120pt), 1–4 items in rounded pills with green checks | Header, next-arrow, footer |
| 4 | **Content — quote** | subtitle, title (100pt), quote (78pt indented), attribution (optional) | Header, quote-mark glyph, next-arrow, footer |
| 5 | **Outro** | subtitle, closing title (120pt), final description (80pt) | Header, "READ THE FULL ARTICLE" CTA pill, footer |

The new BSL outro has **no contact pills**. The CTA pill ("READ THE FULL ARTICLE") replaces them and stays template-fixed.

### v1 Redline / Kenyon / TrustFlight (4 source pages)

| Source page | Role | Editable fields |
|------|------|-----------------|
| 0 | **Cover** | subtitle, title (120pt), description (80pt) |
| 1 | **Content** | subtitle, title (120pt), description (80pt) |
| 2 | **Content** | subtitle, title (120pt), description (80pt) |
| 3 | **Outro** | subtitle, closing title, final description, two **contact pills** |

**Outro contact pills (v1 brands only)** stay template-fixed:
- Redline → `trustredline.co.uk` / `sales@trustredline.co.uk`
- Kenyon → `kenyoninternational.com` / `kenyon@kenyoninternational.com`
- TrustFlight → `trustflight.com` / `sales@trustflight.com`

Treat the outro contact pills (v1) and the cover/outro CTA pills (v2 BSL) as **template-fixed text**. Do not rewrite, shorten, or replace them. They are baked into the template PDF and the script preserves them automatically.

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

1. **Hard cap: 6 slides total**, cover and outro included. Never exceed.
2. **Heavily summarise.** Carousels are scan-friendly — strip everything to essentials. Each content page should communicate one idea.
3. **Subtitle pill** (`[VERY SHORT SUBTITLE LABEL]`): all caps, very short (max ~25 characters). Treat as a section/topic chip, not a sentence. **The pill container must hug the label** — see "Subtitle Pill Sizing" below.
4. **Post title** (cover, page 1): the carousel headline. **5 to 8 words, hard cap at 10.** One punchy line is the goal, two if absolutely necessary. Cut adjectives, hedges, and explanatory clauses. *"Where annual audits trip up real Manex 19 implementation"* (10 words, wordy) → *"Why annual audits miss the gap"* (6 words, punchy).
5. **Description** (cover): short paragraph under the title. v1 brands allow a few lines; on v2 BSL it sits between title and CTA pill so keep it 2 to 3 lines max.
6. **Content slide titles** (all slide types): **4 to 8 words, hard cap at 10.** One punchy line, never more than two.
7. **Content slide bodies** depend on the slide type. **Be ruthlessly concise — short, scannable lines, clear meaning, nothing padded.** A carousel slide is glanced at, not read. Prefer the fewest words that still land the point. **Never fill a slide with a wall of text.** When a point starts to feel long, that is the signal to turn it into a bullets or checklist slide instead (see Rule 10), or split it across two slides.
   - **No big paragraph blocks.** Any multi-sentence text (cover/outro descriptions and paragraph bodies) is automatically reflowed by the script: one sentence per line, with a blank line after every two sentences. So no block of text ever runs longer than two sentences before a break. You don't need to insert the line breaks yourself — just write clean sentences and keep the total short.
   - **paragraph** (v2 BSL only): `body` = **2 to 3 short sentences, max.** This layout is the fallback, not the default — reach for bullets/checklist first. If a point needs more than 3 sentences, it is really a list: itemise it. Never use a paragraph slide as a dumping ground.
   - **bullets** (v2 BSL only): `items` = list of 1 to 4 strings. **Each item MUST fit on one row inside its container — never two rows.** That means roughly 3 to 7 words per item, depending on word length. Available row width is ~953pt at 51pt; the script auto-shrinks down to 32pt and will raise `ValueError` if an item still overflows. If that fires, shorten the item. Parallel structure: all start with verbs, or all noun phrases — not a mix.
   - **checklist** (v2 BSL only): `items` = list of 1 to 4 actionable items. Same one-row-per-item rule as bullets. Each starts with a verb ("Run a culture survey", "Map decision lines").
   - **quote** (v2 BSL only): `quote` = a short memorable line, ~10 to 25 words. `attribution` (optional) = name, role, optionally org.
   - **v1 brands**: every content slide is `description` = short paragraph, max 3 to 4 lines.
8. **Closing title + final description** (outro): closing title = 4 to 8 words. Description = one or two lines on v2 BSL (keep clear of the CTA pill below), or up to a few lines on v1 brands.
9. **No duplicate slides.** Every content slide must carry a distinct idea — distinct subtitle pill, distinct title, distinct body / items / quote. Near-duplicates (two slides saying the same thing in different words) are forbidden. If you only have N genuinely distinct points, output N + 2 slides (cover + N content + outro). Better to ship a 3-slide carousel than to pad with repeats. The script also raises `ValueError` if two content slides share an exact title.
10. **Slide-type picking** (v2 BSL): **prefer bullets and checklists, even when the source has no list.** Reshape prose into itemised slides — most points can be. Target at least one bullets or checklist slide per carousel. Use `checklist` for anything actionable ("steps", "do this"), `bullets` for parallel points ("three drivers", "key signs"). Reserve `paragraph` for the rare point that truly cannot be itemised, and `quote` for one memorable line (max one per carousel). When in doubt, itemise — do not default to paragraph.
11. **Never overlap the corner furniture.** Content pages have a next-arrow circle in the **bottom-right** and a footer URL band in the **bottom-left**. No inserted text (title, body, description, items, quote, attribution) may run into either. The script enforces this — every text rect is capped above the arrow circle, and the quote attribution is kept clear of the arrow column — but keep copy concise so text never needs that bottom band in the first place. If a body is long enough that the script has to shrink it hard to stay above the arrow, that is a signal to cut it or split it into a list slide.
12. **Outro CTA / contact pills**: leave template-fixed. Do not try to rewrite them — the script preserves them automatically.
13. **Outro QR code (v2 BSL only):** the red rectangle in the bottom-right of the BSL outro template is a **QR code placeholder linking to the source article**. Pass the article URL as `source_url` to `build()` and the script generates the QR code and overlays it on the placeholder. The QR is **always rendered in Electric (`#03D4FF`)**, the TrustFlight brand colour, on a transparent background so the navy gradient shows through. High error correction, so it stays scannable. If you omit `source_url`, the red placeholder is redacted away so the output never ships with a raw red square.
14. **Brand voice:** follow `skills/brand-framework/SKILL.md`. No em dashes (use comma, colon, or rewrite). "Visit our website" = `https://www.trustflight.com`. Open Sans only.
15. **Suggested LinkedIn caption:** after generating the PDF, propose a social media caption to go with the carousel post.
    - Length: medium — long enough to hook and summarise (roughly 3 to 6 short sentences or ~80 to 150 words), short enough to scan. Never a wall of text, never a one-liner.
    - Tone: professional, confident, informative. Not overly friendly, no hype, no "Hey everyone!" openers.
    - Emojis: use a few, sparingly and on-brand (e.g. ✈️ 🛡️ 📊 🔍). One in the opener and one or two more in the body is plenty. Avoid emoji-as-bullet runs.
    - Hashtags: suggest around five, all relevant to the topic and the brand (e.g. `#AviationSafety #JustCulture #SMS #SafetyCulture #BainesSimmons`). Place them on their own line at the end.
    - Output the caption block in the final reply, clearly labelled, so the user can copy it straight into LinkedIn.

---

## Slide Count Logic

Total slides (cover + content + outro) must be **≤ 6**. Floor is 3 (cover + 1 content + outro).

- **v2 Baines Simmons** has 6 source pages (cover + 4 specialised content layouts + outro). The script `select()`s the cover, the content pages you asked for in your `content` list (in order, repeats allowed — e.g. two `paragraph` slides are fine), and the outro. Unused content layouts are dropped automatically.
- **v1 brands** have 4 source pages. If you ask for 1 content slide, the script drops one of the template's two content pages. If you ask for 3–4, it clones a content page accordingly.

In both cases the script handles the page count. You only have to keep `len(content) + 2 ≤ 6`.

---

## Generation Method

**Python + PyMuPDF (`fitz`).** The bundled `fill_carousel_pdf.py` does all the work. Coordinates, fonts, pill geometry, brand-specific outro pills (v1) and CTA pills (v2) are already baked into the script — no inspection or coordinate hunting on every run.

Under the hood, for each filled page the script:
1. Redacts the original subtitle pill drawing (vector + tracked text) with transparent fill so the gradient flows through cleanly, no seam.
2. Redacts only the placeholder text spans matching the layout's expected font sizes (e.g. 120pt title + 80pt description on cover; 90pt title + 72pt body on a v2 BSL paragraph slide).
3. Draws a new subtitle pill whose width = label text width + symmetric padding (the hug-the-text rule).
4. Inserts each text field with auto-shrink — measured fit before drawing, so no oversized ghosts.
5. On v2 BSL list slides: redacts unused item containers via line-art removal, and covers the orphan icon image (which lives inside a form XObject the redaction cannot reach) with a flat fill that matches the gradient at that y-band.
6. Leaves the brand-specific outro contact pills (v1) and the cover/outro CTA pills (v2 BSL) untouched.

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
3. Distil the slide map (cover + 1–4 content + outro, ≤ 6 total). For each content slide:
   - **v2 BSL**: pick the slide `type` (paragraph / bullets / checklist / quote) that best fits the content shape, then write the matching fields.
   - **v1 brands**: write subtitle + title + description.
4. Write a tight 2-line `blog_description` derived from the cover description.
5. Run **one** `build(...)` call (see "How To Run This Skill" at the top). It produces the carousel PDF and the blog image JPG together.
6. Reply in 3 short lines: carousel PDF path, blog image JPG path, then the LinkedIn caption + ~5 hashtags. Nothing else.

---

## Important Notes

- **Never modify the templates.** `fill_carousel_pdf.py` opens them read-only and saves new files into the user's output folder.
- **Don't improvise on geometry.** All rects, font sizes, pill dimensions, and brand colours are baked into the script. Use `build()` — do not write per-call drawing logic in a heredoc.
- **Open Sans is bundled** (Light / Regular / Bold / SemiBold `.ttf` files sit alongside `SKILL.md`). The script references them via `Path(__file__).parent`. No system font lookup, no font search, no re-upload.
- **All four brand templates are live** (Baines Simmons, Redline, Kenyon, TrustFlight) and bundled with the skill.
