---
name: bsl-course-sheets
description: Automate the creation of Baines Simmons course sheet PDFs. Use this skill whenever the user asks to generate, fill, process, or export BSL course sheets from the source PDFs. Handles extraction, rendering, and output for all 70+ course sheet PDFs across all pathways.
---

# BSL Course Sheet Automation

**Script:** `/Users/alexcraiu/Desktop/Claude Playground/InDesign/BSL Course Sheets/fill_course_sheet.py`  
**Template:** `/Users/alexcraiu/Desktop/Claude Playground/InDesign/BSL Course Sheets/Course - Regulatory Compliance Pathway - Template.pdf`  
**Template naming convention:** `Course - [Pathway Name] - Template.pdf` — when the user asks to process a course, confirm it belongs to the same pathway as the active template before running.

**Known pathways (5 total):**
1. Regulatory Compliance Pathway
2. Human Factors & Error Management Pathway
3. Compliance Monitoring Pathway
4. Safety Risk Management Pathway
5. Initial Airworthiness Pathway  
**Source PDFs:** `/Users/alexcraiu/Desktop/Documents/Baines Simmons/Course Sheets/CURRENT PDF VERSIONS/`  
**Output:** `/Users/alexcraiu/Desktop/Claude Playground/InDesign/BSL Course Sheets/Output/`  
**Fonts:** `/Users/alexcraiu/Desktop/Claude Playground/InDesign/BSL Course Sheets/fonts/` (static OpenSans instances)

---

## Running the Script

Single file (opens both source and output PDFs on completion):
```bash
python3 fill_course_sheet.py '/path/to/source.pdf'
```

All files (no auto-open — too many files):
```bash
python3 fill_course_sheet.py --all
```

---

## Template Structure

**Page 1:**
- Midnight header band (y=0–144.8): heading (`[Course Title]`, 24pt Light grey), subtitle (`[Subtitle]`, 12pt White), level + duration (8.5pt Bold White)
- Pathway label: already set in template — never replace it
- Overview text box: `OVERVIEW_RECT = Rect(36, 157, 579, 740)` — body text + headings + bullets
- Cyan stripe at y=140.7–144.8; body text starts at y≈157 (12pt below stripe)

**Page 2:**
- Header band (y=0–57.4) with cyan stripe at y=55.7–59.7
- Body block: `BODY_RECT_P2 = Rect(36, 66, 579, 655)` — overflow from page 1, prerequisites, course details, related courses
- Contact Us section (y=661–720): **never touch** — must remain exactly as in the template; never redact or re-render it
- Footer (y=747): static, never touched

### Template placeholder strings (used to locate and replace header fields)
```python
T_HEADING  = '[Course Title]'
T_SUBTITLE = '[Subtitle]'
T_LEVEL    = 'Practitioner'
T_DURATION = '1 Day'
```
If a `[warn] Not found` appears for any of these, the template has been updated — re-inspect and update the constants.

### Baseline placement
Use `rect.y0 + font.ascender * fontsize` as the baseline for header field replacements — do NOT use `rect.y1 - 1`, which causes ~5pt vertical drift vs the template position.

### Contact info filtering
Source PDFs contain footer contact lines on every page (bainessimmons.com, +44 phone, email). These must **never appear in the output body**. The `_is_contact_text()` helper detects and skips these during extraction across all paths: overview, prerequisites, course details, and related courses.

---

## Content Extraction Rules

### Source PDF page count
- **2-page sources:** page 1 = title + full overview; page 2 = prerequisites + course details + related courses
- **3-page sources:** page 1 = title + partial overview; page 2 = overview continuation (before "Prerequisites") + prerequisites + course details + FAQs; page 3 = more FAQs + related courses

### Overview body text
- Extract from page 1 body zone: `200 <= y <= 760`, exclude top-right header (x > 300, y < 100), exclude quote column (x > 380, y < 400)
- For 3-page sources: also extract from source page 2 above "Prerequisites" — offset those spans' y by +1000 so they sort after all page-1 content
- **FAQs are always excluded** — they were removed in the new condensed template design

### Section routing (per-page, never merge pages)
- **Prerequisites:** first page (after p1) that contains "Prerequisites"
- **Course details:** first page (after p1) that contains "Course format:"
- **Related courses:** last page that contains "courses you might"
- Never merge all page spans — cross-page y-value mixing causes content bleeding

### Headings detected by pattern only (never by source font weight)
```python
HEADING_PATTERNS = [
    'how will this course benefit',
    'key areas of focus',
    'is this course right for me',
    'this course would also benefit',
]
```

### Bullet handling
- Source PDFs use SymbolMT font spans for `•` markers — order in PDF stream varies
- Always track bullet separately (`cur_has_bullet` flag) and prepend at front of line
- Bullet continuation lines (split by source PDF wrapping, `new_para=False`) are reattached to preceding bullet in Pass 3
- **Section-boundary bullet split:** when a bullet's last wrapped line is also the last span before a `BODY_STOP` keyword (e.g. "Prerequisites"), the Pass 1 final flush must use `cur_new_para` (not hardcoded `True`) so Pass 3 can reattach it. If a bullet appears visually split at a section boundary, this is the likely cause.
- **Related courses bullet continuation:** `_extract_related_courses` post-processes its segment list — any non-bullet, non-heading entry that immediately follows a bullet entry is merged onto it. Fixes source PDFs where a related course description wraps onto a second line.

### Title splitting
- If the source title contains a hyphen, en dash (–), or em dash (—), split at the first occurrence: text before → heading field, text after → subtitle field
- En/em dashes are normalised to ` - ` before the split logic runs: `re.sub(r'\s*[–—]\s*', ' - ', full_title)`
- If ` - ` appears more than once (e.g. "TR10 - MRP Part 145 - Successfully Applying..."): first two parts → heading, remainder → subtitle

### Output filename format
- Pattern: `{code} - {title_rest} - {subtitle}.pdf` (subtitle part omitted if empty)
- `code` = first word of heading (e.g. `TR02`)
- `title_rest` = heading with code prefix removed, leading `- ` stripped (e.g. `UK CAA/EASA Part 145`)
- Invalid filename characters (`/ \ : * ? " < > |`) are replaced with a space; double spaces collapsed
- Example: `TR02 - UK CAA EASA Part 145 - Understanding the Requirements for Maintenance.pdf`

### Orphan word prevention
- `_word_wrap` checks if the last line is a single word after wrapping
- If so, merges it onto the previous line, even if it slightly exceeds `max_width` (expanding the right boundary)
- Applies to all text: body paragraphs, bullets, headings, FAQ lines

### Duplicate prevention
- `process()` checks if the output file already exists before running. If it does, prints `[skip]` and returns without regenerating.
- To force a regeneration, delete the existing output file first.

### FAQ extraction
- `_extract_faqs(doc)` scans all source pages for Q/A patterns (`Q. `, `Q: `, `A. `, `A: `)
- Triggered by detecting a "FAQ"/"FAQs" heading span; stops at "courses you might"
- Returns list of `(question_text, answer_text)` tuples with prefixes stripped
- **`_extract_detail` and prerequisites extraction must include `'faq'` in their stop keywords** — otherwise FAQ body text bleeds into Course Size or Prerequisites sections

---

## Rendering Rules

### Typography
- All text rendered via `fitz.TextWriter` + `fitz.Font(fontfile=...)` — never `insert_text`
- **Body text:** Open Sans Regular, 8.5pt, Graphite (#242D41)
- **Intro paragraphs** (before first heading): Open Sans Regular, 8.5pt, Sapphire (#1E5BB5)
- **Section headings:** Open Sans SemiBold, 14pt, Sapphire (#1E5BB5)
- **Bullet markers `•`:** Open Sans Regular, 8.5pt, Azure (#479FF8), x = rect.x0
- **Bullet text:** Open Sans Regular, 8.5pt, Graphite, x = rect.x0 + 12pt indent
- **Course detail labels** (Course format, Course level, Assessment, Course size): Open Sans Bold, 8.5pt, Graphite — rendered inline, value follows in Regular
- **Related course codes** (TR55, TQ02, etc.): Open Sans Bold, 8.5pt, Graphite — rendered inline at start of bullet, description follows in Regular
- **Title/heading:** course code (first word, e.g. "TR02") Open Sans SemiBold 24pt Light (#E0E7F5); remainder Open Sans Light 24pt Light (#E0E7F5) — two separate `tw.append` calls, x offset via `f_semi.text_length(code_str, fontsize)`
- **Subtitle:** Open Sans Regular, 12pt, White
- **Level / Duration:** Open Sans Bold, 8.5pt, White
- Duration: title case (`'1 Day'` not `'1 day'`)

### Spacing rules
- **Paragraph spacing:** 4.5pt — applied via empty `('', False)` segments
- **Space before heading:** `gap_before_head = 12` (12pt fixed)
- **Heading leading:** `lead_head = sz_head * 1.25` (17.5pt) — controls gap below heading
- **Space after heading:** none — `para_space` is suppressed when the previous element was a heading (`last_was_heading` flag)

### Layout + rendering pipeline
- `_layout_segments(rect, segments)` → `(layout, overflow, final_y)` — pure computation, no side effects
- `_render_overview_text(page, rect, segments)` → `(overflow, final_y)` — calls layout then does three TextWriter passes
- **Always use the tuple return from `_render_overview_text`** — it now returns `(overflow, final_y)`, not just `overflow`

### Prerequisites on page 1
After rendering the overview, if there is no overflow AND prerequisites fit entirely in the remaining space, render them on page 1 and exclude from page 2. Uses `_layout_segments` for a dry-run check before committing to render.

### Three-pass TextWriter rendering
Overview and page 2 body both use three passes (one TextWriter per colour):
1. Graphite: body paragraphs + bullet text
2. Sapphire: section headings + intro paragraphs
3. Azure: bullet markers only

### Redaction approach
- Use `add_redact_annot(rect, fill=())` + `apply_redactions(images=0, graphics=0)` to clear text without destroying vector background graphics
- **Batch all `add_redact_annot` calls per page before a single `apply_redactions()` call** — multiple `apply_redactions()` calls per page wipe TextWriter output from previous calls

---

## Page 2 Behaviour

**Always populate page 2 automatically — never ask the user what should go on it.**

Page 2 body block renders in this order:
1. Overflow from page 1 overview (segments that didn't fit in OVERVIEW_RECT)
2. Prerequisites section — only if not already rendered on page 1
3. Course details section (heading + "Label: value" lines for format, level, assessment, size)
4. Related courses section ("Courses you might also like to consider" heading + bullet items)
5. FAQ section — "FAQ" heading (Sapphire SemiBold), then each pair as:
   - `faq_q`: `•` Azure bullet + `Q` Bold Graphite + `: ` Regular + question text Regular Graphite
   - `faq_a`: indented `A` Bold Graphite + `: ` Regular + answer text Regular Graphite (no bullet)
   - Extra `para_space` before each `faq_q` **except the first** (check `last_was_heading` to skip it)

Everything must fit within the 2-page output regardless of source page count.

---

## Brand Colours

| Name | Hex | Use |
|------|-----|-----|
| Graphite | #242D41 | Body text |
| Sapphire | #1E5BB5 | Section headings + intro paragraphs |
| Light | #E0E7F5 | Title (large heading) |
| Azure | #479FF8 | Bullet markers |
| White | #FFFFFF | Subtitle, level, duration |
