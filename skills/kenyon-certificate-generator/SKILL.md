---
name: kenyon-certificate-generator
description: Generate filled Kenyon certificate PDFs from the branded template. Use whenever asked to create, generate, or fill a Kenyon certificate of any type.
---

# Kenyon Certificate Generator

**Template:** burned into this skill — `Certificate - Kenyon - Template.pdf`  
**Script:** `fill_certificate.py` (in this skill directory)  
**Output:** `~/Desktop/Certificate - Kenyon - [type] - [Name].pdf`  
**Can run in browser:** Yes — Python + PyMuPDF only, no desktop apps needed.

---

## Certificate Types & Required Fields

| Type | Page | Fields |
|------|------|--------|
| Training | 1 | Name, Date, Course |
| Academy Training | 2 | Name, Date, Course |
| Acceptance | 3 | Name, Date |
| Achievement | 4 | Name, Date, Incident |

The "Incident" field on Achievement replaces what the other types call "Course" — it is the crisis response event the recipient assisted with.

---

## Step 1 — Ask the user for certificate type

Always ask first:

> "Which type of certificate? Training, Academy Training, Acceptance, or Achievement?"

---

## Step 2 — Collect any missing fields

Based on the type, confirm you have all required fields:

| Field | Required for |
|-------|-------------|
| **Name** | All types |
| **Date** | All types — e.g. "12th June 2026" |
| **Course** | Training, Academy Training |
| **Incident** | Achievement |

If any required field is missing, ask for it before running the script.

---

## Step 3 — Run the script

```bash
python3 - << 'PYEOF'
import sys
sys.path.insert(0, "/Users/alexcraiu/.claude/skills/kenyon-certificate-generator")
from fill_certificate import fill_certificate

output = fill_certificate(
    cert_type="training",                    # "training" | "academy training" | "acceptance" | "achievement"
    name="John Smith",
    date="12th June 2026",
    course_or_incident="Emergency Response Planning",  # omit or pass None for Acceptance
)
print(output)
PYEOF
```

---

## Step 4 — Deliver the output

**Desktop CLI (`claude` terminal or IDE extension):**
```bash
open "<output path from script>"
```
Report the Desktop path to the user.

**Browser-based Claude (claude.ai/code):**
Do NOT save to `~/Desktop` and do NOT auto-download. Instead:
1. Pass a temp path to the script, e.g. `/tmp/Certificate - Kenyon - [type] - [Name].pdf`
2. After the script runs, use the `Read` tool on that path — the PDF renders visually inside the chat.
3. Tell the user the certificate is shown above and they can download it from the chat if it looks correct.

To detect which environment you are in: if you have access to the user's local filesystem (e.g. `~/Desktop` resolves to a real Mac path) you are on desktop. If not, use the temp path + Read approach.

---

## Important Notes

- **Only touch the three Sapphire fields.** Name, Date, and Course/Incident are the only things that change. Every other element — "PROUDLY AWARDED TO", "FOR SUCCESSFULLY COMPLETING", "PRESENTED ON THIS DAY", signatures, signatory names/titles, the Kenyon seal, the logo, decorative lines, layout — must be left exactly where it is, untouched.
- **Template is burned in.** The script loads it from the skill directory — no need to re-upload it.
- **Date format:** accepts any string with an ordinal suffix (`st`, `nd`, `rd`, `th`). The ordinal is rendered as a superscript to match the template. Dates without ordinals are inserted as plain text.
- **Name font sizing:** auto-scales from 34pt down so any length name fits.
- **Course / Incident font sizing:** auto-scales from 24pt down.
- **Single-page output:** only the relevant certificate page is saved, not all 4 template pages.
- **Never modify the template.** The script reads it and saves a new file.
