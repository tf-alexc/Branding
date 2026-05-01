---
name: linkedin-holiday-generator
description: Generate LinkedIn holiday post artboards from the open Holidays Illustrator file. Use this skill whenever the user asks to create, generate, build, or export LinkedIn holiday posts, seasonal graphics, or holiday artboards from the Holidays template.
---

# LinkedIn Holiday Post Generator

**File:** `/Users/alexcraiu/Desktop/Claude Playground/Illustrator Templates/Holidays - Template.ai`  
**Master artboard:** index 0 (`linkedin-holiday-template`) — never modify this, it is the source of truth  
**Workflow:** duplicate master → edit copy → export → delete copy. The master is always restored.  
**CAPTION layer:** update with holiday title text (the large display name)  
**Title layer:** do NOT modify — always reads "celebrating"  
**Photo layer:** `Picture` — replace background image per holiday  
**Photography root:** `$HOME/Library/CloudStorage/OneDrive-SharedLibraries-TrustFlight/[ORG]-Design - Documents/Photography/`  
**Export root:** `$HOME/Library/CloudStorage/OneDrive-SharedLibraries-TrustFlight/[ORG]-Design - Documents/Graphics - Blog & Social Media/Holidays/`

---

## Holidays Reference Table

Process each holiday below. The **Artboard Name** column is the kebab-case artboard ID. The **Caption** column is the exact text to set in the CAPTION layer. The **Photo** column is the path relative to the Photography root (use the `-lr.jpg` file; some Military Aircraft files use `" - lr.jpg"` with a space).

Holidays marked **[EXISTS]** already have an artboard in the file — skip creating a new one, but still export if needed.

| # | Artboard Name | Caption | Photo |
|---|---------------|---------|-------|
| 1 | linkedin-holiday-new-year | New Year | `Other/fireworks-01.jpg` |
| 2 | linkedin-holiday-mlk-day | Martin Luther King Day | `Corporate Business People/corporate-01-edit-lr.jpg` |
| 3 | linkedin-holiday-engineers-week | Engineers Week | `Engineers/engineers-ipad-10-lr.jpg` |
| 4 | linkedin-holiday-canada-aviation-day-feb | Canada's National Aviation Day | `Commercial jets/aircraft-commercial-10-lr.jpg` |
| 5 | linkedin-holiday-womens-history-month | International Women's History Month | `Pilots/shutterstock_2445924441-lr.jpg` |
| 6 | linkedin-holiday-womens-day | International Women's Day | `Pilots/shutterstock_2445924441-lr.jpg` |
| 7 | linkedin-holiday-womens-month-raymonde-de-laroche | Raymonde de Laroche Day | `Pilots/pilot-ipad-news-01-lr.jpg` | **[EXISTS — artboard 1]** |
| 8 | linkedin-holiday-womens-month-rosie-the-riveter | Rosie the Riveter Day | `Engineers/engineers-ipad-6-lr.jpg` | **[EXISTS — artboard 3]** |
| 9 | linkedin-holiday-mothers-day-us | Mother's Day | `Corporate Business People/corporate-02-edit-lr.jpg` |
| 10 | linkedin-holiday-mothers-day-uk | Mothering Sunday | `Corporate Business People/corporate-03-edit-lr.jpg` |
| 11 | linkedin-holiday-internship-month | National Internship Awareness Month | `Corporate Business People/corporate-01-edit-lr.jpg` |
| 12 | linkedin-holiday-april-fools | April Fools | `Commercial jets/aircraft-commercial-17-lr.jpg` |
| 13 | linkedin-holiday-earth-day | Earth Day | `Commercial jets/aircraft-commercial-15-lr.jpg` |
| 14 | linkedin-holiday-world-pilots-day | World Pilots Day | `Pilots/pilot-ipad-news-01-lr.jpg` | **[EXISTS — artboard 4]** |
| 15 | linkedin-holiday-faa-drone-safety-day | FAA Drone Safety Day | `Other/air-traffic-controller-01.jpg` |
| 16 | linkedin-holiday-general-aviation-month | General Aviation Appreciation Month | `Commercial jets/aircraft-commercial-11-lr.jpg` |
| 17 | linkedin-holiday-skilled-trades-day | National Skilled Trades Day | `Engineers/engineers-ipad-10-lr.jpg` |
| 18 | linkedin-holiday-firefighters-day | International Firefighters' Day | `Commercial jets/aircraft-commercial-9-lr.jpg` |
| 19 | linkedin-holiday-may-the-fourth | May the 4th | `Commercial jets/aircraft-commercial-17-lr.jpg` |
| 20 | linkedin-holiday-victoria-day | Victoria Day | `Commercial jets/aircraft-commercial-10-lr.jpg` |
| 21 | linkedin-holiday-aviation-maintenance-day | Aviation Maintenance Technician Day | `Jet Engines/engine-01-lr.jpg` |
| 22 | linkedin-holiday-paper-airplane-day | National Paper Airplane Day | `Commercial jets/aircraft-commercial-9-lr.jpg` |
| 23 | linkedin-holiday-memorial-day | Memorial Day | `Military Aircraft/shutterstock_2223994557 - lr.jpg` |
| 24 | linkedin-holiday-flight-attendant-day | International Flight Attendant Day | `Corporate Business People/corporate-02-edit-lr.jpg` |
| 25 | linkedin-holiday-world-environment-day | World Environment Day | `Commercial jets/aircraft-commercial-15-lr.jpg` |
| 26 | linkedin-holiday-pride-month | Pride Month | `Airports/airport-bristol-01-lr.jpg` |
| 27 | linkedin-holiday-juneteenth | Juneteenth | `Corporate Business People/corporate-03-edit-lr.jpg` |
| 28 | linkedin-holiday-women-in-engineering-day | Women in Engineering Day | `Engineers/engineers-ipad-6-lr.jpg` |
| 29 | linkedin-holiday-canada-day | Canada Day | `Other/flag-canada.jpg` | **[EXISTS — artboard 5]** |
| 30 | linkedin-holiday-independence-day | Independence Day | `Other/flag-usa-01.jpg` | **[EXISTS — artboard 6]** |
| 31 | linkedin-holiday-amelia-earhart-day | National Amelia Earhart Day | `Pilots/shutterstock_2445924441-lr.jpg` |
| 32 | linkedin-holiday-national-intern-day | National Intern Day | `Corporate Business People/corporate-01-edit-lr.jpg` |
| 33 | linkedin-holiday-civic-holiday | Civic Holiday | `Commercial jets/aircraft-commercial-11-lr.jpg` |
| 34 | linkedin-holiday-national-airborne-day | National Airborne Day | `Military Aircraft/shutterstock_2435571439 - lr.jpg` |
| 35 | linkedin-holiday-helicopter-day | International Helicopter Day | `Helis/h125-01.jpg` |
| 36 | linkedin-holiday-national-aviation-day | National Aviation Day | `Commercial jets/aircraft-commercial-17-lr.jpg` |
| 37 | linkedin-holiday-national-aviation-week | National Aviation Week | `Commercial jets/aircraft-commercial-15-lr.jpg` |
| 38 | linkedin-holiday-womens-equality-day | National Women's Equality Day | `Pilots/shutterstock_2445924441-lr.jpg` |
| 39 | linkedin-holiday-labour-day | Labour Day | `Commercial jets/aircraft-commercial-10-lr.jpg` | **[EXISTS — artboard 8]** |
| 40 | linkedin-holiday-hispanic-heritage-month | Hispanic Heritage Month | `Corporate Business People/corporate-02-edit-lr.jpg` |
| 41 | linkedin-holiday-free-museum-day | Free Museum Day | `Commercial jets/aircraft-commercial-9-lr.jpg` |
| 42 | linkedin-holiday-usaf-anniversary | 75th Anniversary of the U.S. Air Force | `Military Aircraft/shutterstock_2223994557 - lr.jpg` |
| 43 | linkedin-holiday-business-womens-day | American Business Women's Day | `Corporate Business People/corporate-03-edit-lr.jpg` |
| 44 | linkedin-holiday-truth-reconciliation-day | Day for Truth and Reconciliation | `Other/flag-canada.jpg` |
| 45 | linkedin-holiday-black-history-month | Black History Month | `Corporate Business People/corporate-01-edit-lr.jpg` |
| 46 | linkedin-holiday-world-teachers-day | World Teachers Day | `Corporate Business People/corporate-02-edit-lr.jpg` |
| 47 | linkedin-holiday-first-presidential-flight | First Flight by a US President | `Commercial jets/aircraft-commercial-11-lr.jpg` |
| 48 | linkedin-holiday-canadian-thanksgiving | Canadian Thanksgiving | `Airports/airport-bristol-01-lr.jpg` |
| 49 | linkedin-holiday-atc-day | Day of the Air Traffic Controller | `Other/air-traffic-controller-01.jpg` |
| 50 | linkedin-holiday-native-american-heritage-month | Native American Heritage Month | `Commercial jets/aircraft-commercial-17-lr.jpg` |
| 51 | linkedin-holiday-aviation-history-month | National Aviation History Month | `Military Aircraft/shutterstock_2435571439 - lr.jpg` |
| 52 | linkedin-holiday-stem-day | National STEM/STEAM Day | `Engineers/engineers-ipad-10-lr.jpg` |
| 53 | linkedin-holiday-remembrance-day | Remembrance Day | `Other/poppies-01.jpg` |
| 54 | linkedin-holiday-thanksgiving-us | Thanksgiving | `Airports/airport-bristol-01-lr.jpg` | **[EXISTS — artboard 9]** |
| 55 | linkedin-holiday-native-american-heritage-day | Native American Heritage Day | `Commercial jets/aircraft-commercial-9-lr.jpg` |
| 56 | linkedin-holiday-civil-aviation-day | International Civil Aviation Day | `Commercial jets/aircraft-commercial-15-lr.jpg` |
| 57 | linkedin-holiday-oklahoma-women-aviation | Oklahoma Women in Aviation Day | `Pilots/pilot-ipad-news-01-lr.jpg` |
| 58 | linkedin-holiday-wright-brothers-day | Wright Brothers Day | `Commercial jets/aircraft-commercial-11-lr.jpg` |
| 59 | linkedin-holiday-christmas | Christmas Day | `Airports/airport-bristol-01-lr.jpg` |
| 60 | linkedin-holiday-boxing-day | Boxing Day | `Commercial jets/aircraft-commercial-10-lr.jpg` |

---

## Step 1: Verify the Active Document

Use `mcp__illustrator__get_document_info` to confirm `Holidays - Template.ai` is open and active. If it is not open, open it first:

```bash
open '/Users/alexcraiu/Desktop/Claude Playground/Illustrator Templates/Holidays - Template.ai'
sleep 5
```

Resolve the Photography root and Export root dynamically:

```bash
PHOTO_ROOT="$HOME/Library/CloudStorage/OneDrive-SharedLibraries-TrustFlight/[ORG]-Design - Documents/Photography"
EXPORT_ROOT="$HOME/Library/CloudStorage/OneDrive-SharedLibraries-TrustFlight/[ORG]-Design - Documents/Graphics - Blog & Social Media/Holidays"
mkdir -p "$EXPORT_ROOT"
```

---

## Step 2: For Each Holiday (loop)

Work through the holidays table one at a time. For each holiday, the cycle is: **duplicate master → name copy → edit → export**. The copy is kept in the document. The master artboard (index 0) is never touched.

**Skip** any holiday where an artboard named `socials-{kebab-caption}` already exists in the document — use `mcp__illustrator__get_artboards` to check before starting. The kebab name is the caption lowercased with spaces replaced by hyphens (e.g. `"Wright Brothers Day"` → `socials-wright-brothers-day`).

### 2a: Duplicate master + edit copy in one osascript

Run a single osascript that:
1. Duplicates the master artboard (index 0) by adding a new artboard **to the right** of the last existing artboard (40px gap), then copy-pasting all art and translating it to align with the new artboard position
2. Updates the CAPTION text on the copy
3. Replaces the background image on the copy
4. Enforces 85pt minimum font size with two-line overflow handling

```bash
CAPTION_TEXT="Wright Brothers Day"   # replace per holiday
PHOTO_PATH="/full/path/to/photo.jpg" # replace per holiday

cat > /tmp/holiday_gen.js << JSEOF
var doc = app.activeDocument;
var captionText = "$CAPTION_TEXT";
var photoPath = "$PHOTO_PATH";
var MIN_SIZE = 85;

// --- 1. Duplicate master artboard ---
var masterAB = doc.artboards[0];
var masterRect = masterAB.artboardRect; // [L, T, R, B] in Illustrator coords (T > B)
var abW = masterRect[2] - masterRect[0];
var abH = masterRect[1] - masterRect[3];

// Find the rightmost edge of all existing artboards to avoid overlap
var GAP = 40;
var rightmost = masterRect[2];
for (var i = 0; i < doc.artboards.length; i++) {
  var r = doc.artboards[i].artboardRect[2];
  if (r > rightmost) rightmost = r;
}
var newLeft = rightmost + GAP;
var newRect = [newLeft, masterRect[1], newLeft + abW, masterRect[3]];

var newAB = doc.artboards.add(newRect);
newAB.name = "ARTBOARD_NAME"; // e.g. socials-wright-brothers-day
var newIdx = doc.artboards.length - 1;

// Copy all art from master — pasteInPlace lands it at master's coordinates
doc.artboards.setActiveArtboardIndex(0);
app.executeMenuCommand('selectall');
app.executeMenuCommand('copy');
doc.artboards.setActiveArtboardIndex(newIdx);
app.executeMenuCommand('pasteInPlace');

// Translate pasted art to align with the new artboard position
var dx = newLeft - masterRect[0];
var sel = doc.selection;
for (var s = 0; s < sel.length; s++) {
  sel[s].translate(dx, 0);
}

// --- 2. Update CAPTION text on copy ---
// The CAPTION layer now has two frames (master + copy). The copy is the one
// whose bounds fall within the new artboard's document rect.
var captionLayer = null;
for (var i = 0; i < doc.layers.length; i++) {
  if (doc.layers[i].name === "CAPTION") { captionLayer = doc.layers[i]; break; }
}
if (!captionLayer) throw new Error("CAPTION layer not found");
captionLayer.locked = false;

var tf = null;
var abRect = doc.artboards[newIdx].artboardRect;
for (var j = 0; j < captionLayer.textFrames.length; j++) {
  var gb = captionLayer.textFrames[j].geometricBounds;
  // Match frames whose left edge aligns with the new artboard (same doc coords as master,
  // but we pick the last/most-recently-pasted one — highest index)
  tf = captionLayer.textFrames[j]; // keep updating to get last match
}
if (!tf) throw new Error("CAPTION text frame not found");

// Set text and enforce 85pt minimum
tf.contents = captionText;
tf.textRange.characterAttributes.size = MIN_SIZE;
app.redraw();

// Check overflow and split to two lines if needed
var maxWidth = abW - 94; // ~47px margin each side
var frameWidth = tf.geometricBounds[2] - tf.geometricBounds[0];
if (frameWidth > maxWidth) {
  var words = captionText.split(" ");
  var bestSplit = 1, bestDiff = Infinity;
  for (var s = 1; s < words.length; s++) {
    var diff = Math.abs(words.slice(0, s).join(" ").length - words.slice(s).join(" ").length);
    if (diff < bestDiff) { bestDiff = diff; bestSplit = s; }
  }
  tf.contents = words.slice(0, bestSplit).join(" ") + "\r" + words.slice(bestSplit).join(" ");
}

// --- 3. Replace image inside clipping mask on copy ---
var picLayer = null;
for (var i = 0; i < doc.layers.length; i++) {
  if (doc.layers[i].name === "Picture") { picLayer = doc.layers[i]; break; }
}
if (!picLayer) throw new Error("Picture layer not found");
picLayer.locked = false;

// Find the clipping group on the copy (most recently pasted = pageItems[0], topmost)
var clipGroup = null;
for (var j = 0; j < picLayer.pageItems.length; j++) {
  var item = picLayer.pageItems[j];
  if (item.typename === "GroupItem" && item.clipped) {
    clipGroup = item; // keep iterating — we want the last match (most recently pasted copy)
  }
}
if (!clipGroup) throw new Error("Clipping group not found in Picture layer");

// Clipping path is always the FIRST child in Illustrator clipping groups.
// Do NOT check the clippingPath property — it always returns undefined in ExtendScript.
var maskPath = clipGroup.pageItems[0]; // first child = mask path (by Illustrator convention)

var maskBounds = maskPath.geometricBounds; // [L, T, R, B]
var maskW = maskBounds[2] - maskBounds[0];
var maskH = maskBounds[1] - maskBounds[3];

// Remove all children EXCEPT the mask (index 0) — iterate backwards to avoid index shift
for (var k = clipGroup.pageItems.length - 1; k >= 1; k--) {
  clipGroup.pageItems[k].remove();
}

// Place new image into the clipping group
var imgFile = new File(photoPath);
var placed = clipGroup.placedItems.add();
placed.file = imgFile;

// Scale to cover the mask rectangle (cover-style, centre crop)
var scaleX = maskW / placed.width;
var scaleY = maskH / placed.height;
placed.resize(Math.max(scaleX, scaleY) * 100, Math.max(scaleX, scaleY) * 100);

// Centre within the mask bounds
placed.left = maskBounds[0] + (maskW - placed.width) / 2;
placed.top = maskBounds[1] - (maskH - placed.height) / 2;
placed.zOrder(ZOrderMethod.SENDTOBACK);
picLayer.locked = true;
JSEOF

osascript << 'ASEOF'
with timeout of 120 seconds
  tell application "Adobe Illustrator" to do javascript (read POSIX file "/tmp/holiday_gen.js")
end timeout
ASEOF
echo "Edit result: $?"
```

### 2b: Export the copy as JPG via osascript

Do **not** use the MCP export tool — it fails silently on this document. Use osascript instead. Illustrator replaces spaces with dashes in filenames, so rename the file after export.

```bash
CAPTION_TEXT="Wright Brothers Day"   # replace per holiday
EXPORT_ROOT="$HOME/Library/CloudStorage/OneDrive-SharedLibraries-TrustFlight/[ORG]-Design - Documents/Graphics - Blog & Social Media/Holidays"

# Build expected Illustrator output name (spaces → dashes)
ILLUS_NAME=$(echo "Holiday - $CAPTION_TEXT" | tr ' ' '-')
FINAL_NAME="Holiday - $CAPTION_TEXT"

cat > /tmp/export_holiday.js << JSEOF
var doc = app.activeDocument;
var newIdx = doc.artboards.length - 1;
doc.artboards.setActiveArtboardIndex(newIdx);
var exportFile = new File("$EXPORT_ROOT/$ILLUS_NAME.jpg");
var opts = new ExportOptionsJPEG();
opts.artBoardClipping = true;
opts.resolution = 150;
opts.qualitySetting = 10;
opts.antiAliasing = true;
doc.exportFile(exportFile, ExportType.JPEG, opts);
JSEOF

osascript << 'ASEOF'
with timeout of 120 seconds
  tell application "Adobe Illustrator" to do javascript (read POSIX file "/tmp/export_holiday.js")
end timeout
ASEOF

# Rename to correct filename with spaces
mv "$EXPORT_ROOT/$ILLUS_NAME.jpg" "$EXPORT_ROOT/$FINAL_NAME.jpg" 2>/dev/null || true
ls -lh "$EXPORT_ROOT/$FINAL_NAME.jpg"
```

### 2c: Open export folder

After each export (or after completing all holidays in a batch):

```bash
open "$EXPORT_ROOT"
```

---

## Step 3: Confirm Output

Report back:
- Total JPGs exported
- Any holidays where a suitable photo was not found (fall back to `Commercial jets/aircraft-commercial-9-lr.jpg` if no better match exists)
- Confirm the master artboard was not modified (document still has exactly 1 artboard named `linkedin-holiday-template`)

---

## Important Notes

- **Never modify the master artboard.** Index 0 (`linkedin-holiday-template`) is the source of truth. Always work on the copy. The copy is kept — named `socials-{kebab-caption}`.
- **Artboard placement:** New artboards must never overlap existing ones. Always place each new artboard to the right of the rightmost existing artboard with a 40px gap. After `pasteInPlace`, translate all pasted art by `newLeft - masterRect[0]` to align it with the new artboard.
- **Skip duplicates.** Before creating a copy, check if `socials-{kebab-caption}` already exists in the artboard list. If it does, skip that holiday.
- **Never use the MCP export tool** — it fails silently on this document. Always export via osascript `ExportOptionsJPEG`.
- **Filename spaces:** Illustrator converts spaces to dashes on export. Always `mv` the output file to the correct `Holiday - {Caption}.jpg` name immediately after.
- **Never modify the Title layer.** It always reads "celebrating". Only the CAPTION layer text changes.
- **Photo rule:** Only use `-lr.jpg` files from the Photography folder. If a subfolder has no `-lr.jpg`, use the best available `.jpg` (not `.psd`). Military Aircraft files use `" - lr.jpg"` (space before lr).
- **Clipping mask:** The image in the `Picture` layer lives inside a clipping group. Always place the new image inside the group, scale it to cover the mask rectangle, and never remove or modify the clipping path itself.
- **CAPTION font size:** Minimum 85pt always. Never go below this. If the text overflows, split into two lines (`\r`) at the most balanced word boundary. Two lines maximum — never three.
- **Unlock layers before working on them.** Before any read or write operation on a layer, always unlock it first (`layer.locked = false`). This applies to CAPTION, Picture, and any other layer you need to access. Locked layers are invisible to `selectall`, `textFrames`, and `pageItems` — operations will silently fail or miss content if the layer is locked.
- **Process in batches** if the full list is too large. Confirm with the user how many to process at once.
