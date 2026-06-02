---
name: deck-builder
description: Build a branded presentation deck for TrustFlight, Baines Simmons, Kenyon, or Redline. PowerPoint is the primary output. Trigger on any request that mentions a deck, presentation, slides, pitch, or slideshow, including phrasings like "need a deck", "put together a presentation", "build me some slides", "make a pitch", "draft a slideshow". When invoked, always ask the user about the purpose of the deck, whether they have a brief or abstract, which brand it is for, and whether they also want a PDF export.
---

# Deck Builder

Primary output: PowerPoint (`.pptx`).

Templates are baked into this skill at `templates/` — never ask the user to upload one.

## Trigger phrases

Invoke this skill on any request that contains the words **deck**, **presentation**, **slides**, **pitch**, or **slideshow** — and any natural phrasing around them. Examples:

- "need a deck"
- "put together a presentation"
- "build me some slides"
- "draft a pitch"
- "throw together a slideshow"
- "can you make a deck for..."
- "I need slides on..."

If the request is ambiguous (e.g. "a one-pager" or "a write-up"), confirm with the user before invoking.

## Step 1: Gather Intent

Ask the user, in this order, before building anything:

1. **Purpose of the deck.** Sales, CRM, pitch, capability overview, internal update, training, event, etc. The purpose drives structure and tone.
2. **Brief or abstract?** Ask: "Do you have a brief or an abstract for this deck?"
   - **Yes** — request it and follow the structure it implies.
   - **No** — propose a structure based on the purpose and confirm before building.
3. **Brand.** Ask which brand the deck is for:
   - TrustFlight
   - Baines Simmons
   - Kenyon
   - Redline
4. **PDF export?** Ask whether the user also wants a `.pdf` alongside the `.pptx`.

Record each answer. Do not skip any of these questions.

## Step 2: Load the Right Template

Open the matching template from `skills/deck-builder/templates/`:

| Brand | Template file |
|-------|---------------|
| TrustFlight | `TrustFlight - Basic Presentation Template.pptx` |
| Baines Simmons | `Baines Simmons - Basic Presentation Template.pptx` |
| Kenyon | `Kenyon - Basic Presentation Template.pptx` |
| Redline | `Redline - Basic Presentation Template.pptx` |

Always build from the brand's template. Never start from a blank presentation. Never substitute one brand's template for another.

## Step 3: Build the Deck

Follow the structure implied by the brief (Step 1.2) or the agreed structure for the purpose (Step 1.1).

### Formatting and Styling

- **Font:** Always Open Sans. No other font is permitted anywhere in the deck — not Arial, not Aptos, not Lato, not Calibri. Set `run.font.name = "Open Sans"` on every text run, including footers, page numbers, tables, charts, and callouts.
- **Titles:** All slide titles in **Open Sans Light**. Never Regular, never Bold. This applies to every title placeholder, including section breaks and the agenda. Body copy stays in the template's default body weight.
- **Colours and styling:** Follow the loaded template. Use the swatches, backgrounds, and accents that ship with the chosen brand's template — do not introduce colours from outside it.
- **Slide layouts:** Vary layouts across the deck. Do not default every slide to a bulleted list.
  - Suggest interesting layouts where they fit the content: three-column, four-column, stat callouts, text + image, icon grids, timelines, numbered steps, quote slides.
  - Choose the layout per slide based on the content, not on a fixed sequence.
- **Big numbers:** Whenever a slide leads with a large statistic or headline number, set it in **Open Sans Light, 50pt, Centrik Gold (`#FFD740`)**. Supporting copy beneath stays in the template's body style.

### Agenda Slide

**Every deck must include an Agenda slide — no exceptions.** It is required regardless of deck length, audience, purpose, or whether the brief mentions one. If the brief does not specify an agenda, derive it from the section break titles and include it anyway. Place it directly after the title slide.

The Agenda slide must always follow the **style and structure of the Agenda slide already in the brand template**. Do not redesign it, do not rebuild it from a blank layout, and do not substitute a different layout.

- Clone the template's Agenda slide and edit it in place.
- **Add or remove rows as needed** to match the deck's actual section count — keep the same row shape, spacing, type style, and accents as the existing rows.
- New rows must visually match the template's existing rows exactly (same height, same fills, same text style). Duplicate an existing row rather than constructing one from scratch.
- Populate each row with the title of the corresponding section break slide, in order.

### Stylising with Graphics and Iconography

Using icons and decorative graphics to lift a slide is **optional but encouraged**. A well-placed icon, illustration, or supporting graphic lifts a slide far beyond plain text — use them on stat callouts, icon grids, numbered steps, section breaks, and anywhere a slide would otherwise feel text-heavy. Skip them on slides that are already visually rich (full-bleed photos, product screenshots, charts).

**Source folder.** Pull icons and decorative graphics from the SharePoint `Graphics - General & Iconography/` folder (local path: `/Users/alexcraiu/Library/CloudStorage/OneDrive-SharedLibraries-TrustFlight/[ORG]-Design - Documents/Graphics - General & Iconography`).

**Match the file to the slide context.** Read the filename and only use a graphic whose subject genuinely fits the slide's topic — e.g. a `safety-shield.png` belongs on a safety slide, not a generic "next steps" slide. When in doubt, pick a more neutral graphic or skip it rather than forcing a poor match.

**Placement.** Place transparent PNGs directly on the slide with `add_picture` — no rounded rectangle wrapper, no border. Preserve the original aspect ratio; never stretch.

### Build Notes

(Further build patterns to be added.)

## Step 4: Export

- Always save the `.pptx`.
- If the user asked for PDF in Step 1.4, also export a `.pdf` from the same deck.
