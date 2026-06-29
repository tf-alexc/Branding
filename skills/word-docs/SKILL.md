---
name: word-docs
description: Rebuild any Word document with TrustFlight brand styling using the master template. Use this skill whenever the user asks to restyle, brand, recreate, or draft a Word document (including a brief) to match TrustFlight standards.
---

# TrustFlight Word Branding Skill

**Script:** `~/.claude/skills/word-docs/word_docs.py`  
**Master template (full):** `~/.claude/skills/word-docs/templates/Basic Document.docx`  
**Master template (letterhead):** `~/.claude/skills/word-docs/templates/Basic Letterhead.docx`  
**Dependencies:** `python-docx` (required), `docx2pdf` (required for PDF export — `pip install docx2pdf`). On macOS, `docx2pdf` drives Word.app for full-fidelity rendering. LibreOffice headless is used as a fallback if installed.

The script picks one of the two bundled templates based on the document type, inherits its named styles, fonts, page layout, headers and footers, then inserts the content from a JSON spec.

---

## Step 0 — Always ask: high-level or basic branding?

Before doing anything else, **always** ask the user this question and surface it as two selectable options. Do not skip the question, do not infer the answer from context — even if the user has already used a keyword like "brief". This is the single decision that picks the template.

1. **High-level document** — uses `Basic Document.docx`. The full template: cover page, Revision History page, back-cover contact page. User content goes between Revision History and the back cover. Set `is_brief: false` (or omit the flag) in the JSON spec. Pick this when the doc is substantial, formal, or audience-facing: manuals, reports, policies, customer-facing deliverables.
2. **Basic branding / brief** — uses `Basic Letterhead.docx`. The lightest template: branded only via the header and footer, no cover, no Revision History, no back cover. Triggered explicitly (the user picks this option) or when the user uses words like "brief", "letter", "short doc", "memo". Set `is_brief: true` in the JSON spec.

---

## Brand Styling Reference (from master template)

| Element | Spec |
|---|---|
| Body font | Open Sans, 8pt, `#242D41` |
| Heading 1 | Open Sans Light, 24pt, `#062955` |
| Heading 2 | Open Sans SemiBold, 14pt, `#062955` |
| Heading 3 | Open Sans SemiBold, 10pt bold, `#062955` |
| Title | Open Sans Bold, 14pt, `#062955` |
| Subtitle | Open Sans Light, 23pt, `#062955` |
| Table Heading (col headers) | Open Sans Bold, 8pt, `#1E5BB5` text + thick blue bottom border (`#1E5BB5`, 1.5pt) |
| Table Row Heading (first col) | Open Sans Bold, 8pt, `#242D41` |
| Table grid lines | `#D9D9D9` single, 0.5pt |

**Named styles available in the template:**
`Title`, `Subtitle`, `heading 1`, `heading 2`, `heading 3`, `Table Heading`, `Table Row Heading`, `Table Grid`, `Normal`, `List Paragraph`, `Numbered List`

---

## Process

1. **Read the source document** with the Word MCP tool (`get_document_text`) to understand its structure — headings, tables, paragraphs.
2. **Map the content** to the JSON spec below.
3. **Write a temp JSON file** (e.g. `/tmp/doc_data.json`) with the mapped content.
4. **Run the script:**
   ```bash
   python3 ~/.claude/skills/word-docs/word_docs.py /tmp/doc_data.json
   ```
5. The script saves to `output_path` — always set this to the original source file path to override it. A PDF is automatically produced next to the DOCX with the same base name (e.g. `output.docx` + `output.pdf`).

---

## JSON Spec

In **Basic Document** mode, `title` and `subtitle` populate the cover page of `Basic Document.docx` (they replace the `Document Title Goes Here` and `Document Subtitle` placeholders), and `sections` are inserted between the Revision History page and the back-cover page.

In **Brief** mode (`is_brief: true`), the script opens `Basic Letterhead.docx` instead: `title` replaces the Title paragraph at the top, `subtitle` is ignored (the letterhead has no subtitle slot), and `sections` are inserted below the title. There is no cover, Revision History, or back cover.

```json
{
  "output_path": "/path/to/original.docx",
  "title": "DOCUMENT TITLE",
  "subtitle": "Optional subtitle line",
  "is_brief": false,
  "sections": [
    {
      "heading": "SECTION NAME",
      "heading_level": 2,
      "table": {
        "headers": ["", "Column A", "Column B"],
        "rows": [
          ["Field label", "Value A", "Value B"],
          ["Another field", "Value A", "Value B"]
        ],
        "col_widths": [4200, 3170, 3170]
      }
    },
    {
      "heading": "Prose Section",
      "heading_level": 2,
      "paragraphs": [
        "First paragraph of body text.",
        "Second paragraph."
      ],
      "bullets": [
        "Bullet one",
        "Bullet two"
      ],
      "numbered": [
        "First step",
        "Second step"
      ]
    }
  ]
}
```

### Section content keys

A section may combine any of `table`, `paragraphs`, `bullets`, and `numbered`. They render in that order: table → paragraphs → bullets → numbered. Use multiple sections if you need a different order.

- **`paragraphs`** → `Normal` style.
- **`bullets`** → `List Paragraph` style (the template's bulleted-list style). **Never** prefix items with `•`, `-`, `*`, or any other character — Word draws the bullet from the style. Adding a literal character creates a giant double-bullet.
- **`numbered`** → `Numbered List` style. **Never** prefix items with `1.`, `1)`, etc. — the style numbers them.

Both list styles inherit bullet character, indentation, and size directly from the master template, so they always match the brand.

### Table of Contents

The Basic Document template includes a TOC field. After every basic-mode build the script:

- Rewrites the TOC instruction to `TOC \o "1-2" \h \z \u`, so **only H1 and H2 headings appear in the TOC** — H3 and deeper are excluded by design.
- Marks every `w:fldChar` dirty and sets `<w:updateFields val="true"/>` in `settings.xml`, so Word refreshes the TOC automatically the next time the document is opened, including when `docx2pdf` opens it to produce the PDF. No manual "Update field" step required.

When writing content, you can still use Heading 3 (and deeper) inside a section — those headings just won't be indexed in the TOC.

### End page (contact card)

The back-cover contact card from the master template is preserved verbatim — content, formatting, trailing layout paragraphs, everything — and a hard page break is always inserted directly before it so the card lands on its own page regardless of how much user content comes before. Do not duplicate or rewrite the contact-card content in the JSON spec; it is restored from the template on every build.

### col_widths (optional, in twips)
If omitted, defaults are applied automatically:
- 1 col: `[10540]`
- 2 cols: `[5270, 5270]`
- 3 cols: `[4200, 3170, 3170]` — field label (40%) + two data cols (30% each)

To convert inches to twips: `inches × 1440`

### Table styling rules
- `headers` row → **Table Heading** style: blue text, thick blue bottom border
- First column of data rows → **Table Row Heading** style: bold label
- Other data cells → **Normal** style
- All table borders → `#D9D9D9` gray grid

## Example — Form with Tables (SRF pattern)

```json
{
  "output_path": "/Users/alexcraiu/Downloads/SRF-TrustFlight.docx",
  "title": "SITE-TO-SITE IPSEC REQUEST FORM",
  "subtitle": "Saudi Royal Fleet - TrustFlight",
  "sections": [
    {
      "heading": "CONTACT DETAILS",
      "table": {
        "headers": ["", "SRF", "TrustFlight"],
        "rows": [
          ["Technical contact name", "", ""],
          ["Email address", "", "Dmitrii.golub@trustflight.com"],
          ["Telephone number", "", ""]
        ]
      }
    }
  ]
}
```
