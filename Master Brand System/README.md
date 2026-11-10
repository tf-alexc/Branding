# Master Brand System (local mirror)

A partial copy of the Master Brand System design system, kept so the Baines Simmons proposal template can be rendered and exported locally. The live system is the source of truth: https://claude.ai/artifact/3TSvubnBz4WCsS1xD7o3b9

Paths match the live system's `project/` folder, so every relative link in the template resolves.

## Baines Simmons proposal

- Pages: `templates/proposal-baines-simmons/Page01.dc.html` to `Page15.dc.html`, one fixed US Letter page each.
- Print copy: `templates/proposal-baines-simmons/Baines Simmons - Proposal - Commercial Proposal -print-.html`, generated from the 15 pages.
- Rules: `assets/docs/templates/proposal-baines-simmons/PROCESS.md` and `CLAUDE-CODE-RULES.md`.
- Design canvas: https://claude.ai/artifact/6bZKWgjxJcqrdnzYxbD95z

## Corporate booklets

- Portrait (US Letter): `templates/corporate-booklet-portrait/CorporateBookletPortrait.dc.html`. Design canvas: https://claude.ai/artifact/A856f2qebJULeretGKpe8S
- Landscape (A4): `templates/corporate-booklet-landscape/CorporateBookletLandscape.dc.html`. Design canvas: https://claude.ai/artifact/NJUPS9dDoqhB8txcAJREEa
- The sidebar shows the document title, set once in the `documentTitle` tweak. The back cover has no sidebar and matches the TrustFlight proposal back cover.
- Both load the system through `ds-base.js` (`styles.css` and `_ds_bundle.js`), so open them from the served folder.

## Corporate whitepaper (portrait)

- Pages: `templates/corporate-whitepaper-portrait/Page01.dc.html` (cover) to `Page15.dc.html` (back cover), one fixed US Letter page each. Design canvas: https://claude.ai/artifact/EkZ5i6htuAbrCmmekWTSv3
- Corporate cover, sidebar and back cover; whitepaper text and layouts; proposal table style. The sidebar title is typed on each page.
- For Kenyon, the sidebar logo is the Kenyon globe mark only (`kenyon-globe-white.svg` on dark sidebars, `kenyon-globe-rgb.svg` on light), never a wordmark, horizontal, anniversary or stacked logo.
- A Kenyon-only whitepaper carries the Kenyon globe watermark on every page except the cover and full-bleed photo pages (Kenyon proposal spec: inline SVG, 478px at `left:553px;top:793px`, `z-index:-1`; `#F8F9FA` on white pages, `#0E2F5A` on Midnight pages; never `opacity`).

## Exporting a PDF locally

Serve this folder, then print the print copy from Chrome (US Letter, margins None, Background graphics ON):

```bash
python3 -m http.server 8768 --bind 127.0.0.1 --directory "Master Brand System"
```

Open `http://127.0.0.1:8768/templates/proposal-baines-simmons/` and pick the print copy. Never add `doc-page.js` or any print script: it makes Chrome write the text as Type 3 glyph outlines, which breaks the spacing and makes the PDF very slow in Acrobat.

## Keeping it in sync

Changes are made in the live system first, then copied here. The fonts, `tokens.css`, `styles.css` and `components/bundle.css` are copies of the live system's files; do not edit them here.
