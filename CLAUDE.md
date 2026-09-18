# TrustFlight Branding — Claude Workspace

**Owner:** Alex Craiu, Branding & Visual Designer, TrustFlight  
**Repo:** `tf-alexc/Branding`  
**Working directory (local CLI):** `/Users/alexcraiu/Desktop/Claude Playground/`

This repo contains TrustFlight brand assets, automation scripts, and Claude skill definitions used to generate branded collateral. Most skills drive desktop applications (Illustrator, InDesign, PowerPoint, Word) and require the local CLI. Skills that only involve Python scripts or web fetching can run in the browser.

---

## Brand Rules (always apply)

- Never use em dashes. Use a comma, colon, or rewrite the sentence.
- "Visit our website" always means `https://www.trustflight.com`
- Font: Open Sans throughout — never Arial, Aptos, or Lato.
- All generated PowerPoint files save to `/Users/alexcraiu/Desktop/Claude Playground/Claude Presentations/`
- Word docs: always override the original file, never create a versioned copy.
- Images in presentations must be cropped inside a rounded rectangle with an Azure (`#479FF8`) 1pt outline.
- Pull photography from SharePoint `Photography/` folder — JPGs with `-lr` in the filename only, never PSDs.

For full brand voice, messaging, and visual identity: see `skills/brand-framework/SKILL.md` and `skills/brand-framework/BRAND-GUIDELINES.md`.

---

## Skills

All skill definitions live in `skills/`. Each folder contains a `SKILL.md` with the full operating procedure.

### `brand-framework` — Brand voice and identity
Reference for any copy, messaging, or design decisions. Covers the four capability pillars (Centrik, TechLog, SmartSuite, Baines Simmons), tone of voice, boilerplate, and visual identity.  
**Can run in browser:** Yes (reference only — no tool calls needed).

---

### `ppt-design-system` — PowerPoint presentations
Build or restyle PowerPoint decks to TrustFlight brand standards.  
**Template:** `skills/ppt-design-system/Master Presentation Template - v2.pptx`  
**Brand tokens:** `skills/ppt-design-system/brand.json`  
**Trigger:** any request for a deck, slides, pitch, or presentation.  
**Can run in browser:** Partially (Python/python-pptx script runs anywhere; MCP server for reading slide info is local-only).

Key rules:
- Always build from the master template — never a blank file.
- Use first (shorter) agenda slide variant.
- Keep footer + page number on all slides except cover and end slide.
- MCP `keep_slides`, `delete_slide`, `clone_slide` are broken — use python-pptx directly for structural changes.
- Strip SharePoint/OMEX artefacts on every save using the `clean_and_save()` pattern in the SKILL.md.

---

### `linkedin-ad-generator` — LinkedIn ad graphics
Generate JPG ads from the Illustrator Ads template. Layouts 01, 02, 03 — each produces a square and wide artboard.  
**Template:** `Illustrator Templates/Ads - Template.ai`  
**Export root:** SharePoint `[ORG]-Design - Documents/Graphics - Blog & Social Media/Ad Campaigns/`  
**Can run in browser:** No — requires local Illustrator MCP.

---

### `linkedin-holiday-generator` — LinkedIn holiday posts
Generate holiday post graphics from the Illustrator Holidays template. One artboard per holiday — duplicate master, edit, export, keep master intact.  
**Template:** `Illustrator Templates/Holidays - Template.ai`  
**Export root:** SharePoint `[ORG]-Design - Documents/Graphics - Blog & Social Media/Holidays/`  
**Can run in browser:** No — requires local Illustrator MCP.

Key rules:
- Set CAPTION text on master before duplicating (so copy inherits it).
- New artboards go to the right of the last artboard with a 40px gap.
- Always open Illustrator + template at the start of every run (`open` + `sleep 5`).
- CAPTION font size: loop 160pt → 85pt (step -5pt); 85pt is the floor, not the target.
- Always save the document after the final export.

---

### `linkedin-event-generator` — LinkedIn event graphics
Generate event announcement graphics from the Events Generator Illustrator template. Pulls event data from the events API.  
**Template:** `Illustrator Templates/Events Generator.ai`  
**Events API:** `https://p01--events-tracker--xzp2zkf8b975.code.run/api/events`  
**Export root:** `Events Generated/`  
**Can run in browser:** No — requires local Illustrator MCP.

Key rules:
- 2+ attendees for the same event go in one artboard, not separate files.
- Use full attendee title verbatim — no truncation.

---

### `bsl-course-sheets` — Baines Simmons course sheet PDFs
Fill branded course sheet PDFs from source BSL documents. 70+ courses across 5 pathways.  
**Script:** `InDesign/BSL Course Sheets/fill_course_sheet.py`  
**Templates:** `InDesign/BSL Course Sheets/Course - [Pathway] - Template.pdf`  
**Source PDFs:** `/Users/alexcraiu/Desktop/Documents/Baines Simmons/Course Sheets/CURRENT PDF VERSIONS/`  
**Output:** `InDesign/BSL Course Sheets/Output/`  
**Can run in browser:** No — source PDFs are local.

---

### `course-dates-generator` — Sub-brand course date PDFs
Scrape a course listing page and generate branded course date PDFs for Redline, BSL, or Kenyon.  
**Script:** `skills/course-dates-generator/fill_course_pdf.py`  
**Templates:** `Course PDFs/Courses - [Brand] - Template.pdf`  
**Can run in browser:** Yes — uses WebFetch + Python/PyMuPDF, no local apps needed.

Key rules:
- Course titles with ` - ` separator: prefix on line 1, subtitle on following lines.

---

### `word-brand` — Word document branding
Restyle any Word document to TrustFlight brand standards using the master template.  
**Script:** `skills/word-brand/word_brand.py`  
**Master template:** `/Users/alexcraiu/Desktop/Documents/Word templates/Basic Document.docx`  
**Can run in browser:** No — master template is local.

---

### `kenyon-certificate-generator` — Kenyon certificate PDFs
Fill the branded Kenyon certificate template with recipient details and export a single-page PDF.  
**Script:** `skills/kenyon-certificate-generator/fill_certificate.py`  
**Template:** `skills/kenyon-certificate-generator/Certificate - Kenyon - Template.pdf` (burned in — no upload needed)  
**Font:** `skills/kenyon-certificate-generator/TitilliumWeb-Regular.ttf` (burned in). Deliberate exception to the Open Sans rule: the certificate artwork sets its fill-in fields in Titillium Web Regular, so filled text must match.  
**Output:** `~/Desktop/Certificate - Kenyon - [type] - [Name].pdf`  
**Can run in browser:** Yes — Python + PyMuPDF only, no desktop apps needed.

Five types: Training (page 1), Academy Training (page 2), Acceptance (page 3, no course field), Achievement (page 4, Incident field instead of Course), Membership (page 5, no course field, the date is the member-since date).  
Always ask the user for the certificate type before proceeding.

---

### `asip-webinar-generator` — ASIP webinar & blog promo graphics
Fill the Webinar PDF template with an eyebrow/subtitle and title, export as JPG.  
**Script:** `skills/asip-webinar-generator/fill_webinar.py`  
**Template:** `skills/asip-webinar-generator/Webinar - Template.pdf` (burned in — no upload needed, 9 pages: 3 TrustFlight webinar/purple + 3 TrustFlight blog/green + 3 Kenyon, one per size each)  
**Output:** `Webinar Generated/`  
**Can run in browser:** Yes — Python + PyMuPDF only, no desktop apps needed.

Always ask the user, unless already specified: (1) which brand — Kenyon or TrustFlight (Baines Simmons and Redline will follow); if the user instead gives a link to an existing article or reference doc, detect the brand from it automatically rather than asking; (2) for TrustFlight only, webinar or blog/article — picks the purple "WEBINAR SERIES"/"REGISTER NOW" theme or the green "BLOG SERIES"/"READ THE FULL ARTICLE" theme (Kenyon currently only has one style, its own blog/article layout — don't ask this for Kenyon); (3) which size(s): 1920x1080 (website article thumbnail, no CTA button in this template), 1200x628 (LinkedIn wide ad), 1200x1200 (LinkedIn square ad).

Key rules:
- Only the eyebrow/subtitle and title fields ever change. Never move, resize, or alter any other visual element. Same rule applies across every brand and theme.
- Fonts are a deliberate exception to the Open Sans brand rule: Titillium Web Bold (eyebrow, Electric `#03D4FF`) and Titillium Web Light (title, White) — fixed per this template's own spec.
- Optional background photo, sourced from Unsplash/Pexels (needs `UNSPLASH_ACCESS_KEY` and/or `PEXELS_API_KEY` env vars): always blurred, always cover-fit, always tinted by the chosen brand/theme's own gradient at ~10% opacity so pills/button/logo/lines/text stay exactly as designed on top of it. Ask for a search keyword; never guess one from the title.

---

## File Structure

```
Claude Playground/
├── skills/                        # Claude skill definitions (mirrored from ~/.claude/skills)
│   ├── brand-framework/           # Brand voice, messaging, visual identity
│   ├── ppt-design-system/         # PowerPoint automation + master template
│   ├── linkedin-ad-generator/     # LinkedIn ad Illustrator workflow
│   ├── linkedin-holiday-generator/# Holiday post Illustrator workflow
│   ├── linkedin-event-generator/  # Event graphic Illustrator workflow
│   ├── bsl-course-sheets/         # BSL PDF automation
│   ├── course-dates-generator/    # Course dates PDF automation
│   ├── kenyon-certificate-generator/ # Kenyon certificate PDF generator
│   ├── word-brand/                # Word document branding
│   └── asip-webinar-generator/    # ASIP webinar promo graphic generator
├── Illustrator Templates/         # Master .ai files for Illustrator skills
├── InDesign/
│   ├── BSL Course Sheets/         # Templates, script, fonts, output PDFs
│   └── indesign-mcp/              # Local InDesign MCP server
├── Course PDFs/                   # Course date PDF templates (Redline, BSL, Kenyon)
├── PDF Templates/                 # PDF templates for other PyMuPDF-driven skills (webinar, whitepaper, socials)
├── Claude Presentations/          # All generated PowerPoint files
├── Events Generated/              # Exported event graphic JPGs
├── Webinar Generated/             # Exported ASIP webinar graphic JPGs
├── fill_course_pdf.py             # Course dates script (root copy)
└── CLAUDE.md                      # This file
```

---

## Local vs Browser

| Skill | Browser | CLI |
|-------|---------|-----|
| brand-framework (reference) | Yes | Yes |
| ppt-design-system | Partial | Yes |
| course-dates-generator | Yes | Yes |
| linkedin-ad-generator | No | Yes |
| linkedin-holiday-generator | No | Yes |
| linkedin-event-generator | No | Yes |
| bsl-course-sheets | No | Yes |
| kenyon-certificate-generator | Yes | Yes |
| word-brand | No | Yes |
| asip-webinar-generator | Yes | Yes |

Skills marked "No" require desktop apps (Illustrator, InDesign, PowerPoint, Word) running locally via MCP.
