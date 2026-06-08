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

### `carousel-builder` — LinkedIn carousel PDFs
Summarise an article or brief into a short LinkedIn carousel (max 6 slides, intro and outro included) using a brand-specific PDF template. Templates share structure across brands — only logo and footer URLs differ.  
**Templates:** `skills/carousel-builder/Carousel - [Brand] - Template.pdf` (bundled with the skill — all four brands live: Baines Simmons, Redline, Kenyon, TrustFlight). Blog image companion template (`Blog Image - Template.pdf`) is also bundled with the skill, one page per brand.  
**Output:** `Carousel PDFs/Carousel - [Brand]/`  
**Trigger:** "carousel", "LinkedIn carousel", "multi-page LinkedIn post", or similar.  
**Can run in browser:** Yes — uses WebFetch + Python/PyMuPDF, no local apps needed.

Key rules:
- Max 6 slides total, intro and outro included.
- If the template is shorter than the needed page count, duplicate one of the inner content pages at random (never the intro or outro).
- Output must look identical to the template — only text changes.
- Always generates a matching blog post image (JPG) alongside the carousel PDF — no opt-in, blog description capped at 2 lines.
- All four brand templates (Baines Simmons, Redline, Kenyon, TrustFlight) are live and bundled with the skill.

---

### `word-brand` — Word document branding
Restyle any Word document to TrustFlight brand standards using the master template.  
**Script:** `skills/word-brand/word_brand.py`  
**Master template:** `/Users/alexcraiu/Desktop/Documents/Word templates/Basic Document.docx`  
**Can run in browser:** No — master template is local.

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
│   ├── carousel-builder/          # LinkedIn carousel PDF automation
│   └── word-brand/                # Word document branding
├── Illustrator Templates/         # Master .ai files for Illustrator skills
├── InDesign/
│   ├── BSL Course Sheets/         # Templates, script, fonts, output PDFs
│   └── indesign-mcp/              # Local InDesign MCP server
├── Course PDFs/                   # Course date PDF templates (Redline, BSL, Kenyon)
├── Carousel PDFs/                 # Generated LinkedIn carousel PDFs (templates live inside the skill)
├── Claude Presentations/          # All generated PowerPoint files
├── Events Generated/              # Exported event graphic JPGs
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
| carousel-builder | Yes | Yes |
| linkedin-ad-generator | No | Yes |
| linkedin-holiday-generator | No | Yes |
| linkedin-event-generator | No | Yes |
| bsl-course-sheets | No | Yes |
| word-brand | No | Yes |

Skills marked "No" require desktop apps (Illustrator, InDesign, PowerPoint, Word) running locally via MCP.
