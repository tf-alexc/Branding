# Baines Simmons proposal template – rules for Claude Code

These are the template's hard rules plus the global brand and export rules it depends on. The process of record is `PROCESS.md` in this folder; read both before editing, filling or exporting the template.

## Where the files live
Template files (Master Brand System, `templates/proposal-baines-simmons/`): 15 Design Component pages, one file per sheet, `Page01.dc.html` (cover) to `Page15.dc.html` (back cover), each a fixed US Letter page (816×1056px). Print copy for local PDF export: `Baines Simmons - Proposal - Commercial Proposal -print-.html`, generated from the 15 pages. Design canvas: [Baines Simmons Proposal](https://claude.ai/artifact/6bZKWgjxJcqrdnzYxbD95z), the same 15 pages as artboards (`Main.dc.html` is page 1). Built from the Intermountain Health proposal (OP10663 V2.0).
- Rules: `assets/docs/templates/proposal-baines-simmons/PROCESS.md` (process of record) and this file.
- Shared files the pages read: `styles.css` (imports `tokens.css` and `components/bundle.css`), `fonts/*.woff2`, `assets/logos/baines-logo-white.svg`, `assets/logos/trustflight-logo-horizontal-white.svg`, `assets/logos/trustflight-icon-blue.svg`.
- The 21 older per-page files in `templates/proposal-baines-simmons/` (`Baines Simmons - Proposal - <Section>.html`) are the previous layout. Do not use them for new proposals.

Page stack: 01 cover · 02 contents · 03–04 description · 05–07 proposal details (tranche + MSA pricing tables) · 08 project summary · 09–10 associated costs, payment terms, additional information · 11 acceptance · 12–14 Terms of Agreement · 15 back cover.

## Hard rules (template)
1. **Terms of Agreement (pp 12–14) are locked.** Never change, reword, reorder or "fix" any clause, typos included. Header/footer only. Single full-width column (8.5pt / 1.4) flowing across three pages in clause order (5.3 opens p13). If it reflows, re-balance by moving whole paragraphs between pages, never by editing text or shrinking type. Clause subheadings: 12px above, 2px below. Sub-clause numbers (1.1, 5.3, 9.1…) are bold Midnight.
2. **Deal code in every footer.** Take the OPxxxxx code and version from the quote filename (e.g. `OP10663_IMHFAS_Quote_V2.0` → `OP10663`, `V2.0`). Footer reads "Proposal [code] · [version]" on every inner page (every page except the cover and back cover, the contents page included), with no "Baines Simmons Limited" prefix. Never ship with the `[OP00000]` placeholder.
3. **Acceptance (p11) and back cover/contact page (p15) are locked:** exact layout and content. Do not change acceptance copy, signature fields or the purchase-order table.
4. **Acceptance labels** (Name (Print), Position, Authorised Signature, Date, Purchase Order Number) are sapphire at 9pt, the same size as the a)/b)/c) body lines. Never shrink them.
5. **Cover pill** always ends with the fixed word "Proposal"; the proposal type is the word(s) before it (default "Commercial" → "COMMERCIAL PROPOSAL"). No trailing hyphen after the client name on the cover.
6. **Cover photo placeholder** matches the original TrustFlight proposal: Sapphire→Midnight gradient, faint diagonal stripes, "[Placeholder Photo]". It flexes to fill down to 40px above the Baines Simmons logo (min 528px). Swap in the client photo per deal.
7. **Running header** on inner pages is all caps and keeps the dash: "CLIENT – PROPOSAL TITLE · PROPOSAL".
8. **No controls in the template:** no control bar, form fields or buttons on any page.
9. **PDF filename (hard rule):** `Proposal - Baines Simmons - [Proposal Title] - [Client]`, filename-illegal characters removed.
10. **Page and contents numbers are typed text.** Renumber every running header and the p2 contents list whenever a page is added or removed.
11. **The contents list on p2 is clickable.** Each entry is a link to its page: `<a href="PageNN.dc.html">` in the page files and on the canvas (page 1 is `Main.dc.html` on the canvas), and `<a href="#pNN">` to the sheet with `id="pNN"` in the print copy, which Chrome turns into internal PDF links. When pages move, update the targets as well as the numbers. Never turn the entries into plain text.

## Filling it from a quote
- Deal details are literal text: client and proposal title (cover and running headers), proposal type (cover pill), prepared for, prepared by, date issued (cover), deal code and version (footers pp 2–14). Replace every instance across all 15 pages.
- Replace bracketed placeholders on pp 3–8 with the quote's description, tranche tables and summary totals. Add or remove table rows by duplicating an existing row; keep the column template.
- Venue address goes on p10.
- Kickoff: when starting a new proposal, ask for prepared by, client company, prepared for (names), date effective, validity and classification, then fill [Name], [Client], [Date] etc. throughout.

## Brand and typography
- Fonts: Titillium Web (headings), Open Sans (body), always loaded from the Master Brand System (`styles.css` / `tokens.css` / `fonts/`, or `ds/master-brand-system/` on a canvas). Never a template-only font file, `@font-face` or Google Fonts link. Every export embeds them as real fonts.
- **No all caps** on headings, eyebrows, section labels, table group rows or pills, and no `text-transform:uppercase`. Only exceptions: the running page header and the cover proposal-type pill.
- **Punctuation:** never use em dashes; use en dashes (–) or rephrase. Body copy is left-aligned, never justified.
- **Brand grey / light grey** = `#E0E7F5` (`--color-mist`) at 25% opacity by default: `color-mix(in srgb, var(--color-mist) 25%, transparent)`.
- **Dark blue callouts** (`--color-dark-blue` background) at 50% opacity, text fully opaque.
- **Headings:** eyebrow label ("Section NN" / "Appendix A") on its own line, then the section H1. Secondary headings on the same page are H2. When a section spans pages, show the H1 only on its first page; continuation pages show just the eyebrow (with extra bottom margin).
- **Lists:** markers always sapphire (`var(--brand-primary)`); generous gap between items; list container indented ~6px.
- **Two-column comparison blocks** ("Baines Simmons will provide" / "The client will"): each column in its own light-grey outlined container (border + radius).
- **Column copy parity:** in any row of parallel columns/cards, headings are all one line or all two lines, and bodies have identical line counts. Fix by rewriting to length, never by shrinking type or clamping one cell. Cells in a row share width and height (`grid-auto-rows:1fr`).
- **Links:** every URL, email and phone number is a live `<a>` (`https://`, `mailto:`, `tel:+` digits only), `text-decoration:none`.
- **Messaging:** TrustFlight is the "Aerospace Safety Intelligence Platform". Baines Simmons is a **capability** of TrustFlight, never a subsidiary, division or business unit. Never write "TrustFlight Group", "a TrustFlight company" or "TrustFlight Services", and never name competitors in customer-facing copy. Keep the ™ on "Integrated Safety at Every Elevation™".

## Tables
Copy the canonical table (TrustFlight proposal p11, page id `tech-log-matrix`); never invent a new style.
- CSS grid, never `<table>`. Wrapper: `border:1px solid var(--border-subtle);border-radius:10px;overflow:hidden;margin:0 0 14px;`
- Every row is its own `display:grid` with the same fixed `grid-template-columns` in fr units (never `auto`).
- Header row: `background:var(--brand-primary)`, Titillium Web 700, white; cells `padding:6px 10px;font-size:8pt;line-height:1.3;`
- Group rows: `border-top:1px solid var(--border-subtle);background:color-mix(in srgb, var(--color-mist) 25%, transparent);` label `padding:4px 10px;` Titillium Bold 8.5pt, line-height 1.25, Midnight.
- Body rows: `border-top:1px solid var(--border-subtle);`. First cell `padding:4px 10px;font-size:8pt;line-height:1.3;font-weight:700;color:var(--color-midnight);`. Other cells `padding:4px 10px;font-size:8pt;line-height:1.35;color:var(--text-secondary);border-left:1px solid var(--border-subtle);`
- Total row: `background:var(--surface-sunken);font-weight:700;`
- Row icons: all rows or none. Tables are full-width, never side by side; stacking is fine if nothing overflows.

## Page geometry
- US Letter by default (8.5×11in), never A4 unless asked.
- Every page is its own file with a fixed 816×1056px root (never `min-height`) and `overflow:hidden`, so each page is exactly one sheet.
- Size page boxes in inches for print, never px.

## PDF export (mandatory recipe)
1. **Canvas:** Export › All artboards (.pdf); the 15 artboards export in reading order, one page each.
2. **Local:** regenerate the print copy from the 15 page files (each page's markup inside a `<div class="sheet">`, `@page{size:8.5in 11in;margin:0}`, `.sheet{width:8.5in;height:11in;overflow:hidden;break-after:page}`, `<link rel="stylesheet" href="../../styles.css">`, no scripts), serve the system folder locally and print to PDF from Chrome: US Letter, margins None, Background graphics ON.
3. **Never** use `doc-page.js` or any script that re-renders the pages for print: Chrome then writes body text as Type 3 glyph outlines from a locally installed font, the spacing breaks and Acrobat slows to a crawl.
4. **Verify:** 15 pages at 8.5×11in; only OpenSans-* and TitilliumWeb-* fonts, embedded, no Type 3 and no substitutes (LiberationSans etc.); text selectable; ≤ 5 MB.
- Only compress photography to meet 5 MB; never logos, icons or UI screenshots.
- Always offer a .docx alongside the PDF.

## Editor vs output
- No editor-only affordances in the template: no control bar, placeholder rings, guide boxes or buttons on any page.

## File naming
- `[Brand] - [Doc type] - [Doc title]`, e.g. `Baines Simmons - Proposal - Commercial Proposal`. Applies to HTML, PDF and DOCX.
- Exception: the exported proposal PDF is named `Proposal - Baines Simmons - [Proposal Title] - [Client]`.
