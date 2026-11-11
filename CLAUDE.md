# TrustFlight Branding — Claude Workspace

**Owner:** Alex Craiu, Branding & Visual Designer, TrustFlight  
**Repo:** `tf-alexc/Branding`  
**Working directory (local CLI):** `/Users/alexcraiu/Desktop/Claude Playground/`

This repo contains TrustFlight brand assets, automation scripts, and Claude skill definitions used to generate branded collateral. Most skills drive desktop applications (Illustrator, InDesign, PowerPoint, Word) and require the local CLI. Skills that only involve Python scripts or web fetching can run in the browser.

---

## Writing Style: No AI Artefacts (ALWAYS APPLY)

Write like a competent human colleague, not a chatbot. These rules apply to every output: chat replies, documents, emails, code comments, commit messages and published content.

### Punctuation and formatting
- Never use em dashes (—). Use a hyphen, colon, comma or full stop, or restructure the sentence.
- No emojis unless explicitly asked.
- Don't over-format. Use headers and bullets only when the content is a genuine list or reference material. Default to plain paragraphs.
- No bold for emphasis scattered through prose. Bold is for labels only.
- Use sentence case for headings, not Title Case.

### Banned words and phrases
- Vocabulary: delve, leverage, utilise, robust, seamless, cutting-edge, game-changer, unlock, empower, elevate, harness, tapestry, landscape, realm, journey, navigate (when not literal), foster, bolster, pivotal, crucial, vital, meticulous, comprehensive, holistic, synergy, streamline, testament, underscore, embark.
- Openers: "Great question", "Certainly!", "Absolutely!", "I'd be happy to", "Let's dive in", "In today's fast-paced world", "In the ever-evolving...".
- Closers: "I hope this helps", "Let me know if you have any other questions", "Feel free to reach out", "Happy to help further".
- Filler: "It's worth noting that", "It's important to remember", "At the end of the day", "When it comes to", "In order to" (use "to").

### Sentence patterns to avoid
- "It's not just X, it's Y" and "This isn't about X, it's about Y" constructions.
- Reflexive groups of three ("fast, simple, and secure"). Use as many items as are actually true.
- Rhetorical questions followed by the answer ("The result? A 30% saving.").
- Summary sentences that restate the paragraph you just wrote. No "In conclusion" or "Overall".
- Hedging stacks ("may potentially help to possibly improve"). State it, or state the uncertainty once.
- Fake enthusiasm and hype adjectives. Let facts carry the weight.

### No mannered prose
Don't substitute metaphor or flourish for a direct statement. Write "a parameter worth changing", not "a dial worth turning". Write "this still matters", not "this earns its keep". When a literal phrase is available, use it. Metaphors add connotations you didn't choose and make the reader work harder.

### What to do instead
- Lead with the answer or the point. Context after, if needed.
- Use short, plain words and specific nouns and numbers.
- Vary sentence length naturally.
- Cut any sentence that doesn't add information.
- Before finishing, reread the output and remove anything on the lists above.

---

## Brand Rules (always apply)

- Writing style: follow the "No AI Artefacts" section above for all copy.
- "Visit our website" always means `https://www.trustflight.com`
- Font: Open Sans throughout — never Arial, Aptos, or Lato.
- Logos: the horizontal anniversary lockup comes first wherever a brand has one, above all for Kenyon (`kenyon-120-logo-rgb.svg` / `-white.svg`; the standard Kenyon logo only when asked). Brands without one use their default horizontal logo. Never use a stacked logo unless it is asked for by name.
- Kenyon sidebars: wherever a design has a sidebar or side rail (whitepaper, deck, booklet, etc.) and it is for Kenyon, the logo at the top of the sidebar is the Kenyon globe mark only (`kenyon-globe-white.svg` on dark, `kenyon-globe-rgb.svg` on light). No wordmark, horizontal, anniversary or stacked logo there.
- Gradients: new graphics never use the dark brand gradient (Midnight to near-black, `#010306` to `#083976`); use solid Midnight or a photo. Keep the gradient in the design system; never delete it.
- Carousels: a new carousel starts from the tall format (1200x1600), never square, unless square is asked for.
- Every artifact follows the brand, however basic (notes, a one-pager, a table, a simple page): at minimum Titillium Web headings and Open Sans body text loaded from the design system, and brand colours.
- All generated PowerPoint files save to `/Users/alexcraiu/Desktop/Claude Playground/Claude Presentations/`
- Word docs: always override the original file, never create a versioned copy.
- Images in presentations must be cropped inside a rounded rectangle with an Azure (`#479FF8`) 1pt outline.
- Pull photography from SharePoint `Photography/` folder — JPGs with `-lr` in the filename only, never PSDs.
- Photos fetched from the web come only from Unsplash or Pexels, under their free licences (never Unsplash+ or other paid images). Never use Wikipedia or Wikimedia Commons.
- Decks: any request for a deck, presentation, slides or pitch creates a new artifact from the Slides type (https://claude.ai/artifact/8jTsAFQMFDb2oA8MsPJ2eL), styled on the brand's deck template, so it shows under Slides in the Design section. Use `ppt-design-system` for a .pptx file only when PowerPoint or .pptx is asked for.
- Documents: a proposal template is the base only when the document is a proposal (proposal, bid, tender, RFP response, quote turned into a proposal). Any other document never starts from or borrows from a proposal template, even when its brand has one.
- Documents: build the artifact first and share it, then ask at the end whether a PDF is needed (unless the request asked for one).
- PDFs: before sharing, run the design system's `assets/scripts/pdf-check.md` and look at every rendered page. No pink or magenta casts: no transparency, opacity, filters, blend modes or box-shadows on the page, and every image converted to 8-bit sRGB JPEG or PNG first.

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
**Trigger:** a request for a PowerPoint or .pptx file, or to restyle an existing .pptx. Any other deck request is a Slides artifact (see Brand Rules).  
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
**Word template:** `skills/kenyon-certificate-generator/Certificate - Kenyon - Membership - Word Template.docx` (burned in; rebuild with `build_word_template.py` after any artwork change).  
**Output:** PDF + PNG preview, shared into the chat for the user to download, with the same result on every surface (claude.ai in a browser; desktop app Chat, Cowork and Code): preview in the conversation, PDF attached, the script's CAPTION line as the message. Never saved to the user's own folders: the script only writes to the conversation's outputs folder or a temporary staging folder, and `--deliver-to` only accepts an `outputs` folder outside the user's home.  
**Can run in browser:** Yes — Python + PyMuPDF only, no desktop apps needed. Script paths resolve from its own folder, so it runs on anyone's machine.

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

## Master Brand System design system

The live design system is the artifact https://claude.ai/artifact/3TSvubnBz4WCsS1xD7o3b9; its README's Template routing table links every template's Design canvas.

### Baines Simmons proposal template
15 fixed US Letter pages, no controls. Rebrand-from-Word workflow in `PROCESS.md`.  
**Live:** `templates/proposal-baines-simmons/Page01.dc.html` to `Page15.dc.html` in the design system; Design canvas https://claude.ai/artifact/6bZKWgjxJcqrdnzYxbD95z  
**Local mirror:** `Master Brand System/` (same paths, renders and exports locally; see its README)  
**Rules:** `Master Brand System/assets/docs/templates/proposal-baines-simmons/PROCESS.md` and `CLAUDE-CODE-RULES.md`

Key rules:
- Fonts always load from the design system (`styles.css` / `tokens.css` / `fonts/`), never a template-only copy.
- Never use `doc-page.js` or any print script that re-renders pages: Chrome then writes Type 3 glyph outlines, the spacing breaks and Acrobat crawls. Check every PDF lists only OpenSans-* and TitilliumWeb-* fonts.
- The contents page entries are links (`PageNN.dc.html` on pages and the canvas, `#pNN` in the print copy).

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
├── Master Brand System/           # Local mirror of design-system files (Baines Simmons proposal)
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
