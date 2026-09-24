---
name: kenyon-certificate-generator
description: Generate filled Kenyon certificate PDFs from the branded template. Use whenever asked to create, generate, or fill a Kenyon certificate of any type, or for the editable Word version of the Kenyon Membership certificate.
---

# Kenyon Certificate Generator

**Output rule:** every file this skill produces is shared into the chat, and the user downloads it from there. Nothing is ever saved to the user's own folders (Desktop, Documents, Downloads, the working directory).  
**Runs anywhere:** Python + PyMuPDF only. No desktop apps, and no paths tied to one person's machine.

Everything the skill needs is embedded in this folder:

| File | What it is |
|------|------------|
| `Certificate - Kenyon - Template.pdf` | The 5-page certificate artwork, one page per type |
| `Certificate - Kenyon - Membership - Word Template.docx` | Editable Word version of the Membership certificate |
| `TitilliumWeb-Regular.ttf` | The font the fill-in fields are set in |
| `fill_certificate.py` | Generates the certificates |
| `build_word_template.py` | Maintenance only: rebuilds the Word template after the artwork changes |

---

## Certificate Types & Required Fields

| Type | Page | Fields |
|------|------|--------|
| Training | 1 | Name, Date, Course |
| Academy Training | 2 | Name, Date, Course |
| Acceptance | 3 | Name, Date |
| Achievement | 4 | Name, Date, Incident |
| Membership | 5 | Name, Date (member since) |

The "Incident" field on Achievement replaces what the other types call "Course". It is the crisis response event the recipient assisted with.

On Membership the date is not a presentation date. It sits under "A VALUABLE MEMBER SINCE", so it is the date the member joined.

---

## Step 1: Ask the user for certificate type

Always ask first:

> "Which type of certificate? Training, Academy Training, Acceptance, Achievement, or Membership?"

If the user wants an **editable Word version** rather than a finished PDF, go to "Word version" below instead.

---

## Step 2: Collect any missing fields

Based on the type, confirm you have all required fields:

| Field | Required for |
|-------|-------------|
| **Name** | All types |
| **Date** | All types, e.g. "12th June 2026". On Membership, the member-since date. |
| **Course** | Training, Academy Training |
| **Incident** | Achievement |

If any required field is missing, ask for it before running the script.

---

## Step 3: Run the script

`<skill_dir>` is the directory this SKILL.md is in. Claude Code states it as "Base directory for this skill" when the skill loads; on claude.ai it sits under `/mnt/skills/`. **Never hardcode a `/Users/...` path.** This skill is shared, and that path does not exist on anyone else's machine. If you cannot tell where the skill lives, find it:

```bash
find / -name fill_certificate.py -path "*kenyon-certificate-generator*" 2>/dev/null | head -1
```

Then run it from any working directory:

```bash
python3 "<skill_dir>/fill_certificate.py" \
  --type membership \
  --name "John Smith" \
  --date "12th June 2026"
# add --course "..." for Training / Academy Training
# add --incident "..." for Achievement
```

It prints two paths:

```
PDF: .../Certificate - Kenyon - membership - John Smith.pdf
PREVIEW: .../Certificate - Kenyon - membership - John Smith - preview.png
```

The script chooses where to write, and there is no option to change it. It uses claude.ai's outputs folder (`/mnt/user-data/outputs/`) when that exists, and otherwise a temporary folder. Either way the file is only a staging copy for sharing into the chat. A second certificate with the same name gets ` (2)` added, so nothing the user has not downloaded yet is overwritten.

**If the script stops with `ERROR:`,** tell the user what it says and fix the input, do not work around it:

- *characters the certificate font cannot print*: the name (or course/incident) uses an alphabet Titillium Web does not cover, such as Greek, Cyrillic, Arabic or Chinese. Ask the user for a Latin-alphabet spelling. Never swap in another font, which would break the brand.
- *needs the course / incident field*, *name is empty*, *date is empty*: ask for the missing detail.
- *PyMuPDF is not installed*: run `pip install pymupdf` (add `--break-system-packages` if pip refuses), then rerun.

---

## Step 4: Show the certificate in the chat, before anything else

The user must see the finished certificate inside the conversation and download it from there. A path on disk is not delivery: the person may be in a sandbox, on a different machine, or in a browser, where that path means nothing to them.

1. **Check it yourself first.** Open the PREVIEW PNG with your file-reading tool and confirm the name, date and course/incident are correct and nothing else on the page has moved. Viewing a file this way shows it to you only, not to the user, so it does not count as delivery.
2. **Share both files with the user**, using whichever file-sharing tool this environment gives you:
   - Claude Code desktop app: `SendUserFile`. PNG preview with `display: "render"` so it appears inline, PDF with `display: "attach"` so it can be downloaded.
   - claude.ai: present both files from `/mnt/user-data/outputs/` with the file-presenting tool (e.g. `present_files`).
   - Anywhere else: use the tool that attaches or presents files to the user.

   Always send the PNG as well as the PDF. Some chats cannot preview a PDF inline, but every chat can show an image.
3. **Tell the user to download the PDF from the chat.** Do not mention where the staging copy sits, and never copy, move, or open the file into the user's own folders, Preview, or any other app. If they ask for it in a folder, point them to the download in the chat.
4. **No file-sharing tool at all** (e.g. a plain terminal session)? Say plainly that this environment cannot put files in the chat, give the staging path so they can retrieve it, and never claim the certificate is showing in the chat when it is not.

---

## Word version (Membership only)

When the user asks for an editable Word version of the Membership certificate:

```bash
python3 "<skill_dir>/fill_certificate.py" --word-template
# prints: DOCX: .../Certificate - Kenyon - Membership - Word Template.docx
```

Share that DOCX through the chat exactly as in Step 4 (attach it; there is no preview PNG for this one). Tell them to click the blue placeholders and type over them, and that Titillium Web must be installed on the computer that opens it. Only Membership has a Word version so far. For any other type, say so and offer the PDF.

---

## Important Notes

- **Only touch the Sapphire fill-in fields.** Name, Date, and Course/Incident are the only things that change. Every other element ("PROUDLY AWARDED TO", "FOR SUCCESSFULLY COMPLETING", "PRESENTED ON THIS DAY", "A VALUABLE MEMBER SINCE", signatures, signatory names and titles, the Kenyon seal, the logo, underline rules, line patterns, layout) must be left exactly as it is. The placeholders are removed without painting anything over them, so the artwork behind each field stays intact.
- **Templates and font are embedded.** The script loads everything from its own folder, so nothing depends on what is installed on the machine and nothing needs re-uploading.
- **Font is Titillium Web Regular, not Open Sans.** This is a deliberate exception to the house Open Sans rule, same as the ASIP webinar skill: the certificate artwork sets its own fill-in fields in Titillium Web Regular, so filled text has to match it. `TitilliumWeb-Regular.ttf` ships inside this skill and is embedded into every generated PDF. It covers Latin alphabets only (including accents, Polish, Turkish, Romanian and Vietnamese). It is SIL Open Font License 1.1 (http://scripts.sil.org/OFL), so redistributing it inside the skill is fine. Do not switch this back to Open Sans.
- **Field positions are read from the template at runtime.** The script finds the fill-in fields by their Titillium Web Regular styling, so a redesigned template drops in without code changes. If a future template sets the placeholders in a different font, the script raises an error rather than filling the wrong spot.
- **Date format:** accepts any string with an ordinal suffix (`st`, `nd`, `rd`, `th`). The ordinal is rendered as a superscript matching the template's own. Dates without ordinals are inserted as plain text, which suits Membership if only a year is given.
- **Type names are forgiving:** `academy training`, `Academy_Training` and `academy-training` all work.
- **Name font sizing:** auto-scales from the template's size (34pt) down so any length name fits.
- **Course / Incident font sizing:** auto-scales from 24pt down.
- **Single-page output:** only the relevant certificate page is saved, not all 5 template pages.
- **Never modify the templates** while generating. The script reads them and writes new files.

---

## Replacing the template

When new artwork arrives, merge the pages into a single `Certificate - Kenyon - Template.pdf` in this exact order, then overwrite the file in both `~/.claude/skills/kenyon-certificate-generator/` and the `skills/kenyon-certificate-generator/` folder of the Branding repo:

1. Training
2. Academy Training
3. Acceptance
4. Achievement
5. Membership

Keep the fill-in placeholders live text in Titillium Web Regular, and keep every other element in a different font, or the script cannot tell them apart. No other code change is needed: positions, sizes and the superscript offset are all read back from the new file.

Then rebuild the Word template so it matches the new artwork (needs `pip install python-docx`):

```bash
python3 "<skill_dir>/build_word_template.py"
```

If a future template moves the fill-in fields to a different typeface, bundle that font file alongside the template and update `PLACEHOLDER_FONT` and `FONT_FILE` in `fill_certificate.py` together. Never point `FONT_FILE` at a system fonts folder: the font must travel with the skill.

After any change, rebuild `kenyon-certificate-generator.zip` so the claude.ai copy can be re-uploaded.
