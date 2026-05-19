---
name: linkedin-ad-generator
description: Generate LinkedIn graphic ads from the TrustFlight Illustrator template. Use this skill whenever the user asks to create, generate, make, or export a LinkedIn ad, social graphic, or campaign asset from the Ads template. Handles layout selection, caption update, and JPG export.
---

# LinkedIn Ad Generator

**Template:** SharePoint — `[ORG]-Design - Documents/Claude MCPs and Skills/Illustrator MCPs/Ads - Template.ai`  
**Export root:** SharePoint — `[ORG]-Design - Documents/Graphics - Blog & Social Media/Ad Campaigns/`  
**Caption layer:** `Caption` (unlocked)  
**Layouts:** 01, 02, 03 — each has two artboards (square and wide)

---

## What You Need From the User

Before starting, confirm you have:

1. **Layout** — 01, 02, 03, or "randomise"
2. **Caption text** — the copy to set on both artboards
3. **Product name** — used in the subfolder name and output filename (default: `Centrik 5` if not specified)

If caption text is missing, ask before proceeding. Layout and product name are optional — use defaults if not provided.

---

## Step 1: Prepare the Output Folder

Resolve the SharePoint export root dynamically and create the campaign subfolder. The subfolder name is `{product} - {caption}` (e.g. `Centrik 5 - Elevating Aerospace Safety Standards`):

```bash
EXPORT_ROOT="$HOME/Library/CloudStorage/OneDrive-SharedLibraries-TrustFlight/[ORG]-Design - Documents/Graphics - Blog & Social Media/Ad Campaigns"
SUBFOLDER="{product} - {caption}"
mkdir -p "$EXPORT_ROOT/$SUBFOLDER"
```

---

## Step 2a: Resolve the Layout

If the user specified a layout number (01, 02, or 03), use that.

If the user said "randomise", did not specify a layout, or asked you to choose — pick one of the three layouts at random yourself. Note which layout was chosen so you can report it back in Step 7.

---

## Step 2b: Launch Adobe Illustrator

Ensure Illustrator is running before opening the document. Use Bash:

```bash
open -a "Adobe Illustrator"
sleep 5
```

The `sleep 5` gives Illustrator time to fully launch if it wasn't already open. If it was already running, this is harmless.

---

## Step 2c: Open the Template

First resolve the template path dynamically — the SharePoint sync root varies by username but the structure is consistent:

```bash
TEMPLATE_PATH="$HOME/Library/CloudStorage/OneDrive-SharedLibraries-TrustFlight/[ORG]-Design - Documents/Claude MCPs and Skills/Illustrator MCPs/Ads - Template.ai"
echo "$TEMPLATE_PATH"
```

Use the resolved path with `mcp__illustrator__open_document`:
- `path`: the full path returned by the bash command above

---

## Step 3: Discover Artboards

Use `mcp__illustrator__get_artboards` to list all artboards and their names.

Identify the **two artboards** whose names contain the chosen layout number (e.g. "01" for layout 01). One will be the square format and one will be the wide format. Note their zero-based indices — you will need these for export.

---

## Step 4: Find the Caption Text Frames

Use `mcp__illustrator__find_objects` with:
- `layer`: `Caption`

This returns all text frames in the Caption layer across the document. Each text frame has a UUID and position. You will have one Caption text frame per artboard layout — six total in the document.

Match each Caption text frame to its artboard by comparing the text frame's position (x, y) against each artboard's bounds. A text frame belongs to an artboard if its position falls within that artboard's rectangle.

Identify the two Caption text frames that correspond to the two artboards of the chosen layout.

---

## Step 5: Update the Caption Text

For each of the two matched Caption text frames, use `mcp__illustrator__modify_object` with:
- `uuid`: the text frame's UUID
- `properties.contents`: the caption text provided by the user

Do this for both the square and wide artboards.

---

## Step 5b: Check for Screenshot Overlap

After setting the caption text on each artboard, check whether the Caption text frame overlaps with any object in the **Screenshot** layer on that artboard.

Use `mcp__illustrator__find_objects` with `layer`: `Screenshot` to get all objects in that layer. Then compare bounds:

- Caption text frame bounds: from the `verified.bounds` returned by `modify_object` in Step 5
- Screenshot object bounds: from the `find_objects` result — match to the same artboard by position

**Overlap check:** two rectangles overlap if they intersect on both axes. In artboard-web coordinates (x right, y down):
- No horizontal overlap if: `caption.x + caption.width <= screenshot.x` OR `screenshot.x + screenshot.width <= caption.x`
- No vertical overlap if: `caption.y + caption.height <= screenshot.y` OR `screenshot.y + screenshot.height <= caption.y`
- If neither condition is true → they overlap

**If overlap is detected on an artboard:**

Split the caption into two lines by inserting a line break (`\r`) at the most natural word boundary near the middle of the text. For example, "Safety Intelligence Elevated Further" → "Safety Intelligence\rElevated Further".

Re-apply using `mcp__illustrator__modify_object` with the updated `contents` (using `\r` as the line break character, not `\n`).

Re-check bounds after applying — if overlap persists, try a different split point.

**If no overlap:** keep the caption as a single line. No action needed.

Do this check independently for the square and wide artboards — the same caption text may need different line breaks on each, or neither.

---

## Step 5c: Apply Split Colour Styling

After the overlap check, apply two-tone colour to the caption text. This step is **always required** — every ad must use the split colour treatment.

**Colour values:**
- First half of words → **White**: RGB(255, 255, 255)
- Second half of words → **Electric**: RGB(3, 212, 255)

**Calculate SPLIT_INDEX for the caption:**

The caption `contents` may contain `\r` (if a line break was inserted in Step 5b). Treat `\r` as a word separator alongside spaces:

1. Split `contents` on spaces and `\r` to get a word array.
2. `mid = Math.floor(word_count / 2)` — how many words go in the white first half.
3. Find the character index in `contents` where word `mid` begins (i.e., the start of the first electric word). This is `SPLIT_INDEX`.
   - Example: "Elevating Aerospace Safety Standards" → 4 words, mid=2, word 2 is "Safety" which starts at character index 20 → SPLIT_INDEX=20.
   - Example with line break: "Elevating Aerospace\rSafety Standards" → mid=2, "Safety" starts at index 20 → SPLIT_INDEX=20.

**Apply the colour styling** by writing a script to a temp file and running it via osascript:

```bash
SPLIT_INDEX=<calculated value>
CAPTION_TEXT="<caption contents, with \r if line-broken>"

cat > /tmp/tf_color.js << JSEOF
var doc = app.activeDocument;
var splitAt = $SPLIT_INDEX;
var electric = new RGBColor();
electric.red = 3; electric.green = 212; electric.blue = 255;
var white = new RGBColor();
white.red = 255; white.green = 255; white.blue = 255;
for (var i = 0; i < doc.layers.length; i++) {
  if (doc.layers[i].name === "Caption") {
    var tfs = doc.layers[i].textFrames;
    for (var j = 0; j < tfs.length; j++) {
      var contents = tfs[j].contents;
      if (contents === "$CAPTION_TEXT") {
        var chars = tfs[j].textRange.characters;
        for (var k = 0; k < splitAt; k++) { chars[k].fillColor = white; }
        for (var k = splitAt; k < chars.length; k++) { chars[k].fillColor = electric; }
      }
    }
    break;
  }
}
JSEOF

osascript -e 'tell application "Adobe Illustrator" to do javascript (read POSIX file "/tmp/tf_color.js")'
```

Since both caption frames for the chosen layout share the same contents, a single run colours both the square and wide frames simultaneously.

**Important:** If the caption text contains any characters that would break bash variable interpolation (e.g. double quotes), escape them appropriately before substituting into the heredoc.

---

## Step 6: Export as JPG

For each of the two artboards (square and wide), use `mcp__illustrator__export` with:
- `target`: `artboard:{index}` (zero-based index from Step 3)
- `format`: `jpg`
- `output_path`: `{EXPORT_ROOT}/{product} - {caption}/Ad - {product} - {caption} - {format}.jpg`
  - `{EXPORT_ROOT}` = the resolved SharePoint path from Step 1
  - Replace `{product}` with the product name (default: `Centrik 5`)
  - Replace `{caption}` with the caption text as provided (no line breaks — use the original single-line caption even if `\r` was inserted for the artboard)
  - Replace `{format}` with `Square` or `Wide` based on the artboard
- `raster_options`: `{"dpi": 150}` — pass as a native JSON object, not a string

Export both artboards.

Then open the destination folder in Finder:

```bash
open "$EXPORT_ROOT/$SUBFOLDER"
```

---

## Step 7: Confirm Output

Report back to the user with:
- The layout used (and if it was randomly chosen, say so)
- The full paths to the two exported JPG files
- Confirm both files were created successfully

---

## Important Notes

- Never save or overwrite the template file. It is read-only for this workflow.
- If the artboard names do not clearly indicate square vs. wide, check the artboard dimensions: the wider artboard is the wide format.
- If `find_objects` does not return results filtered by layer, fall back to `mcp__illustrator__list_text_frames` and filter manually by checking which frames are positioned within the target artboards.
- The caption text should be applied exactly as the user provides it, with no modifications.
