---
name: whitepaper-builder
description: Build a TrustFlight-branded whitepaper from the bundled PDF master template. Triggers on any request for a "high-level whitepaper", "whitepaper", "white paper", long-form report, thought-leadership document, or similar keywords (e.g. "draft a whitepaper on X", "write a high-level whitepaper", "restyle this whitepaper").
---

# TrustFlight Whitepaper Builder

**Script:** `~/.claude/skills/whitepaper-builder/whitepaper_builder.py`
**Master template (PDF, bundled with the skill):** `~/.claude/skills/whitepaper-builder/Whitepaper Template.pdf`
**Font:** `/Users/alexcraiu/Library/Fonts/OpenSans-VariableFont_wdth,wght.ttf`
**Dependency:** `PyMuPDF` (already installed)

The bundled PDF is the canonical template **and** the visual reference for every layout, colour, and type spec in this skill. The script opens it, clones the correct page for each requested layout, redacts the placeholder content, overlays the new content in Open Sans, and emits a new PDF. The **back cover (page 7) is copied verbatim** and never edited.

Open the bundled PDF whenever you need to verify a layout choice, colour, or type spec — it is the source of truth.

---

## Brand styling reference (from the bundled PDF)

| Element | Spec |
|---|---|
| Body | Open Sans Regular, 10pt, `#242D41` |
| Cover title | Open Sans Light, 44pt, `#FFFFFF` on navy `#062955` |
| Cover eyebrow | Open Sans Bold, 14pt, `#16C2EE` (cyan), letter-spaced |
| Cover overview | Open Sans SemiBold, 12pt, `#062955` on light band |
| Cover date | Open Sans SemiBold, 10pt, `#062955` |
| TOC title | Open Sans Light, 44pt, `#FFFFFF` on navy |
| TOC entry number | Open Sans Light, 24pt, `#16C2EE` |
| TOC entry title | Open Sans Regular, 12pt, `#242D41` |
| Page eyebrow | Open Sans Bold, 11pt, `#062955`, letter-spaced |
| Page title (H1) | Open Sans Light, 32pt, `#062955` |
| Section heading (H2) | Open Sans SemiBold, 14pt, `#1E5BB5` |
| Lead paragraph | Open Sans Bold, 10pt, `#242D41` |
| Body paragraph | Open Sans Regular, 10pt, `#242D41` |
| Bulleted list | Open Sans Regular, 10pt, `#242D41`, cyan square bullet |
| Callout box (dark) | navy `#0A2A5A` bg, cyan title, white body |
| Side-callout (light) | `#E4ECF7` bg, blue title `#1E5BB5`, ink body |
| Running header | TrustFlight logo (left), `WHERE AEROSPACE PLACES ITS TRUST` (right) on navy |
| Running footer | Document short title (bottom-left, `#7A8AA8`), page number (bottom-right) |

---

## Page layouts

The script reuses the seven pages of the bundled PDF as canonical layouts. **Always pick one from this list — never invent a new layout.** Reuse the same layout across pages whenever the content fits, so the document stays visually consistent.

| `layout` | Source page in template | When to use | Required fields |
|---|---|---|---|
| `cover` | Page 1 | Front page. Emitted automatically from the top-level `cover` block. | (top-level keys) |
| `toc` | Page 2 | Table of contents. Emitted automatically from the top-level `toc` block. | (top-level keys) |
| `hero` | Page 3 | First body page after TOC, or any section opener with a strong photo. Hero image fills top half. | `title`, `hero_image`, `intro`, optional `subintro`, `body`, `callout` |
| `content` | Page 4 | Standard body page. Eyebrow + title at top, then prose, headings, bullets. | `title`, optional `eyebrow`, `lead`, `body`, `subsections` |
| `content_side_callout` | Page 5 | Body page with a left-rail callout next to right-side body. | `title`, `body`, `subsections` (one must use the `two_column` nested layout with `side_callout: true`) |
| `content_image` | Page 6 | Body page with a supporting image floated right. | `title`, `image`, optional `eyebrow`, `lead`, `body`, `subsections` |

**Static back cover:** page 7 of the template is appended verbatim. Do not include it in the JSON.

---

## Brand-rule reminders

- **No em dashes.** Use a comma, colon, or rewrite.
- Any reference to the website is `https://www.trustflight.com`.
- Font is **Open Sans** throughout. Never Arial, Aptos, or Lato.
- The **bottom-left footer text** is set once from `doc_title` and applies to every page except the cover and back cover.
- Override the source file: set `output_path` to the original location.

---

## Process

1. **Read the source content** (PDF, brief, or notes) and identify: cover info, TOC entries, body pages.
2. **Choose layouts** from the table above. Reuse the same layout type across similar pages.
3. **Map to the JSON spec** below. Keep `doc_title` short (it shows in every footer).
4. **Write a temp JSON file** (e.g. `/tmp/whitepaper.json`).
5. **Run the script:**
   ```bash
   python3 ~/.claude/skills/whitepaper-builder/whitepaper_builder.py /tmp/whitepaper.json
   ```
6. The script saves a PDF to `output_path`. The static back cover is appended automatically.

---

## JSON spec

```json
{
  "output_path": "/path/to/whitepaper.pdf",
  "doc_title": "Part 5 SMS",
  "cover": {
    "eyebrow": "DOCUMENT EYEBROW",
    "title": "Main Document Title Section In No More Than Two Rows",
    "overview": "Quick overview of the document (no more than two rows)",
    "date": "April 2026"
  },
  "toc": [
    {"page": "03", "title": "Executive Summary"},
    {"page": "04", "title": "What Part 5 Actually Requires"},
    {"page": "05", "title": "Why the FAA Says You Can't Buy Compliance"}
  ],
  "pages": [
    {
      "layout": "hero",
      "title": "Executive Summary",
      "hero_image": "/path/to/photo.jpg",
      "intro": "On May 28, 2027, every Part 135 operator in the United States must have a fully implemented Safety Management System compliant with 14 CFR Part 5.",
      "subintro": "That deadline is now roughly thirteen months away.",
      "body": [
        "For many operators, the instinct is to solve this problem the fastest way possible.",
        "Advisory Circular 120-92D makes clear that operators cannot buy a generic software package."
      ],
      "callout": {
        "title": "Who is this document for?",
        "body": "This white paper is written for Part 135 operators with five or more aircraft."
      }
    },
    {
      "layout": "content",
      "eyebrow": "THE REGULATORY LANDSCAPE",
      "title": "What Part 5 Actually Requires",
      "lead": "The FAA published its final rule expanding 14 CFR Part 5 on April 26, 2024.",
      "body": [
        "The compliance timeline is structured around two milestones."
      ],
      "subsections": [
        {
          "heading": "The Four Components",
          "intro": "Part 5 is organized around four integrated components:",
          "bullets": [
            "Safety Policy (Subpart B) establishes the foundation.",
            "Safety Risk Management (Subpart C) is the analytical core.",
            "Safety Assurance (Subpart D) requires continuous monitoring.",
            "Safety Promotion (Subpart E) addresses the human dimension."
          ]
        },
        {
          "heading": "The Declaration of Compliance",
          "layout": "two_column",
          "columns": [
            {
              "lead": "The Declaration of Compliance is the culmination of the SMS development process.",
              "body": ["Operators must have a fully functional, compliant system before submitting."]
            },
            {
              "body": ["The regulatory environment is also intensifying."]
            }
          ]
        }
      ]
    },
    {
      "layout": "content_image",
      "eyebrow": "THE TRUSTFLIGHT APPROACH",
      "title": "Integrated Consulting, Training, and Technology for Part 5 SMS",
      "image": "/path/to/handshake.jpg",
      "lead": "TrustFlight is the Aerospace Safety Intelligence Platform.",
      "subsections": [
        {
          "heading": "Why Integration Matters",
          "lead": "The market today offers two categories of SMS solution.",
          "body": ["Software platforms provide infrastructure but cannot build the safety culture."]
        }
      ]
    }
  ]
}
```

### Field reference

- `output_path` — absolute path to save to (a `.pdf`).
- `doc_title` — short title shown in the bottom-left footer of every body page.
- `cover.eyebrow` — small caps, cyan accent (e.g. `PART 5 SMS WHITE PAPER`).
- `cover.title` — main title, no more than two lines.
- `cover.overview` — single short line, sits in the light band under the title.
- `cover.date` — month and year, e.g. `April 2026`.
- `toc[]` — `{ "page": "03", "title": "..." }`. Entries are rendered in order; the script does not auto-number.
- `pages[]` — body pages in order. Each must have a `layout` from the table above.

### Layout fields

**`hero`** — `title`, `hero_image`, `intro` (bold, on navy band), `subintro` (regular, on navy band), `body[]`, `callout { title, body }` (renders as a navy box at the foot of the page).

**`content`** — `eyebrow` (caps), `title`, `lead` (bold opening paragraph), `body[]`, `subsections[]`. Each subsection has `heading`, optional `intro`/`lead`, `body[]`, `bullets[]`, or a nested `layout: "two_column"` with `columns[2]`.

**`content_side_callout`** — same fields as `content`. The first subsection should be a `two_column` with `side_callout: true` to render the left rail in the light blue panel style.

**`content_image`** — same as `content`, plus an `image` floated to the right of the body.

**`two_column`** (nested under a subsection) — `columns` is an array of exactly two objects, each with `{ lead, body[], bullets[] }`. Use this for the side-callout pattern (e.g. `What Auditors Are Finding`) or two-column prose (e.g. `Declaration of Compliance`).

---

## Example — minimum viable whitepaper

```json
{
  "output_path": "/Users/alexcraiu/Downloads/Part-5-SMS-Whitepaper.pdf",
  "doc_title": "Part 5 SMS",
  "cover": {
    "eyebrow": "PART 5 SMS WHITE PAPER",
    "title": "Building an SMS the FAA Will Actually Accept",
    "overview": "What a decade of global SMS implementation reveals for Part 135 operators",
    "date": "April 2026"
  },
  "toc": [
    {"page": "03", "title": "Executive Summary"},
    {"page": "04", "title": "What Part 5 Actually Requires"}
  ],
  "pages": [
    {
      "layout": "hero",
      "title": "Executive Summary",
      "hero_image": "/Users/alexcraiu/Pictures/jet-nose-lr.jpg",
      "intro": "On May 28, 2027, every Part 135 operator must have a fully implemented SMS.",
      "subintro": "That deadline is now roughly thirteen months away.",
      "body": ["Advisory Circular 120-92D makes clear that off-the-shelf solutions will not work."],
      "callout": {
        "title": "Who is this document for?",
        "body": "Part 135 operators with five or more aircraft."
      }
    }
  ]
}
```

---

## Implementation notes

- The script **never edits page 7** of the template. It always appends it verbatim as the final page.
- The footer `doc_title` is written into the bottom-left of every page from page 2 onwards; the cover and back cover are excluded.
- Page numbers in the bottom-right of body pages are written by the script in sequence (starting at 2 for the TOC).
- Hero, content, and content_image images are inserted at the page's full content width, behind the cyan rounded-frame element from the template.
- Open Sans is loaded from `~/Library/Fonts/OpenSans-VariableFont_wdth,wght.ttf`. If the file is missing, the script falls back to PyMuPDF's `helv` Helvetica (and warns).
- If a content block overflows its layout's body region, the script appends an extra copy of the same layout (without the eyebrow/title) so the run continues on a consistent-looking page.
- New layouts must be added to the `LAYOUTS` dispatch table in the script AND documented in the table above. Never improvise inline styling.
