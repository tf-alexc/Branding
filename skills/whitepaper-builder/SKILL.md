---
name: whitepaper-builder
description: Build a TrustFlight-branded whitepaper from the master Whitepaper template. Triggers on any request for a "high-level whitepaper", "whitepaper", "white paper", long-form report, thought-leadership document, or similar keywords (e.g. "draft a whitepaper on X", "write a high-level whitepaper", "restyle this whitepaper").
---

# TrustFlight Whitepaper Builder

**Script:** `~/.claude/skills/whitepaper-builder/whitepaper_builder.py`
**Master template (Word, used by the script):** `/Users/alexcraiu/Desktop/Documents/Word templates/Whitepaper Template.docx`
**Visual reference (PDF, bundled with the skill):** `~/.claude/skills/whitepaper-builder/Whitepaper Template.pdf`
**Dependency:** `python-docx` (already installed)

The bundled PDF is the canonical visual reference for every layout, colour, and type spec in this skill. Open it whenever you need to verify a layout choice or check that the master Word template still matches the brand intent. The script itself reads only the `.docx` template.

The script opens the master template as the base document, inheriting all named styles, fonts, headers, footers, page backgrounds, and the **static back cover**. It then injects cover content, builds the table of contents, and lays out body pages using a small set of reusable layouts. The back cover (last page) is never altered.

---

## Brand styling reference (from the master template)

| Element | Spec |
|---|---|
| Body font | Open Sans, 10pt, `#242D41` |
| Cover title | Open Sans Light, 44pt, `#FFFFFF` |
| Cover eyebrow | Open Sans Bold, 14pt, `#16C2EE` (cyan), letter-spaced |
| Cover overview | Open Sans SemiBold, 12pt, `#062955` (on light band) |
| Cover date | Open Sans SemiBold, 10pt, `#062955` |
| TOC title | Open Sans Light, 44pt, `#FFFFFF` (on navy) |
| TOC entry number | Open Sans Light, 24pt, `#16C2EE` |
| TOC entry title | Open Sans Regular, 12pt, `#242D41` |
| Page eyebrow | Open Sans Bold, 11pt, `#062955`, letter-spaced |
| Page title (H1) | Open Sans Light, 32pt, `#062955` |
| Section heading (H2) | Open Sans SemiBold, 14pt, `#1E5BB5` |
| Lead paragraph | Open Sans Bold, 10pt, `#242D41` |
| Body paragraph | Open Sans Regular, 10pt, `#242D41` |
| Bulleted list | Open Sans Regular, 10pt, `#242D41`, cyan square bullet |
| Callout box title | Open Sans SemiBold, 14pt, `#16C2EE` on `#0A2A5A` |
| Callout box body | Open Sans Regular, 10pt, `#FFFFFF` on `#0A2A5A` |
| Side-callout title | Open Sans SemiBold, 14pt, `#1E5BB5` on `#E4ECF7` |
| Side-callout body | Open Sans Regular, 10pt, `#242D41` on `#E4ECF7` |
| Header (running) | TrustFlight logo (left) + `WHERE AEROSPACE PLACES ITS TRUST` (right, Open Sans Bold 8pt, letter-spaced, `#FFFFFF` on navy) |
| Footer (running) | Document short title (bottom-left, Open Sans Regular 9pt, `#7A8AA8`) + page number (bottom-right) |

### Named styles available in the template

`Whitepaper Cover Title`, `Whitepaper Cover Eyebrow`, `Whitepaper Cover Overview`, `Whitepaper Cover Date`, `Whitepaper TOC Title`, `Whitepaper TOC Number`, `Whitepaper TOC Entry`, `Whitepaper Eyebrow`, `Whitepaper Title`, `Whitepaper H2`, `Whitepaper Lead`, `Whitepaper Body`, `Whitepaper Bullet`, `Whitepaper Callout Title`, `Whitepaper Callout Body`, `Whitepaper Side Callout Title`, `Whitepaper Side Callout Body`, `Whitepaper Caption`.

---

## Page layouts

The script supports a fixed set of reusable layouts. **Always pick one of these — never invent a new layout.** Reuse the same layout across pages whenever the content fits, so the document looks consistent.

| `layout` | When to use | Required fields |
|---|---|---|
| `cover` | Front page (page 1) — emitted automatically from top-level `cover` block. | n/a (top-level keys) |
| `toc` | Table of contents (page 2) — emitted automatically from top-level `toc` block. | n/a (top-level keys) |
| `hero` | First body page after TOC, or any section opener with a strong photo. Hero image fills top half; title and intro sit on the navy band underneath. | `title`, `hero_image`, `intro`, optional `subintro`, `body`, `callout` |
| `content` | Standard body page. Eyebrow + title at top, then prose, headings, and bullets. | `title`, optional `eyebrow`, `lead`, `body`, `subsections` |
| `content_image` | Body page with a supporting image floated right (used for `The TrustFlight Approach`-style pages). | `title`, `image`, optional `eyebrow`, `lead`, `body`, `subsections` |
| `two_column` | A subsection that needs side-by-side prose, or a left-rail callout next to right-side body (used for `Declaration of Compliance` and `What Auditors Are Finding`). | `columns` (array of 2) |

**Static back cover:** the last page in the master template (contacts page) is preserved verbatim. Do not include it in the JSON.

---

## Brand-rule reminders

- **No em dashes.** Use a comma, colon, or rewrite.
- Any reference to the website is `https://www.trustflight.com`.
- Font is **Open Sans** throughout. Never Arial, Aptos, or Lato.
- The **bottom-left footer text** is set once from `doc_title` and applies to every page except the cover and back cover.
- Override the source file: set `output_path` to the original location.

---

## Process

1. **Read the source content** (Word doc, PDF, brief, or notes) and identify: cover info, TOC entries, body pages.
2. **Choose layouts** — reuse the same layout type across similar pages.
3. **Map to the JSON spec** below. Keep `doc_title` short (it shows in every footer).
4. **Write a temp JSON file** (e.g. `/tmp/whitepaper.json`).
5. **Run the script:**
   ```bash
   python3 ~/.claude/skills/whitepaper-builder/whitepaper_builder.py /tmp/whitepaper.json
   ```
6. The script saves to `output_path`. The static back cover is preserved untouched.

---

## JSON spec

```json
{
  "output_path": "/path/to/whitepaper.docx",
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

- `output_path` — absolute path to save to (overrides original source).
- `doc_title` — short title shown in the bottom-left footer of every body page.
- `cover.eyebrow` — small caps, cyan accent (e.g. `PART 5 SMS WHITE PAPER`).
- `cover.title` — main title, no more than two lines.
- `cover.overview` — single short line, sits in the light band under the title.
- `cover.date` — month and year, e.g. `April 2026`.
- `toc[]` — `{ "page": "03", "title": "..." }`. Pages are emitted in the order they appear; the script does not auto-number.
- `pages[]` — body pages, in order. Each must have a `layout`.

### Layout fields

**`hero`** — `title`, `hero_image`, `intro` (bold, on navy band), `subintro` (regular, on navy band), `body[]`, `callout { title, body }` (renders as a navy box at the foot).

**`content`** — `eyebrow` (caps), `title`, `lead` (bold opening paragraph), `body[]`, `subsections[]`. Each subsection has `heading`, optional `intro`/`lead`, `body[]`, `bullets[]`, or a nested `layout: "two_column"` with `columns[2]`.

**`content_image`** — same as `content` but with an `image` floated to the right of the body.

**`two_column`** (as nested subsection layout) — `columns` is an array of exactly two objects, each with `{ lead, body[], bullets[] }`. Left column is narrower (label rail), right column carries the body. Use this for the side-callout pattern (e.g. `What Auditors Are Finding`).

---

## Example — minimum viable whitepaper

```json
{
  "output_path": "/Users/alexcraiu/Downloads/Part-5-SMS-Whitepaper.docx",
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

- The script never edits the **last section** (back cover) of the master template. It inserts new sections **before** it.
- The footer `doc_title` is written into every body section's footer XML, but the back cover footer is left alone.
- Hero and content images are inserted at the page's full content width, cropped via a rounded-rectangle frame (Azure `#479FF8` 1pt outline, per brand rules).
- If `python-docx` cannot represent a shape (e.g. the curved decorative cutouts), the master template carries that shape natively — the script only fills text and inserts pictures.
- If you need a new layout, add it to the script's `LAYOUTS` dispatch table and document it here. Do not improvise inline styling.
