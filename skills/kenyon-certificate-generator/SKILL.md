---
name: kenyon-certificate-generator
description: Generate filled Kenyon certificate PDFs from the branded template. Use whenever asked to create, generate, or fill a Kenyon certificate of any type.
---

# Kenyon Certificate Generator

**Template:** burned into this skill — `Certificate - Kenyon - Template.pdf`  
**Font:** burned into this skill — `TitilliumWeb-Regular.ttf`  
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
| Membership | 5 | Name, Date (member since) |

The "Incident" field on Achievement replaces what the other types call "Course" — it is the crisis response event the recipient assisted with.

On Membership the date is not a presentation date. It sits under "A VALUABLE MEMBER SINCE", so it is the date the member joined.

---

## Step 1 — Ask the user for certificate type

Always ask first:

> "Which type of certificate? Training, Academy Training, Acceptance, Achievement, or Membership?"

---

## Step 2 — Collect any missing fields

Based on the type, confirm you have all required fields:

| Field | Required for |
|-------|-------------|
| **Name** | All types |
| **Date** | All types — e.g. "12th June 2026". On Membership, the member-since date. |
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
    cert_type="training",                    # "training" | "academy training" | "acceptance" | "achievement" | "membership"
    name="John Smith",
    date="12th June 2026",
    course_or_incident="Emergency Response Planning",  # omit or pass None for Acceptance and Membership
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

- **Only touch the Sapphire fill-in fields.** Name, Date, and Course/Incident are the only things that change. Every other element — "PROUDLY AWARDED TO", "FOR SUCCESSFULLY COMPLETING", "PRESENTED ON THIS DAY", "A VALUABLE MEMBER SINCE", signatures, signatory names/titles, the Kenyon seal, the logo, decorative lines, layout — must be left exactly where it is, untouched.
- **Template and font are burned in.** The script loads both from the skill directory — no need to re-upload either, and nothing depends on what is installed on the machine.
- **Font is Titillium Web Regular, not Open Sans.** This is a deliberate exception to the house Open Sans rule, same as the ASIP webinar skill: the certificate artwork sets its own fill-in fields in Titillium Web Regular, so filled text has to match it. `TitilliumWeb-Regular.ttf` ships inside this skill and is embedded into every generated PDF. It is SIL Open Font License 1.1 (http://scripts.sil.org/OFL), so redistributing it inside the skill is fine. Do not switch this back to Open Sans.
- **Field positions are read from the template at runtime.** The script finds the fill-in fields by their Titillium Web Regular styling, so a redesigned template drops in without code changes. If a future template sets the placeholders in a different font, the script raises an error rather than filling the wrong spot.
- **Date format:** accepts any string with an ordinal suffix (`st`, `nd`, `rd`, `th`). The ordinal is rendered as a superscript matching the template's own. Dates without ordinals are inserted as plain text, which suits Membership if only a year is given.
- **Name font sizing:** auto-scales from the template's size (34pt) down so any length name fits.
- **Course / Incident font sizing:** auto-scales from 24pt down.
- **Single-page output:** only the relevant certificate page is saved, not all 5 template pages.
- **Never modify the template.** The script reads it and saves a new file.

---

## Replacing the template

When new artwork arrives, merge the pages into a single `Certificate - Kenyon - Template.pdf` in this exact order, then overwrite the file in both this directory and `/Users/alexcraiu/Desktop/Claude Playground/skills/kenyon-certificate-generator/`:

1. Training
2. Academy Training
3. Acceptance
4. Achievement
5. Membership

Keep the fill-in placeholders live text in Titillium Web Regular, and keep every other element in a different font, or the script cannot tell them apart. No other change is needed — positions, sizes and the superscript offset are all read back from the new file.

If a future template moves the fill-in fields to a different typeface, bundle that font file alongside the template and update `PLACEHOLDER_FONT` and `FONT_FILE` in `fill_certificate.py` together. Never point `FONT_FILE` at `/Users/alexcraiu/Library/Fonts/` — the font must travel with the skill.
