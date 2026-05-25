---
name: word-brand
description: Rebuild any Word document with TrustFlight brand styling using the master template. Use this skill whenever the user asks to restyle, brand, or recreate a Word document to match TrustFlight standards.
---

# TrustFlight Word Branding Skill

**Script:** `~/.claude/skills/word-brand/word_brand.py`  
**Master template (Basic):** `/Users/alexcraiu/Desktop/Documents/Word templates/Basic Document.docx`  
**Master template (Proposal):** `~/.claude/skills/word-brand/templates/Proposal Template.docx`  
**Dependency:** `python-docx` (already installed)

The script opens the relevant master template as the base document, inheriting all named styles, fonts, page layout, headers and footers, then rebuilds the content from a JSON spec.

---

## Step 0 — Ask: Document Type

Before doing anything else, ask the user which document type to produce:

1. **Basic Document** — default for any restyling, form, report, internal doc. Follow the rest of this SKILL.md as-is.
2. **Proposal** — only when the user specifically requests a proposal. Follow the **Proposal sub-flow** below instead of the basic process.

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
   python3 ~/.claude/skills/word-brand/word_brand.py /tmp/doc_data.json
   ```
5. The script saves to `output_path` — always set this to the original source file path to override it.

---

## JSON Spec

```json
{
  "output_path": "/path/to/original.docx",
  "title": "DOCUMENT TITLE",
  "subtitle": "Optional subtitle line",
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
      ]
    }
  ]
}
```

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

---

## Proposal Sub-Flow

Use this flow **only when the user specifically asks for a proposal**. Do not trigger it for general document branding.

**Master template:** `~/.claude/skills/word-brand/templates/Proposal Template.docx`

### Step P1 — Ask which product(s) the proposal is for

Ask the user which product or service this proposal covers. Multi-select allowed:

- **Tech Log**
- **Centrik 5**
- **Smart Suite** (Smart Documents + Smart Regulations)

The content baked into the proposal must match the selection. If the user picks Centrik 5 and Smart Suite, include both sections and **omit** Tech Log entirely. Same logic for any other combination.

### Step P2 — Ask for the RFQ / RFP / Request for Submission

Ask the user to attach the RFQ, RFP, or Request for Submission the prospect sent. The proposal structure must follow what the customer asked for: align section headings, scope coverage, evaluation criteria, and terminology to the prospect's document.

If the user does not have one to attach, confirm before proceeding with the default proposal structure.

### Step P3 — Build the proposal

Build from `Proposal Template.docx`, applying these rules:

1. **Cover page and end page** — reuse as-is from the Proposal Template. Do not regenerate or restyle them. Only the dynamic placeholders (organisation name, deal owner, presented-to person, date) should be updated.
2. **Body content** — use the exact content structure already baked into the Proposal Template. Do not invent new sections, do not rewrite the boilerplate prose. Only swap `[COMPANY]`, `[PRODUCT]`, and other placeholders for the prospect's actual values.
3. **Product-conditional sections** — include or exclude entire product blocks based on the Step P1 selection:
   - **Tech Log block** — heading "Tech Log Technical Overview" + Capabilities Matrix + Implementation Schedule + Framework + Proposed Schedule + SLAs.
   - **Centrik 5 block** — heading "Centrik 5 Technical Overview" + Capabilities Matrix + Implementation Schedule + Framework + Proposed Schedule + Integrations + Technical Description + SLAs + Training + Data Migration.
   - **Smart Suite block** — heading "Smart Suite Technical Overview" + Smart Documents Overview + Capabilities + Roadmap + Smart Regulations Overview + Capabilities + Roadmap + Implementation Schedule + Framework + Proposed Schedule + SLAs.
4. **Sections that always stay (regardless of product):** Company Overview and Strategic Vision, Product Capabilities (intro), Commercial Proposal, References, ISO 9001 Certification, ISO 27001 Certification.
5. **Tailor the cover letter and value propositions** to the RFP. Strip the `[SAMPLE VALUE PROPOSITIONS]` block and replace with prospect-aligned bullets pulled from the RFP scope.
6. **Save** to the path the user specifies. Default if none given: same folder as the source RFP, filename `TrustFlight Proposal - [COMPANY] - [Products].docx`.

### Proposal section inventory (reference)

Top-level structure of the Proposal Template (use this to decide what to keep / drop per product selection):

| Section | Always include | Product-gated |
|---|---|---|
| Cover page (tables + title block) | Yes | — |
| Contact Details / Copyright / TOC | Yes | — |
| Cover letter | Yes | — |
| Company Overview and Strategic Vision | Yes | — |
| Product Capabilities (intro) | Yes | — |
| Tech Log Technical Overview | — | Tech Log only |
| Centrik 5 Technical Overview | — | Centrik 5 only |
| Smart Suite Technical Overview | — | Smart Suite only |
| Commercial Proposal | Yes | — |
| References | Yes | — |
| ISO 9001 / ISO 27001 Certifications | Yes | — |
| End page | Yes | — |

---

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
