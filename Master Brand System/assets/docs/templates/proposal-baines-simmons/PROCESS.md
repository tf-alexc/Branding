# Baines Simmons proposal – process of record

Template files (Master Brand System, `templates/proposal-baines-simmons/`): 15 Design Component pages, one file per sheet, `Page01.dc.html` (cover) to `Page15.dc.html` (back cover), each a fixed US Letter page (816×1056px). Print copy for local PDF export: `Baines Simmons - Proposal - Commercial Proposal -print-.html`, generated from the 15 pages. Design canvas: [Baines Simmons Proposal](https://claude.ai/artifact/6bZKWgjxJcqrdnzYxbD95z), the same 15 pages as artboards (`Main.dc.html` is page 1). Built from the Intermountain Health proposal (OP10663 V2.0).

**Page stack:** 01 cover · 02 contents · 03–04 description · 05–07 proposal details (tranche + MSA pricing tables) · 08 project summary · 09–10 associated costs, payment terms, additional information · 11 acceptance · 12–14 Terms of Agreement · 15 back cover.

## Hard rules
1. **Terms of Agreement (pp 12–14): content is locked.** Never change, reword, reorder or "fix" any clause, even typos. Header/footer only. Layout is a **single full-width column** (8.5pt / 1.4), flowing across three pages in clause order (5.3 opens p13). If anything ever reflows, re-balance by moving whole paragraphs between pages – never by editing text or shrinking type. Clause subheadings: 12px above, 2px below (heading sits tight to its clause). Sub-clause numbers (1.1, 5.3, 9.1, 12.4…) are bold Midnight at the start of each paragraph.
2. **Deal code in every footer.** Each reference document (quote .docx/.pdf) carries an OPxxxxx code and version (e.g. `OP10663_IMHFAS_Quote_V2.0` → `OP10663`, `V2.0`). Always set the code and version from the document being fed; the footer reads "Proposal [code] · [version]" on every inner page. Never ship with the `[OP00000]` placeholder.
3. **Acceptance (p11) and back cover (p15): exact layout and content.** Do not change the acceptance copy, signature fields or the purchase-order table; do not change the contact page.
4. **No all-caps** on headings, section labels, eyebrows, table group rows or pills. Only two exceptions, always all caps: the running page header on inner pages, and the cover proposal-type pill (e.g. "COMMERCIAL PROPOSAL").
5. **Cover photo placeholder matches the original TrustFlight proposal** (Sapphire→Midnight gradient, faint diagonal stripes, "[Placeholder Photo]"). It flexes to fill the space down to 40px above the Baines Simmons logo (min 528px); swap in the client photo per deal.
6. **Footer** shows only "Proposal [code] · [version]" – no "Baines Simmons Limited" prefix. It appears on every page except the cover and back cover, the contents page included.
7. **Cover:** no trailing hyphen after the client name; the cover pill always ends with the fixed word "Proposal". The proposal type is the word(s) before it (default "Commercial" → "COMMERCIAL PROPOSAL"); never let "Proposal" double.
8. **Acceptance page (p11) labels:** the sapphire field labels (Name (Print), Position, Authorised Signature, Date, Purchase Order Number) are 9pt – the same size as the a)/b)/c) body lines. Never shrink them back.
9. **No controls in the template.** There is no control bar, form or button on any page. Every page shows only what prints.
10. **PDF filename:** `Proposal - Baines Simmons - [Proposal Title] - [Client]` (see Export).
11. **Running header** keeps the dash between client and proposal title ("CLIENT – PROPOSAL TITLE · PROPOSAL").

## Filling it from a quote
- Deal details are literal text on the pages, never form fields: client and proposal title (cover, and the running header on pp 3–14), proposal type (cover pill), prepared for, prepared by and date issued (cover), deal code and version (footer on pp 2–14). Replace every instance; search all 15 pages for `[Client]`, `[Proposal Title]`, `[OP00000]`, `V1.0`, `[Name]` and `[Date]` before export.
- Replace bracketed placeholders on pp 3–8 with the quote's description, tranche tables (codes, names, durations, delegates, dates, prices, expenses) and summary totals. Add/remove table rows by duplicating an existing row; keep the column template.
- Venue address on p10.
- Page numbers (top right of the running header) and the contents list on p2 are typed text. When a page is added or removed, renumber every header and the contents list by hand.
- A continuation page is a new page file inserted in sequence (and a new artboard on the canvas, placed in reading order).
- **The contents list on p2 is clickable.** Each entry is a link to its page: `<a href="PageNN.dc.html">` in the page files and on the canvas (page 1 is `Main.dc.html` on the canvas), and `<a href="#pNN">` to the sheet with `id="pNN"` in the print copy, which Chrome turns into internal PDF links. When pages move, update the targets as well as the numbers. Never turn the entries into plain text.

## Fonts
Open Sans and Titillium Web always come from the Master Brand System: `styles.css` → `tokens.css` → `fonts/*.woff2` in the system, or its installed copy under `ds/master-brand-system/` on a canvas. Never add a template-only font file, `@font-face` rule or Google Fonts link. The brand Open Sans has no kerning table (Google's Open Sans ships without one); Titillium Web carries its own kerning.

## Export
- **On the canvas:** Export › All artboards (.pdf). Each artboard is one page, in reading order.
- **Locally (Claude Code):** open the print copy in Chrome over a local server (not `file://`) and print to PDF: US Letter, margins None, Background graphics ON. Regenerate the print copy from the 15 pages after any edit.
- **Keep the PDF light for Acrobat.** The canvas exports on a Linux server, so the page CSS sets `text-rendering:geometricPrecision` (exact letter widths; without it every letter snaps to a whole pixel and the spacing looks broken) and `font-kerning:normal`. Never use semi-transparent colours (`rgba()` with alpha, `color-mix(… transparent)`), `opacity`, `box-shadow`, `filter`/blur or `repeating-linear-gradient` on the pages: Chrome turns them into transparency groups, luminosity masks and PostScript-function patterns that Acrobat redraws slowly. Use the solid pre-blended colour instead (for example `#9296A0` for Graphite at 50% on white, `#DADFE6` for white at 85% on Midnight), draw repeating stripes as plain SVG lines, and inline the footer brandmark as an SVG filled `#7689A2`.
- **Never** add `doc-page.js` or any script that re-renders the pages for print. It makes Chrome write the text as drawn glyph outlines (Type 3 fonts) that substitute a locally installed font, with rounded letter positions: the spacing looks wrong and the PDF is very slow in Acrobat.
- **Verify every PDF:** 15 pages, 8.5×11in; fonts listed are only OpenSans-* and TitilliumWeb-* (no Type 3, no substitutes such as LiberationSans); no `/SMask` or `/FunctionType 4`; letter positions fractional (not whole numbers); text is selectable; under 5 MB.
- **Filename:** `Proposal - Baines Simmons - [Proposal Title] - [Client]`, filename-illegal characters removed.

## Rebranding an existing Baines Simmons proposal (Word or PDF)
Use this when someone uploads an existing Baines Simmons proposal (usually a .docx) and asks to rebrand, redesign or "put it in the new template". The output is a new proposal built on this template; the source file is never edited.

1. **Read the source in full** (text, tables, headers and footers, filename). List what it contains before building anything.
2. **Deal fields.** Take the deal code and version from the filename or the document (`OP10663_IMHFAS_Quote_V2.0` → `OP10663`, `V2.0`). Fill client, proposal title, proposal type, prepared for, prepared by and date issued from the document. Anything the source does not state stays a bracketed placeholder and is listed back to the user; never invent a name, date, price or code.
3. **Map content to the page stack**, never the other way round:
   - background, current situation, objectives → Description (pp 3–4, "Background", "Our approach");
   - session-by-session or day-by-day plans → the tranche day table on p3;
   - management system support, deliverables, follow-on work → "Management system assistance", "Deliverables", "Beyond the programme" (p4);
   - course codes, names, durations, delegates, dates, prices and expenses → the tranche and MSA tables (pp 5–7), one row per line item, rows added by duplicating an existing row;
   - totals → Project summary (p8);
   - subsistence, travel, shipping, cancellation → Associated costs (p9); payment terms → Payment terms (p9); venue, timings, equipment, validity and similar → Additional information (pp 9–10).
   Keep the source's facts and figures exactly. Rewrite wording only to meet the brand rules (no all caps, no em dashes, left-aligned, column parity, TrustFlight messaging) and to fit the layout.
4. **Locked pages stay as they are.** Acceptance (p11), Terms of Agreement (pp 12–14) and the back cover (p15) are never rebuilt from the source. If the source's terms or acceptance wording differ from the template, keep the template and tell the user which clauses differ.
5. **Overflow.** If content does not fit a page, re-balance across the existing pages first (move whole blocks); add a continuation page only for Description or Proposal details, using the continuation-page heading rule. Never shrink type.
6. **Cover photo.** Use the client or programme photo if the source has one; otherwise keep the placeholder and say so. Web images follow the README's "Sourcing images from the web".
7. **Output.** Fill a copy of the 15 pages (in chat: a new Design artifact with the Baines Simmons Proposal canvas files copied in, never the canvas itself), export the PDF as in Export, check it, name it `Proposal - Baines Simmons - [Proposal Title] - [Client]`, and offer a .docx.
8. **Report** in a few lines: the deal fields used, which source sections went where, every remaining placeholder, any clause differences from step 4, and where any image came from.
