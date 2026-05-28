---
name: deck-builder
description: Build a branded presentation deck for TrustFlight, Baines Simmons, Kenyon, or Redline. PowerPoint is the primary output. When invoked, always ask the user about the purpose of the deck, whether they have a brief or abstract, which brand it is for, and whether they also want a PDF export.
---

# Deck Builder

Primary output: PowerPoint (`.pptx`).

Templates are baked into this skill at `templates/` — never ask the user to upload one.

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

Follow the structure implied by the brief (Step 1.2) or the agreed structure for the purpose (Step 1.1). Keep all visual styles, fonts, and colours from the loaded template.

(Detailed build patterns to be added.)

## Step 4: Export

- Always save the `.pptx`.
- If the user asked for PDF in Step 1.4, also export a `.pdf` from the same deck.
