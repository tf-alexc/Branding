# Master Brand System (local mirror)

A partial copy of the Master Brand System design system, kept so the Baines Simmons proposal template can be rendered and exported locally. The live system is the source of truth: https://claude.ai/artifact/3TSvubnBz4WCsS1xD7o3b9

Paths match the live system's `project/` folder, so every relative link in the template resolves.

## Baines Simmons proposal

- Pages: `templates/proposal-baines-simmons/Page01.dc.html` to `Page15.dc.html`, one fixed US Letter page each.
- Print copy: `templates/proposal-baines-simmons/Baines Simmons - Proposal - Commercial Proposal -print-.html`, generated from the 15 pages.
- Rules: `assets/docs/templates/proposal-baines-simmons/PROCESS.md` and `CLAUDE-CODE-RULES.md`.
- Design canvas: https://claude.ai/artifact/6bZKWgjxJcqrdnzYxbD95z

## Exporting a PDF locally

Serve this folder, then print the print copy from Chrome (US Letter, margins None, Background graphics ON):

```bash
python3 -m http.server 8768 --bind 127.0.0.1 --directory "Master Brand System"
```

Open `http://127.0.0.1:8768/templates/proposal-baines-simmons/` and pick the print copy. Never add `doc-page.js` or any print script: it makes Chrome write the text as Type 3 glyph outlines, which breaks the spacing and makes the PDF very slow in Acrobat.

## Keeping it in sync

Changes are made in the live system first, then copied here. The fonts, `tokens.css`, `styles.css` and `components/bundle.css` are copies of the live system's files; do not edit them here.
