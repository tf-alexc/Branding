---
name: ppt-design-system
description: TrustFlight PowerPoint design system. Use this skill whenever the user asks to create, generate, build, make, or draft a presentation, deck, slides, pitch, or PowerPoint — for any audience or purpose, including internal decks, customer pitches, event materials, product demos, or capability overviews. Also use when asked to restyle, rebrand, or update an existing PowerPoint to match TrustFlight brand standards. Always invoke this skill for any presentation-related request, even quick one-off slides.
---

# TrustFlight PowerPoint Design System

**Source data:** `~/.claude/skills/ppt-design-system/brand.json`  
**Brand messaging + voice:** `~/.claude/skills/brand-framework/SKILL.md` and `BRAND-GUIDELINES.md`

---

## Before You Start

Read `brand.json` for all colour hex values, template paths, and layout indices. Do not hard-code values from memory — always reference the file.

Also load the brand-framework skill for messaging guidance if the presentation requires copy (pitches, customer decks, corporate comms).

---

## Step 1: Identify the Mode

Determine which mode applies based on the user's request:

| Mode | Trigger | Action |
|------|---------|--------|
| **New deck** | "Create a deck", "Make a presentation", "Build slides" | Create from master template |
| **Single slide** | "Add a slide", "Make one slide", "Create a title slide" | Add to existing or create minimal file |
| **Rebrand** | "Restyle this", "Apply our brand", "Fix the colours" | Open existing file, apply brand colours and fonts |

---

## Step 2: Load the Master Template

The canonical template is at (from `brand.json > templates.master`):
```
~/.claude/skills/ppt-design-system/Basic Presentation Template.pptx
```

Slide size: **12192000 × 6858000 EMU** (13.33" × 7.5", standard widescreen 16:9).

The Baines Simmons template (`templates.reference_only.baines_simmons`) is for BSL-specific work only.

**Always build from this template — never start from a blank presentation.**

> **MCP v2.1.0 bug notice:** `keep_slides`, `delete_slide`, and `clone_slide` are broken in the current MCP server (error: `'PresentationPart' object has no attribute 'related_parts'`). All structural operations — deleting slides, cloning slides, stripping the template — must be done directly via Python/python-pptx. The MCP server is only reliable for reading slide info and setting core properties. Use the Python patterns in Steps 3 and 5 below.

**Required: strip SharePoint metadata before saving.** The master template carries SharePoint customXml, a modern-comments author list, and stale app.xml metadata — all of which cause PowerPoint to show a "found a problem with content" repair dialog on open. Strip them and fix app.xml on every save using this pattern:

```python
import zipfile, io, re

def clean_and_save(prs, output_path):
    """Save presentation with all repair-triggering template artefacts stripped."""
    import tempfile, os
    from lxml import etree
    tmp = tempfile.mktemp(suffix='.pptx')
    prs.save(tmp)

    STRIP = {
        'customXml/item1.xml', 'customXml/item2.xml', 'customXml/item3.xml',
        'customXml/itemProps1.xml', 'customXml/itemProps2.xml', 'customXml/itemProps3.xml',
        'customXml/_rels/item1.xml.rels', 'customXml/_rels/item2.xml.rels',
        'customXml/_rels/item3.xml.rels',
        'docProps/custom.xml',   # SharePoint ContentTypeId
        'ppt/authors.xml',       # modern-comments author list — causes repair when slides are rebuilt
    }

    STRIP_PARTS = {'/'+s for s in STRIP}

    def strip_rels(xml_bytes):
        root = etree.fromstring(xml_bytes)
        for rel in list(root):
            t = rel.get('Target','').lstrip('/')
            if any(t.endswith(s.split('/')[-1]) or s in t for s in STRIP):
                root.remove(rel)
        return etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)

    def strip_content_types(xml_bytes):
        root = etree.fromstring(xml_bytes)
        for el in list(root):
            if el.get('PartName','') in STRIP_PARTS:
                root.remove(el)
        return etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)

    def fix_app_xml(xml_bytes, slide_count):
        """Update app.xml slide count — python-pptx never updates this, causing repair."""
        text = xml_bytes.decode('utf-8')
        text = re.sub(r'<Slides>\d+</Slides>', f'<Slides>{slide_count}</Slides>', text)
        # Zero out TitlesOfParts and HeadingPairs to avoid stale slide title list
        text = re.sub(r'<TitlesOfParts>.*?</TitlesOfParts>', '<TitlesOfParts/>', text, flags=re.DOTALL)
        text = re.sub(r'<HeadingPairs>.*?</HeadingPairs>', '<HeadingPairs/>', text, flags=re.DOTALL)
        return text.encode('utf-8')

    slide_count = len(prs.slides)

    buf = io.BytesIO()
    with zipfile.ZipFile(tmp, 'r') as zin, zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename in STRIP:
                continue
            content = zin.read(item.filename)
            if item.filename == '[Content_Types].xml':
                try: content = strip_content_types(content)
                except: pass
            elif item.filename == 'docProps/app.xml':
                try: content = fix_app_xml(content, slide_count)
                except: pass
            elif item.filename.endswith('.rels'):
                try: content = strip_rels(content)
                except: pass
            zout.writestr(item, content)

    os.remove(tmp)
    with open(output_path, 'wb') as f:
        f.write(buf.getvalue())
```

Use `clean_and_save(prs, OUTPUT_PATH)` instead of `prs.save(OUTPUT_PATH)` on every deck.

---

## Step 3: Clean Up Template Slides

Strip all unwanted template slides using Python directly (MCP delete is broken — see Step 2 note).

**Template structure (`Basic Presentation Template.pptx`, 7 example slides, 0-indexed):**

| Index | Layout | Notes |
|-------|--------|-------|
| 0 | Dark - Title | Blank title slide — clone as cover |
| 1 | Dark - Section Break | Example section break |
| 2 | Dark - Horizontal Split | Example content (top/bottom split) |
| 3 | Dark - Vertical Split | Example content (left/right split) |
| 4 | Dark - Radial Split 2 | Example content with radial graphic |
| 5 | Light - Main | Example light-background content |
| 6 | Dark - End | **End slide** — always clone this as the closing slide. It already contains the TrustFlight boilerplate, logo, and contact information. Never recreate it from a blank layout. |

The example slides exist for visual reference only — they should all be deleted from the working deck once you've cloned the end slide (and any other layout you want to copy structure from). Build new slides from the layouts via `prs.slides.add_slide(layout)` rather than reusing the example content.

**Python delete pattern:**
```python
R_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'

def delete_slide(prs, idx):
    slide_ids = list(prs.slides._sldIdLst)
    el = slide_ids[idx]
    rId = el.get('{%s}id' % R_NS)
    try: prs.part.drop_rel(rId)
    except: pass
    prs.slides._sldIdLst.remove(el)

# Delete in reverse order to avoid index shifting
for i in range(len(prs.slides) - 1, -1, -1):
    if i not in keep_set:
        delete_slide(prs, i)
```

**Recommended approach for new decks:** Open the template with `Presentation(template_path)`, clone the end slide (index 6) to preserve it, add all new content slides to the end using `prs.slides.add_slide(layout)`, then delete all original example slides in reverse order. This avoids any MCP structural tools entirely.

---

## Step 4: Build Slides on Top of the Template

The example slides in the template are not reusable content — they're visual reference for the layouts. Build new slides from the layouts directly.

The one exception is the **end slide** (index 6), which contains the TrustFlight boilerplate, logo, and contact block. Always clone it rather than rebuilding from the `Dark - End` layout.

### Clone pattern (Python — MCP clone_slide is broken)

```python
import copy

R_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'

def clone_slide(prs, src_idx):
    src = prs.slides[src_idx]
    new = prs.slides.add_slide(src.slide_layout)
    sp_tree = new.shapes._spTree
    for el in list(sp_tree): sp_tree.remove(el)
    for el in src.shapes._spTree: sp_tree.append(copy.deepcopy(el))
    for rel in src.part.rels.values():
        if 'image' in rel.reltype:
            new_rId = new.part.relate_to(rel.target_part, rel.reltype)
            for el in sp_tree.iter():
                if el.get('{%s}id' % R_NS) == rel.rId:
                    el.set('{%s}id' % R_NS, new_rId)
    return new
```

Use this for the end slide (index 6) and any other slide with embedded visuals you want to preserve verbatim.

### Plan the Slide Structure

For a full deck, plan the structure before building. Standard TrustFlight deck structure:

1. **Title slide** — layout index 0 (`Dark - Title`)
2. **Agenda** — build from layout 9 (`Light - Main`) or 7 (`Dark - Section Break`); the new template does not ship a dedicated agenda slide
3. **Section breaks** — layout 7 (`Dark - Section Break`) between major topics
4. **Content slides** — vary across layouts 1, 2, 3, 4, 6, 10, 11 (see table below) — never default everything to one layout
5. **Light-background content** — layout 9 (`Light - Main`) when a visual change of pace is needed mid-deck
6. **Closing slide** — always clone template slide index 6 (the `Dark - End` example) using the clone pattern above. Never use `add_slide` for the end slide. Do not clear or replace its content — the slide already contains the TrustFlight boilerplate, logo, and contact block and must be used as-is.

**Available layouts:**

| Index | Name | Use for |
|-------|------|---------|
| 0  | Dark - Title           | Opening title slide |
| 1  | Dark - Radial split    | Split content with radial graphic accent |
| 2  | Dark - Radial Split 2  | Alternative radial split — different proportions |
| 3  | Dark - Radial Centre   | Centred radial — key stat, single focus message |
| 4  | Dark - Blank           | Blank dark canvas for custom-built content (tables, timelines, image grids) |
| 5  | Dark - Globe Split     | Split content with globe graphic |
| 6  | Dark - Globe           | Globe layout — global reach, international stats |
| 7  | Dark - Section Break   | Section divider between topics |
| 8  | Dark - End             | **Never use the layout directly** — always clone template slide index 6 |
| 9  | Light - Main           | Light-background content — title + body |
| 10 | Dark - Horizontal Split| Top/bottom split content |
| 11 | Dark - Vertical Split  | Left/right split content |

### Vary the Layout on Every Slide

**Never default every content slide to a bulleted list.** A deck full of bullet points is hard to read and looks unfinished. For each slide, choose the layout that best fits the content. Use python-pptx to build custom arrangements directly in XML or via `add_shape`, `add_table`, and `add_picture` — the placeholder system is just a starting point.

**Layout options to consider for each slide:**

- **Bulleted list** — only when content is genuinely list-like (4 or fewer items, each standing alone). Not the default.
- **2-column text** — build two text boxes side by side. Good for comparisons, before/after, or two parallel ideas.
- **3-column text** — three equal-width text boxes. Good for feature trios, pillars, or step-by-step processes.
- **Stat callout** — one large number or short phrase as the dominant element, with a supporting sentence below. Use for impact moments.
- **Text + image** — body copy on the left, a rounded-rectangle photo on the right (see Step 7 for image rules). Good for product or capability slides.
- **Table** — when data has clear rows and columns. Style with Midnight header row, alternating Light/White rows, Open Sans throughout.
- **Quote** — a single pull quote centred or left-aligned in large type, attributed below. Clone the section break layout and repurpose it.
- **Icon grid** — 3 or 6 icons with short labels beneath. Use transparent PNGs placed directly (no border).
- **Numbered steps** — large numerals (styled as accent elements) with a short description beside each. Better than a plain numbered list.
- **Timeline** — a horizontal line with labelled nodes, built from shapes. Good for roadmaps or onboarding sequences.

Build these using python-pptx shapes and text boxes rather than forcing everything into placeholder 1. Position elements using EMU coordinates (slide is 12192000 × 6858000 EMU).

**Suggesting New Layouts**

When planning a deck, call out the intended layout for each slide before building — e.g. "Slide 6: Centrik 5 — text + image (copy left, screenshot right)". This lets the user approve the structure before content is written.

---

## Step 5: Build Slides

Add new slides with `mcp__powerpoint__add_slide` (for fresh layouts) or `mcp__powerpoint__clone_slide` (for slides that already exist in the template). Then use `mcp__powerpoint__populate_placeholder` to fill content.

**Font rule:** All text in Open Sans (Regular or Bold). Never Arial, Aptos, or Lato in PowerPoint.

**Preserve template styles:** When setting text on cloned or template-based slides, only set the font name (Open Sans) — do not override weight, size, or colour. The master template already defines the correct style for each placeholder (e.g. titles are Light weight, not Bold). Explicitly setting `bold=True`, `font.size`, or `font.color` on a run will override these template styles and break the visual system. Set only `run.font.name = "Open Sans"` and leave everything else untouched.

**Colour rule:**
- All template slides: Midnight (#062955) background, white text
- Accents and highlights: Sapphire (#1E5BB5), Azure (#479FF8), or Electric (#03D4FF)
- Product-specific decks: reference product palette from `brand.json > colors.products`

**Text rules:**
- All body text left-aligned
- Active voice, short sentences
- No em dashes — use hyphens, colons, or commas instead
- No corporate jargon (see brand-framework for approved language)
- Lead with the value — put the most important point first on every slide

**Critical: fix `grpSpPr` on every slide added via `add_slide`:**
`add_slide` creates an empty `<p:grpSpPr/>` which is invalid OOXML and causes PowerPoint to show a "found a problem with content" repair dialog on open. After adding each new slide, call this fix before doing anything else with the slide:

```python
A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'
P_NS = 'http://schemas.openxmlformats.org/presentationml/2006/main'

def fix_grp_sp_pr(slide):
    sp_tree = slide.shapes._spTree
    grp = sp_tree.find(f'{{{P_NS}}}grpSpPr')
    if grp is not None and grp.find(f'{{{A_NS}}}xfrm') is None:
        grp.insert(0, etree.fromstring(
            f'<a:xfrm xmlns:a="{A_NS}">'
            f'<a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
            f'<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/>'
            f'</a:xfrm>'
        ))
```

Call `fix_grp_sp_pr(slide)` immediately after every `prs.slides.add_slide(layout)`. Cloned slides (via `clone_slide`) inherit the correct xfrm from the source and do not need this fix.

**Footer and page number — built into the layouts:**
Every layout except `Dark - Title` (index 0) and `Dark - End` (index 8) ships with both a Footer placeholder and a Slide Number placeholder. Slides added via `add_slide(layout)` inherit them automatically — do not copy them manually.

The default footer text is `©2026 TrustFlight Ltd. All rights reserved.` Update the year manually if the deck is being prepared for a future date.

**Footer text colour:**
- Dark slides (Midnight/dark background): footer text is Light grey — `#E0E7F5`
- Light slides (Light - Main, index 9): footer text is Graphite — `#242D41`

These colours come from the layout — do not override them on the run. If a placeholder appears in the wrong colour, the fix is in the layout, not the slide.

---

## Step 6: Copy Guidance

When writing slide copy, align to the brand framework. Key principles:

**Headline pattern:** Lead with a verb or outcome, not a category label.
- Good: "Connect your safety data to your training records"
- Avoid: "Safety and Training Integration"

**Body pattern:** Short, declarative sentences. Max 3-4 bullet points per slide. Each bullet should stand alone — no sub-bullets.

**Numbers:** Use the approved key numbers verbatim — do not round or paraphrase:
- 1,600+ organisations
- 120 countries
- 120+ regulatory frameworks
- Centrik: 180,000+ aviation professionals
- Tech Log: 20,000+ active users
- Baines Simmons: 25 years, 750+ organisations, 40+ regulators advised, 200,000+ trained
- Redline: 20+ years, ICAO-appointed UK Aviation Security Training Centre, 200+ clients
- Kenyon: 120 years, 2,500+ specialist responders, 500+ organisations

**Product positioning:**
- Centrik 5 = "proven operational platform for safety, quality, and risk management" — not "safety software"
- Tech Log = "maintenance and airworthiness records" — not "a logging tool"
- Smart Suite = "AI innovation engine" and "the future" — lead with intelligence, not features
- Never describe TrustFlight as "a software company"

**Connecting capabilities:**
- When mentioning one capability, connect it to others — Centrik data feeding Smart Suite, Tech Log linking to Centrik, Baines Simmons expertise unlocked by Centrik findings
- Never silo products — always show the platform picture

**Audience framing:**

| Audience | Lead With |
|----------|-----------|
| CEO / Board | Operational resilience, enterprise risk reduction |
| COO | Operational confidence, one partner for the full lifecycle |
| CIO / IT | Platform consolidation, AI-native, one source of truth |
| VP Safety | Safety intelligence — SMS/QMS connected to training and response |
| Head of Compliance | Compliance efficiency, audit management, regulatory tracking |
| Procurement | Total cost of ownership, vendor consolidation |

---

## Step 7: Insert Images

**Two types of image asset — different treatment for each:**

### Photographs (JPGs from the Photography folder)

**Source:** Always pull from the local Photography folder at:
`/Users/alexcraiu/Library/CloudStorage/OneDrive-SharedLibraries-TrustFlight/[ORG]-Design - Documents/Photography`

Use `find` with `-name '*-lr.jpg'` to list available files. Only use JPGs with `-lr` in the filename. Never use `.PSD` files or any other format.

**Style — always apply both of the following:**

1. **Rounded rectangle frame** — embed the image as a `blipFill` inside a `p:sp` shape with `prstGeom prst="roundRect"`. Use a small corner radius: `adj=8000` (8%). Never use the default large rounding.
2. **Azure border** — add a `a:ln` stroke at 1pt (12700 EMU) with colour `#479FF8`.

**Sizing and positioning:**
- Preserve original aspect ratio — read natural pixel dimensions with `PIL.Image.open(path).size` and fit within the target area without distortion
- If the photo is large and a full-bleed or oversized treatment suits the layout, it is acceptable to scale the photo up and let it bleed off the **right edge only** — never off the left, top, or bottom. Set `left` such that the image is anchored left and extends rightward beyond `slide_width_emu` (12192000 EMU)
- **Never cover the TrustFlight logo (top-right corner) or the page number (bottom-right corner).** When positioning or sizing a photo, ensure it does not overlap either of these elements — even when bleeding off the right edge. Keep the top-right and bottom-right corners clear.

### Transparent PNG graphics (icons, product UI, illustrations)

**Do not apply the rounded rectangle frame or Azure border to transparent PNGs.** Place them directly on the slide using `prs.slides[n].shapes.add_picture(img_path, left, top, width, height)`. Preserve aspect ratio the same way, but no shape wrapping and no border.

**CRITICAL: Never stretch images.** The shape dimensions must always match the image's natural aspect ratio. Use `fit_in_area()` to calculate width and height before placing any image — never set width and height independently or to fill an arbitrary box. Stretching is the most visible brand error in a presentation.

**Aspect ratio — never distort (applies to both types):**
- Read the image's natural pixel dimensions using `PIL.Image.open(path).size`
- Given a target area (max width × max height), calculate the shape dimensions to fit within that area while preserving the original ratio
- The shape must match the image's ratio exactly — do not stretch or letterbox

**Python pattern for images:**
```python
from PIL import Image
from pptx.util import Emu
from lxml import etree

def fit_in_area(img_path, max_w_emu, max_h_emu):
    with Image.open(img_path) as im:
        iw, ih = im.size
    ratio = iw / ih
    if ratio > max_w_emu / max_h_emu:
        w = max_w_emu; h = int(max_w_emu / ratio)
    else:
        h = max_h_emu; w = int(max_h_emu * ratio)
    return w, h

def add_image_rounded(slide, img_path, left, top, max_width, max_height, border_pt=1.0):
    width, height = fit_in_area(img_path, max_width, max_height)
    _, rId = slide.part.get_or_add_image_part(img_path)
    spId = max((int(s._element.get('id', 0)) for s in slide.shapes
                if str(s._element.get('id', '')).isdigit()), default=10) + 1
    border_w = int(border_pt * 12700)
    sp_xml = (
        f'<p:sp xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
        f' xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
        f' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f'<p:nvSpPr><p:cNvPr id="{spId}" name="RoundedImage {spId}"/>'
        f'<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr/></p:nvSpPr>'
        f'<p:spPr>'
        f'<a:xfrm><a:off x="{left}" y="{top}"/><a:ext cx="{width}" cy="{height}"/></a:xfrm>'
        f'<a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 8000"/></a:avLst></a:prstGeom>'
        f'<a:blipFill><a:blip r:embed="{rId}"/><a:stretch><a:fillRect/></a:stretch></a:blipFill>'
        f'<a:ln w="{border_w}"><a:solidFill><a:srgbClr val="479FF8"/></a:solidFill></a:ln>'
        f'</p:spPr>'
        f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>'
    )
    slide.shapes._spTree.append(etree.fromstring(sp_xml))
```

---

## Step 7b: Add Charts or Tables (if needed)

Use `mcp__powerpoint__add_chart` or `mcp__powerpoint__add_table` as appropriate.

Apply brand colours to chart series:
- Primary series: Sapphire (#1E5BB5)
- Secondary: Azure (#479FF8)
- Tertiary: Electric (#03D4FF)
- Background fills: Light (#E0E7F5) or Midnight (#062955)

---

## Step 8: Set Core Properties and Save

Use `mcp__powerpoint__set_core_properties`:
- `title`: Presentation title
- `author`: Alexandru Craiu (default)
- `subject`: Audience or purpose

Use `mcp__powerpoint__save_presentation`. Default save location: `/Users/alexcraiu/Desktop/Claude Playground/Claude Presentations`. Name format: `[Topic] - [Date or Version].pptx`

> Never save to `~/Desktop/` directly.

---

## Rebrand Mode

When restyling an existing deck:

1. Open with `mcp__powerpoint__open_presentation`
2. Use `mcp__powerpoint__manage_fonts` to update fonts to Open Sans
3. Use `mcp__powerpoint__apply_professional_design` or manually update slide backgrounds and text colours
4. Check text for em dashes and jargon — flag to user if found
5. Save as a new file (don't overwrite originals)

---

## What Not to Do

- Never add a blank slide when an existing template slide can be cloned instead
- Never describe TrustFlight as "a software company"
- Never use "TrustFlight Group", "TrustFlight Services", or "a TrustFlight company"
- Never call Baines Simmons, Redline, or Kenyon "subsidiaries", "divisions", or "business units"
- Never default every content slide to a bulleted list — vary layouts across the deck (columns, tables, stats, text + image, quotes, icon grids, timelines)
- Never use em dashes
- Never use justified text alignment
- Never override template font styles when setting text — do not explicitly set bold, size, or colour on runs; only set `run.font.name = "Open Sans"` and let the template define everything else
- Never change logo colours to anything other than Midnight or white
- Never name competitors in customer-facing materials
- Never paraphrase or round the approved key numbers
- Never place a raw photograph directly on a slide — always use the rounded rectangle + Azure border treatment
- Never apply the rounded rectangle frame or Azure border to transparent PNG graphics — place them directly without any shape wrapper or border
- Never stretch or distort an image — always preserve the original aspect ratio by fitting within the target area
- Never use a large corner radius for images — adj=8000 (8%) only
- Never pull images from the Photography folder unless the filename contains `-lr` and is a `.jpg`
- Never bleed an oversized photo off the left, top, or bottom edge — only the right edge is permitted
- Never allow a photo to cover the TrustFlight logo (top-right) or the page number (bottom-right)
- Never leave `grpSpPr` empty on an `add_slide` slide — always call `fix_grp_sp_pr(slide)` immediately after adding
- Never rebuild the end slide from the `Dark - End` layout — always clone template slide index 6, which contains the TrustFlight boilerplate, logo, and contact block
