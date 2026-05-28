---
name: deck-builder
description: Build a TrustFlight-branded presentation deck. PowerPoint is the primary output. When invoked, always ask the user up front whether they also want a PDF export.
---

# Deck Builder

Primary output: PowerPoint (`.pptx`).

## Step 1: Ask About PDF

Before building anything, ask the user:

> Do you want a PDF export alongside the PowerPoint?

Wait for the answer. Record the choice:
- **Yes** — produce both `.pptx` and `.pdf` at the end
- **No** — produce only `.pptx`

Do not skip this question, even if the user's original request only mentioned PowerPoint.

## Step 2: Build the Deck

(To be filled in.)

## Step 3: Export

- Always save the `.pptx`.
- If the user asked for PDF in Step 1, also export a `.pdf` from the same deck.
