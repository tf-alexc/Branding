---
name: courses-generator
description: Generate a branded JPG promoting a single academy course for LinkedIn from the sub-brand PDF template. Use whenever the user asks to promote an academy course, create a training post, or generate a course promo graphic for Baines Simmons, Redline, or Kenyon.
---

# Courses Generator

Single-course LinkedIn promo graphic. The user supplies one course page URL, the skill detects the sub-brand from the domain, fills the matching template with the course title and dates, and exports a high-resolution JPG ready to post.

This skill is the JPG / LinkedIn counterpart of `course-dates-generator` (which produces PDFs from a listing page).

**Triggers:** promote academy course, training post, course promo, LinkedIn course graphic.

---

## Templates (one per sub-brand, never modified)

Templates ship inside the skill folder, alongside the script, so the skill
is fully self-contained — no separate upload step is ever required.

| Brand | Domain | Template (relative to skill folder) |
|-------|--------|--------------------------------------|
| Kenyon | `kenyoninternational.com` | `templates/Courses - Kenyon - Template.pdf` |
| Redline | `trustredline.co.uk` (or `redlineassuredsecurity.com`) | `templates/Courses - Redline - Template.pdf` |
| Baines Simmons | `bainessimmons.com` | `templates/Courses - Baines Simmons - Template.pdf` |

The script resolves `TEMPLATE_DIR` automatically from its own location, so
the same code path works on Alex's Mac and in cloud sessions without any
configuration. If a template ever needs updating, replace the PDF in
`templates/` and commit — no script changes required.

Each template has two pages:
- **Page 0** — two-column layout (Initial + Recurrent), used when both date types are present
- **Page 1** — single-column layout, used for everything else

Both pages include a fixed `BOOK NOW` button and website footer — those are visual only and are not edited.

**Generation method:** Python + PyMuPDF. The script fills the template in memory, then rasterises the page to a 2400×2800 JPG (2× zoom from the 1200×1400 template).

**Script:** `fill_course_jpg.py` (bundled at the root of this skill folder).
**Fonts:** `fonts/OpenSans-Regular.ttf` (also bundled — skill is fully self-contained).
**Output folder:** the script auto-selects the first available location:
1. `/mnt/user-data/outputs/Course JPGs - [Brand]/` (claude.ai Skills sandbox)
2. `/Users/alexcraiu/Desktop/Claude Playground/Course PDFs/Course JPGs - [Brand]/` (Alex's Mac)
3. `<repo>/Course PDFs/Course JPGs - [Brand]/` (cloud session checkout)
4. Current working directory (last-resort fallback).

**Output filename:** `Course - [Brand] - [Course Title].jpg`

---

## Column Layout Rules

Same as `course-dates-generator`:

| Date types on page | left_label | column_type | Right column |
|--------------------|-----------|-------------|--------------|
| Both initial and recurrent | `Initial Course Dates` | `both` | Visible |
| Initial only | `Initial Course Dates` | `initial` | Hidden |
| Recurrent only | `Recurrent Course Dates` | `recurrent` | Hidden |
| Generic / no type distinction | `Upcoming Dates` | `generic` | Hidden |

---

## Step 1: Detect Brand from URL

The user provides one course page URL. Match the domain:

- `kenyoninternational.com` → **Kenyon**
- `trustredline.co.uk` or `redlineassuredsecurity.com` → **Redline**
- `bainessimmons.com` → **Baines Simmons**

The script does this automatically via `brand_from_url(url)`. If the domain doesn't match, ask the user which brand to use rather than guessing.

---

## Step 2: Fetch the Course Page

Use the available web-fetch tool on the URL (the tool name varies by host — `WebFetch` in Claude Code, `web_fetch` / `web_search` in claude.ai chat). Extract:

- **Course name** — the page's course title (verbatim, no truncation)
- **Date type** — `initial`, `recurrent`, `both`, or `generic`
- **Left dates** — initial (or generic) dates
- **Right dates** — recurrent dates (only when `column_type="both"`)

Course titles with ` - ` separator: the prefix renders on a coloured first line, the rest as the subtitle (handled automatically by `_split_title`).

If the page has no dates listed, ask the user to provide them or pick `column_type="generic"` with a single placeholder.

---

## Step 3: Generate the JPG

Import `fill_course_jpg` from this skill folder and call `fill_course_from_url`. Add the skill folder to `sys.path` first — the exact directory depends on the host (it's the folder containing this `SKILL.md`).

```python
import sys, os
# Skill folder = directory containing this SKILL.md.
# In claude.ai: typically /mnt/skills/user/courses-generator
# In Claude Code on Mac: /Users/alexcraiu/.claude/skills/courses-generator
sys.path.insert(0, os.path.dirname(os.path.abspath("SKILL.md location")))
from fill_course_jpg import fill_course_from_url

fill_course_from_url(
    url="https://www.bainessimmons.com/training-courses/risk-management-workshop",
    course_name="Risk Management Workshop (RMW)",
    left_label="Upcoming Dates",
    left_dates=["13 - 17 April", "07 - 11 September"],
    right_dates=[],
    column_type="generic",
)
```

For an initial + recurrent split:

```python
fill_course_from_url(
    url="https://www.trustredline.co.uk/courses/aviation-security-foundation",
    course_name="Aviation Security Foundation",
    left_label="Initial Course Dates",
    left_dates=["12 - 13 March", "10 - 11 September"],
    right_dates=["04 May", "02 November"],
    column_type="both",
)
```

If you already know the brand and want to skip URL detection, call `fill_course(brand=..., ...)` directly.

**If PyMuPDF (`fitz`) isn't installed in the sandbox**, install it first: `pip install pymupdf`.

---

## Step 4: Confirm Output

Report back:
- Brand detected
- Course name used
- Full path of the generated JPG (returned by `fill_course_from_url`)

In claude.ai chat, present the JPG file inline so the user can download it directly. In Claude Code on the Mac, also open the output folder:

```bash
open "/Users/alexcraiu/Desktop/Claude Playground/Course PDFs/Course JPGs - [Brand]/"
```

---

## Important Notes

- **Never modify the template.** `fitz.open(template)` reads it; the JPG is rasterised from the in-memory copy. The template file is never written back.
- **JPG only.** No intermediate PDF is saved. If the user later asks for a PDF version of the same content, use `course-dates-generator` instead.
- **Title font sizing:** 65pt (≤55 chars) → step down by 5pt until it fits. Floor is 35pt.
- **Year stripping:** years are stripped from date strings automatically (e.g. `"12 - 13 March 2026"` → `"12 - 13 March"`), matching the visual style of the template placeholders.
- **Filename sanitisation:** `/\:*?"<>|` replaced with `-` in the course title only.
- **Render quality:** 2× zoom from the 1200×1400 template gives a 2400×2800 JPG at quality 92 — high enough for LinkedIn without the file ballooning.
- **Layout constants** mirror `course-dates-generator/fill_course_pdf.py`. The new templates only add the BOOK NOW button + website footer below y=1198; the title/pill/dates region is identical, so no constants needed retuning.
- **If a new brand or domain is added**, update both `BRAND_TEMPLATES` and `BRAND_FROM_DOMAIN` in `fill_course_jpg.py`.
