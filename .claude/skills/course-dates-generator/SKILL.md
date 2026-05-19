---
name: course-dates-generator
description: Generate sub-brand course date PDFs from the Illustrator template by scraping a course listing page. Use whenever the user asks to generate, create, or export course dates for Redline, BSL (Baines Simmons), or Kenyon.
---

# Course Dates Generator

**Templates (one per sub-brand, never modified):**
- Redline: `/Users/alexcraiu/Desktop/Claude Playground/Course PDFs/Courses - Redline - Template.pdf`
- BSL / Baines Simmons: `/Users/alexcraiu/Desktop/Claude Playground/Course PDFs/Courses - Baines Simmons - Template.pdf`
- Kenyon: `/Users/alexcraiu/Desktop/Claude Playground/Course PDFs/Courses - Kenyon - Template.pdf`

**Generation method:** Python + PyMuPDF — edits the PDF directly, no Illustrator involved.  
**Script:** `/Users/alexcraiu/.claude/skills/course-dates-generator/fill_course_pdf.py`  
**Output folder:** `/Users/alexcraiu/Desktop/Claude Playground/Course PDFs/Course - [Brand]/`  
**Output filename:** `Course - [Brand] - [Course Title].pdf` (subfolder prefix matches file prefix)

---

## Column Layout Rules

| Date types found on page | left_label | column_type | Right column |
|--------------------------|-----------|-------------|--------------|
| Both initial and recurrent | `Initial Course Dates` | `both` | Visible |
| Initial only | `Initial Course Dates` | `initial` | Hidden |
| Recurrent only | `Recurrent Course Dates` | `recurrent` | Hidden |
| Generic / no type distinction | `Upcoming Dates` | `generic` | Hidden |

---

## Step 1: Fetch & Parse Course Data

Use `WebFetch` on the URL provided by the user. Extract all courses that have **dates listed on the page**. Skip courses with no dates.

For each course, identify:
- **Course name**
- **Date type:** `initial`, `recurrent`, `both`, or `generic`
- **Left dates:** list of date strings for initial (or generic) column
- **Right dates:** list of date strings for recurrent column (empty list if single-column)

Build a working list before proceeding:
```
courses = [
  { name: "Risk Management Workshop (RMW)", type: "generic", leftDates: ["13–17 April 2026"], rightDates: [] },
  ...
]
```

---

## Step 2: For Each Course — Call fill_course_pdf.py

Run one Python call per course:

```bash
python3 /Users/alexcraiu/.claude/skills/course-dates-generator/fill_course_pdf.py << 'EOF'
# This runs __main__ — for batch use, import fill_course directly:
EOF

# For batch generation, write a one-off driver script:
python3 - << 'PYEOF'
import sys
sys.path.insert(0, "/Users/alexcraiu/.claude/skills/course-dates-generator")
from fill_course_pdf import fill_course

fill_course(
    brand="Baines Simmons",          # "Baines Simmons" | "Redline" | "Kenyon"
    course_name="Risk Management Workshop (RMW)",
    left_label="Upcoming Dates",
    left_dates=["13–17 April 2026"],
    right_dates=[],
    column_type="generic",           # "both" | "initial" | "recurrent" | "generic"
)
PYEOF
```

**For multiple courses in one run**, write all `fill_course(...)` calls into a single Python heredoc so PyMuPDF only loads once per brand template.

---

## Step 3: Confirm Output

Report back:
- Sub-brand generated
- Number of PDFs created
- Output subfolder path (e.g. `.../Course PDFs/Course - Baines Simmons/`)
- Any courses skipped (no dates found)

Then open the folder:
```bash
open "/Users/alexcraiu/Desktop/Claude Playground/Course PDFs/Course - [Brand]/"
```

---

## fill_course_pdf.py — Key Details

Defined constants (derived from BSL template inspection — adjust per brand if needed):

| Constant | Value | Notes |
|----------|-------|-------|
| `NAVY` | `(0.0, 0.075, 0.224)` | Full page background |
| `TITLE_COLOR` | `(204/255, 213/255, 1.0)` | Lavender-white used by template for title |
| `TITLE_RECT` | `Rect(68, 185, 1135, 320)` | Title text box area |
| `LEFT_PILL_ORIGIN` | `(164, 452)` | Baseline for left pill label text |
| `RIGHT_PILL_ORIGIN` | `(700, 452)` | Baseline for right pill label text |
| `DATES_Y_START` | `545` | Baseline y of first date row |
| `DATES_Y_STEP` | `80` | Vertical gap between date rows |
| `DATES_FONTSIZE` | `35` | Font size for date rows and pill labels |
| `FONT_FILE` | `OpenSans-VariableFont_wdth,wght.ttf` | Single variable font covers all weights |

**Title font sizing:** 65pt (≤55 chars) → 50pt (≤75 chars) → 40pt (longer).

**Single-column hiding:** covers `(620, 390, 1135, 720)` with navy — wipes right pill, right dates, and the gap between columns in one rectangle.

---

## Important Notes

- **Never modify the template.** `fitz.open(template)` reads it; `doc.save(output_path)` writes a new file. The template is never touched.
- **One page output.** PyMuPDF operates on a single page; there is no multi-artboard concept. Output is always one page.
- **Open Sans via variable font.** All inserted text uses `OpenSans-VariableFont_wdth,wght.ttf`. This is the only Open Sans file on the system; it covers all weights at a single path.
- **Cover then write.** For each editable region, draw a navy-filled rectangle first (to erase the template placeholder), then insert the new text on top.
- **Subfolder naming:** `Course - [Brand]/` — same prefix as the filename, without the course title.
- **Filename sanitisation:** `/\:*?"<>|` replaced with `-` in the course title portion only.
- **If Redline or Kenyon templates differ in layout**, re-inspect with PyMuPDF (`page.get_text("dict")`) to confirm bbox positions before adjusting `fill_course_pdf.py` constants.
