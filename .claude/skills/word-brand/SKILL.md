---
name: word-brand
description: Rebuild any Word document with TrustFlight brand styling using the master template. Use this skill whenever the user asks to restyle, brand, or recreate a Word document to match TrustFlight standards.
---

# TrustFlight Word Branding Skill

**Script:** `~/.claude/skills/word-brand/word_brand.py`  
**Master template:** `/Users/alexcraiu/Desktop/Documents/Word templates/Basic Document.docx`  
**Dependency:** `python-docx` (already installed)

The script opens the master template as the base document — inheriting all named styles, fonts, page layout, headers and footers — then rebuilds the content from a JSON spec.

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
