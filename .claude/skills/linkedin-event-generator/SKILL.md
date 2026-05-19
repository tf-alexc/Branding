---
name: linkedin-event-generator
description: Generate LinkedIn event announcement graphics from the Events Generator Illustrator template. Use whenever the user asks to generate event graphics, attending posts, or LinkedIn social graphics for TrustFlight events.
---

# LinkedIn Event Generator

**Template:** `/Users/alexcraiu/Desktop/Claude Playground/Illustrator Templates/Events Generator.ai`  
**Master artboard:** index 0 (`socials-default`) — never modify  
**Events API:** `https://p01--events-tracker--xzp2zkf8b975.code.run/api/events`  
**Export root:** `/Users/alexcraiu/Desktop/Claude Playground/Events Generated/`  
**Required env vars:** `PEXELS_API_KEY`, `REMOVEBG_API_KEY`

---

## Layers Reference

| Layer | Content | Method |
|-------|---------|--------|
| `BG` | City background photo | Replace image inside clipping mask (second child) |
| `[EVENT LOGO]` | Event logo PNG (bg removed) | Remove copy's placeholder group; place PNG |
| `Attendees` | `Name\rTitle` | Last text frame in layer |
| `Pill - Country` | ISO alpha-2 code (uppercase) | Last text frame only — icon is static, do not touch |
| `Pill - Venue` | Venue name | Last text frame in layer |
| `Pill - Date` | Formatted date | Last text frame in layer |
| `Attendance` | `ATTENDING` | Static — do not modify |
| `Header & Footer` | — | Locked by design — unlock to paste, then re-lock or leave |
| `Filter` | — | Locked overlay — do not touch contents |

---

## Country → ISO Alpha-2 Mapping

```
Argentina → AR    Canada → CA      Croatia → HR    Egypt → EG
Germany → DE      Greece → GR      Ireland → IE    Netherlands → NL
Qatar → QA        Thailand → TH    Turkey → TR     UK → GB
United Kingdom → GB                United Arab Emirates → AE
United States → US
```

For any country not listed, derive from ISO 3166-1 alpha-2 using your knowledge.

---

## Date Formatting Rules

- Same day: `"12 May 2026"`
- Same month: `"12–14 May 2026"` (en-dash, no spaces around dash)
- Different months: `"29 May – 2 Jun 2026"` (en-dash, space either side)

---

## Step 1: Verify Template is Open

Use `mcp__illustrator__get_document_info` to confirm `Events Generator.ai` is open and active. If not:

```bash
open '/Users/alexcraiu/Desktop/Claude Playground/Illustrator Templates/Events Generator.ai'
sleep 5
```

---

## Step 2: Fetch and Display Upcoming Events

```bash
curl -s "https://p01--events-tracker--xzp2zkf8b975.code.run/api/events" > /tmp/events.json

python3 << 'EOF'
import json
from datetime import datetime, timezone
events = json.load(open('/tmp/events.json'))
today = datetime.now(timezone.utc)
upcoming = [
    e for e in events
    if e.get('status') != 'Cancelled'
    and e.get('start_date')
    and datetime.fromisoformat(e['start_date'].replace('Z', '+00:00')) >= today
]
print(f"Upcoming events ({len(upcoming)}):")
for i, e in enumerate(upcoming):
    sd = e['start_date'][:10]
    ed = e['end_date'][:10]
    date_str = sd if sd == ed else f"{sd} – {ed}"
    staff = f" | attending: {e['staff_names']}" if e.get('staff_names') else ""
    website = " | no website" if not e.get('event_website_url') else ""
    print(f"  {i+1:2}. {e['event_name']} | {e['city']}, {e['country']} | {date_str} | {e['status']}{staff}{website}")
EOF
```

Present the list to the user. Ask which event(s) to generate.

---

## Step 3: Gather Attendee Info

For each selected event, look up its entry in `/tmp/events.json`.

- If `staff_names` is populated: show the names, ask for a **job title per name**. Generate one artboard per name.
- If `staff_names` is null: ask "Who is attending? (full name and job title)"

`staff_names` is always comma-separated names only — titles are never in the API.

---

## Step 4: Prepare Assets (per event/attendee)

### 4a: Resolve export folder

```bash
EVENT_SLUG="socials-tradeshow-wtw-willis"  # socials-tradeshow-{kebab-event-name}
EXPORT_DIR="/Users/alexcraiu/Desktop/Claude Playground/Events Generated/$EVENT_SLUG"
mkdir -p "$EXPORT_DIR"
```

### 4b: Download city background photo (Pexels)

```bash
CITY="Istanbul"  # from event city field
QUERY=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$CITY city'))")
PHOTO_URL=$(curl -s \
  -H "Authorization: $PEXELS_API_KEY" \
  "https://api.pexels.com/v1/search?query=${QUERY}&per_page=3&orientation=portrait" \
  | python3 -c "
import json, sys
d = json.load(sys.stdin)
photos = d.get('photos', [])
if photos:
    print(photos[0]['src']['original'])
else:
    print('NO_RESULT')
")

if [ "$PHOTO_URL" != "NO_RESULT" ]; then
  curl -L -o /tmp/bg_photo.jpg "$PHOTO_URL"
  echo "Photo: $(ls -lh /tmp/bg_photo.jpg | awk '{print $5}')"
else
  echo "WARNING: No Pexels photo found for $CITY"
fi
```

If Pexels returns no results, search again with just the country name.

### 4c: Scrape and process event logo

Only run if `event_website_url` is not null.

```bash
EVENT_URL="https://example.com"

python3 << 'PYEOF'
import urllib.request, re, os, sys

url = "$EVENT_URL"
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')
    # Try og:image
    m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)', html)
    if not m:
        m = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image', html)
    if m:
        print(m.group(1))
    else:
        print("NO_IMAGE")
except Exception as e:
    print("NO_IMAGE")
PYEOF
```

If an image URL is returned (not `NO_IMAGE`):

```bash
LOGO_URL="..."
curl -L -o /tmp/event_logo_raw.png "$LOGO_URL"

# Remove background via remove.bg
curl -s \
  -H "X-Api-Key: $REMOVEBG_API_KEY" \
  -F "image_file=@/tmp/event_logo_raw.png" \
  -F "size=auto" \
  -o /tmp/event_logo.png \
  https://api.remove.bg/v1.0/removebg

LOGO_SIZE=$(stat -f%z /tmp/event_logo.png 2>/dev/null || echo 0)
echo "Logo: ${LOGO_SIZE} bytes"
```

If `LOGO_SIZE` < 5000 bytes, the remove.bg call failed — skip logo placement for this event.

---

## Step 5: Duplicate Artboard + Fill All Text Fields + Replace BG Photo (osascript)

Set variables before running:
```bash
ATTENDEE_NAME="Alex Craiu"
ATTENDEE_TITLE="Head of Design"
CITY="Istanbul"
COUNTRY="Turkey"
VENUE_TEXT="Rixos Tersane Istanbul"
DATE_TEXT="12–14 May 2026"
PHOTO_PATH="/tmp/bg_photo.jpg"
ARTBOARD_NAME="socials-tradeshow-wtw-willis-alex-craiu"  # socials-tradeshow-{kebab-event-name} or socials-tradeshow-{kebab-event-name}-{kebab-attendee-name}
EXPORT_DIR="/Users/alexcraiu/Desktop/Claude Playground/Events Generated/$ARTBOARD_NAME"
```

```bash
cat > /tmp/event_gen.js << JSEOF
var doc = app.activeDocument;
var attendeeName = "$ATTENDEE_NAME";
var attendeeTitle = "$ATTENDEE_TITLE";
var city = "$CITY";
var country = "$COUNTRY";
var venueText = "$VENUE_TEXT";
var dateText = "$DATE_TEXT";
var photoPath = "$PHOTO_PATH";
var artboardName = "$ARTBOARD_NAME";
var RIGHT_PAD = 40;

// Country → "City, Abbrev" display format
var countryAbbrevs = {
  "United Kingdom":"UK","United States":"US","United Arab Emirates":"UAE",
  "Turkey":"Turkey","Netherlands":"Netherlands","Qatar":"Qatar",
  "Argentina":"Argentina","Canada":"Canada","Croatia":"Croatia",
  "Egypt":"Egypt","Germany":"Germany","Greece":"Greece",
  "Ireland":"Ireland","Thailand":"Thailand"
};
var locationText = city + ", " + (countryAbbrevs[country] || country);

function unlockAll(layers) {
  for (var i=0;i<layers.length;i++) {
    layers[i].locked=false; layers[i].visible=true;
    if (layers[i].layers&&layers[i].layers.length>0) unlockAll(layers[i].layers);
  }
}
unlockAll(doc.layers);

var masterAB = doc.artboards[0];
var masterRect = masterAB.artboardRect; // [L,T,R,B] doc coords y-up
// NOTE: masterRect origin may NOT be [0,0] — artboard can be centred (e.g. [-600,0,600,-1400])

// CLEANUP: remove art and artboards from any previous runs
// layer.pageItems only returns direct children — pill groups live in sub-layers, so use recursive cleanLayer
function cleanLayer(layer) {
  for (var i=layer.pageItems.length-1;i>=0;i--) {
    var item=layer.pageItems[i];
    try {
      var b=item.geometricBounds; var cx=(b[0]+b[2])/2; var cy=(b[1]+b[3])/2;
      if (cx<masterRect[0]||cx>masterRect[2]||cy>masterRect[1]||cy<masterRect[3]) item.remove();
    } catch(e) {}
  }
  if (layer.layers) for (var j=0;j<layer.layers.length;j++) cleanLayer(layer.layers[j]);
}
for (var i=0;i<doc.layers.length;i++) cleanLayer(doc.layers[i]);
while (doc.artboards.length>1) doc.artboards[doc.artboards.length-1].remove();
unlockAll(doc.layers);

// Duplicate master via bounds-based selection (never use selectall — grabs items from ALL artboards)
var abW = masterRect[2] - masterRect[0];
var newLeft = masterRect[2] + 40;
var newAB = doc.artboards.add([newLeft,masterRect[1],newLeft+abW,masterRect[3]]);
newAB.name = artboardName;
var newIdx = doc.artboards.length - 1;

app.executeMenuCommand('deselectall');
var toSelect=[];
for (var i=0;i<doc.pageItems.length;i++) {
  var item=doc.pageItems[i];
  try {
    var b=item.geometricBounds; var cx=(b[0]+b[2])/2; var cy=(b[1]+b[3])/2;
    if (cx>=masterRect[0]&&cx<=masterRect[2]&&cy<=masterRect[1]&&cy>=masterRect[3]) toSelect.push(item);
  } catch(e) {}
}
doc.selection=toSelect;
app.executeMenuCommand('copy');
doc.artboards.setActiveArtboardIndex(newIdx);
app.executeMenuCommand('pasteInPlace');

var dx = newLeft - masterRect[0];
var sel=doc.selection;
for (var s=0;s<sel.length;s++) { sel[s].translate(dx,0); }
unlockAll(doc.layers);
app.executeMenuCommand('deselectall');
app.redraw();

// Find text frame in new artboard by placeholder content
// doc.textFrames searches all nesting levels — layer.textFrames only returns direct children
function findTFByContent(placeholder) {
  for (var i=0;i<doc.textFrames.length;i++) {
    var tf=doc.textFrames[i];
    try {
      var b=tf.geometricBounds; var cx=(b[0]+b[2])/2;
      if (cx>=newLeft&&cx<=newLeft+abW&&tf.contents===placeholder) return tf;
    } catch(e) {}
  }
  return null;
}

// Resize pill background path to hug text + RIGHT_PAD
// doc.pathItems searches all nesting levels; pill groups live in sub-layers so layer.pageItems won't find them
// After resize (center anchor), restore left edge — do NOT restore height (triggers proportional rescale)
function resizePillBg(tf) {
  if (!tf) return;
  app.redraw();
  var tfB=tf.geometricBounds; var tfRight=tfB[2]; var tfYCenter=(tfB[1]+tfB[3])/2;
  var bgPath=null; var maxW=0;
  for (var i=0;i<doc.pathItems.length;i++) {
    var item=doc.pathItems[i];
    try {
      var b=item.geometricBounds; var cx=(b[0]+b[2])/2; var cy=(b[1]+b[3])/2; var w=b[2]-b[0];
      if (cx>=newLeft&&cx<=newLeft+abW&&w>400&&Math.abs(cy-tfYCenter)<100) {
        if (w>maxW) { maxW=w; bgPath=item; }
      }
    } catch(e) {}
  }
  if (!bgPath) return;
  var bgLeft=bgPath.geometricBounds[0]; var bgCurrW=bgPath.geometricBounds[2]-bgLeft;
  var origLeft=bgPath.left;
  var desiredW=(tfRight+RIGHT_PAD)-bgLeft;
  if (Math.abs(desiredW-bgCurrW)<1) return;
  bgPath.resize((desiredW/bgCurrW)*100,100,true,false,false,false,100); // center anchor
  bgPath.left=origLeft; // restore left edge only — setting height after non-proportional resize undoes the change
}

// Update text fields and resize pills
var tfCountry = findTFByContent("[Country]");
if (tfCountry) { tfCountry.contents=locationText; resizePillBg(tfCountry); }

var tfVenue = findTFByContent("[Venue]");
if (tfVenue) { tfVenue.contents=venueText; resizePillBg(tfVenue); }

var tfDate = findTFByContent("[Date]");
if (tfDate) { tfDate.contents=dateText; resizePillBg(tfDate); }

// Attendees: read styles from placeholder paragraphs first, set content, reapply styles
// NEVER set tfAttendee.height — it stretches the frame. Let the frame reflow naturally.
// For multiple attendees: stack Name\rTitle\rName\rTitle in one frame.
// Title style is white 48pt — always preserve by reading from paragraph[1] before changing content.
var tfAttendee = findTFByContent("[Name Surname]\r[Title/Position]");
if (tfAttendee) {
  var nameSize  = tfAttendee.paragraphs[0].characters[0].size;
  var nameColor = tfAttendee.paragraphs[0].characters[0].fillColor;
  var nameFont  = tfAttendee.paragraphs[0].characters[0].textFont;
  var titleSize  = tfAttendee.paragraphs[1].characters[0].size;
  var titleColor = tfAttendee.paragraphs[1].characters[0].fillColor;
  var titleFont  = tfAttendee.paragraphs[1].characters[0].textFont;
  var lines = [];
  for (var a = 0; a < attendees.length; a++) {
    lines.push(attendees[a].name); lines.push(attendees[a].title);
  }
  tfAttendee.contents = lines.join("\r");
  var paraIdx = 0;
  for (var a = 0; a < attendees.length; a++) {
    var namePara = tfAttendee.paragraphs[paraIdx];
    for (var c = 0; c < namePara.characters.length; c++) {
      namePara.characters[c].size = nameSize; namePara.characters[c].fillColor = nameColor; namePara.characters[c].textFont = nameFont;
    }
    paraIdx++;
    var titlePara = tfAttendee.paragraphs[paraIdx];
    for (var c = 0; c < titlePara.characters.length; c++) {
      titlePara.characters[c].size = titleSize; titlePara.characters[c].fillColor = titleColor; titlePara.characters[c].textFont = titleFont;
    }
    paraIdx++;
  }
}

// Remove Event Logo placeholder (copy's placeholder, not master's)
for (var i=0;i<doc.layers.length;i++) {
  if (doc.layers[i].name==="Event Logo") {
    var ll=doc.layers[i];
    for (var j=ll.pageItems.length-1;j>=0;j--) {
      try {
        var b=ll.pageItems[j].geometricBounds; var cx=(b[0]+b[2])/2;
        if (cx>=newLeft&&cx<=newLeft+abW) ll.pageItems[j].remove();
      } catch(e) {}
    }
    break;
  }
}

// Replace BG photo — find clipping group in new artboard via doc.pageItems (all levels)
// Must filter w>500 && h>500 — small pill icon clipping groups also match "clipped" and appear first
// Stretch mask to full artboard (abW x abH). Set clipGroup opacity to 15%. Apply Gaussian blur radius 10.
// DO NOT manipulate z-order — paste preserves correct layer order from master automatically.
var clipGroup=null;
for (var i=0;i<doc.pageItems.length;i++) {
  var item=doc.pageItems[i];
  try {
    var b=item.geometricBounds; var cx=(b[0]+b[2])/2;
    var w=b[2]-b[0]; var h=b[1]-b[3];
    if (item.typename==="GroupItem"&&item.clipped&&cx>=newLeft&&cx<=newLeft+abW&&w>500&&h>500) { clipGroup=item; break; }
  } catch(e) {}
}
if (clipGroup) {
  var maskPath=clipGroup.pageItems[0];
  // Stretch mask to full artboard
  maskPath.left=newLeft; maskPath.top=masterRect[1]; maskPath.width=abW; maskPath.height=abH;
  var mb=maskPath.geometricBounds;
  var maskW=mb[2]-mb[0]; var maskH=mb[1]-mb[3];
  for (var k=clipGroup.pageItems.length-1;k>=1;k--) clipGroup.pageItems[k].remove();
  var placed=clipGroup.placedItems.add();
  placed.file=new File(photoPath);
  var sx=maskW/placed.width; var sy=maskH/placed.height;
  placed.resize(Math.max(sx,sy)*100,Math.max(sx,sy)*100);
  placed.left=mb[0]+(maskW-placed.width)/2;
  placed.top=mb[1]-(maskH-placed.height)/2;
  placed.zOrder(ZOrderMethod.SENDTOBACK);
  try {
    placed.applyEffect("<LiveEffect name=\"Adobe Gaussian Blur\"><Dict><Object key=\"blurRadius\" type=\"real\" value=\"10\"/></Dict></LiveEffect>");
    app.redraw();
  } catch(e) {}
  clipGroup.opacity=15;
}
JSEOF

cat > /tmp/event_gen.scpt << 'ASEOF'
with timeout of 120 seconds
  tell application "Adobe Illustrator" to do javascript (read POSIX file "/tmp/event_gen.js")
end timeout
ASEOF
osascript /tmp/event_gen.scpt
echo "Main fill result: $?"
```

---

## Step 6: Place Event Logo (osascript)

Only run if `/tmp/event_logo.png` was successfully created (> 5KB).

```bash
LOGO_SIZE=$(stat -f%z /tmp/event_logo.png 2>/dev/null || echo 0)
if [ "$LOGO_SIZE" -gt 5000 ]; then
LOGO_PATH="/tmp/event_logo.png"

cat > /tmp/event_logo_place.js << JSEOF
var doc = app.activeDocument;
var logoPath = "$LOGO_PATH";

for (var i = 0; i < doc.layers.length; i++) { doc.layers[i].locked = false; }

var newABRect = doc.artboards[doc.artboards.length - 1].artboardRect;
var newLeft = newABRect[0];
var artboardTop = newABRect[1];

var logoLayer = null;
for (var i = 0; i < doc.layers.length; i++) {
  if (doc.layers[i].name === "[EVENT LOGO]") { logoLayer = doc.layers[i]; break; }
}

// Remove copy's placeholder group (last pageItem)
if (logoLayer.pageItems.length > 0) {
  logoLayer.pageItems[logoLayer.pageItems.length - 1].remove();
}

// Place the event logo
var placed = logoLayer.placedItems.add();
placed.file = new File(logoPath);

// Scale to fit within 900x180 area (maintain aspect ratio)
var maxW = 900; var maxH = 180;
var scale = Math.min(maxW / placed.width, maxH / placed.height) * 100;
placed.resize(scale, scale);

// Position: left-aligned at x = newLeft + 70 (artboard-web 70px margin)
// Vertically centred in logo area (artboard-web y=230–468, centre=349)
var logoAreaCenterAW = 349;
placed.left = newLeft + 70;
placed.top = (artboardTop - logoAreaCenterAW) + placed.height / 2;
JSEOF

osascript << 'ASEOF'
with timeout of 60 seconds
  tell application "Adobe Illustrator" to do javascript (read POSIX file "/tmp/event_logo_place.js")
end timeout
ASEOF
echo "Logo placement result: $?"
fi
```

---

## Step 7: Export JPG

```bash
# ARTBOARD_NAME and EXPORT_DIR set earlier — output filename matches artboard name
cat > /tmp/event_export.js << JSEOF
var doc = app.activeDocument;
var newIdx = doc.artboards.length - 1;
doc.artboards.setActiveArtboardIndex(newIdx);
var exportFile = new File("$EXPORT_DIR/$ARTBOARD_NAME.jpg");
var opts = new ExportOptionsJPEG();
opts.artBoardClipping = true;
opts.resolution = 150;
opts.qualitySetting = 10;
opts.antiAliasing = true;
doc.exportFile(exportFile, ExportType.JPEG, opts);
JSEOF

cat > /tmp/event_export.scpt << 'ASEOF'
with timeout of 120 seconds
  tell application "Adobe Illustrator" to do javascript (read POSIX file "/tmp/event_export.js")
end timeout
ASEOF
osascript /tmp/event_export.scpt
echo "Export result: $?"

ls -lh "$EXPORT_DIR/"
```

---

## Step 8: Save Document + Open Export Folder

After all events/attendees for this run are complete:

```bash
osascript << 'ASEOF'
with timeout of 30 seconds
  tell application "Adobe Illustrator" to save document 1
end timeout
ASEOF

open "$EXPORT_DIR"
```

---

## Naming Convention

All three — artboard name, output filename, and folder name — follow the same pattern:

- No attendee or multiple attendees: `socials-tradeshow-{kebab-event-name}`
- Single attendee only: `socials-tradeshow-{kebab-event-name}-{kebab-attendee-name}`

Examples:
- Event "WTW/Willis", no attendee → `socials-tradeshow-wtw-willis`
- Event "WTW/Willis", 2 attendees → `socials-tradeshow-wtw-willis`
- Event "WTW/Willis", 1 attendee "Alex Craiu" → `socials-tradeshow-wtw-willis-alex-craiu`
- Event "SMICG", no attendee → `socials-tradeshow-smicg`

Use lowercase, strip punctuation, replace spaces with hyphens. The folder name and JPG filename are identical to the artboard name.

---

## Important Notes

- **Never modify master artboard (index 0, `socials-default`).** All work is on the copy.
- **Always clean up before duplicating.** `selectall` grabs items from ALL artboards. Remove all art outside master artboard bounds and delete extra artboards first — otherwise translate puts the paste in the wrong place and the export is all white.
- **masterRect origin is NOT always [0,0].** The artboard may be centred (e.g. `[-600,0,600,-1400]`). Always derive `newLeft` and `dx` from `masterRect` values, never hardcode 0.
- **Use `doc.textFrames` not `layer.textFrames`.** Pill text frames are nested inside sub-layers; `layer.textFrames` only returns direct children and misses them. `doc.textFrames` searches all levels. Match by placeholder content + x-position in new artboard.
- **Use `doc.pathItems` not `layer.pageItems` for pill backgrounds.** Pill background paths are deeply nested; `layer.pageItems` returns 0 items. `doc.pathItems` searches all levels. Filter by: cx within new artboard + width > 400px + y-center within 100px of text frame.
- **Pill resize: center anchor + restore left edge only.** `Transformation.LEFT` is unreliable. Use `bgPath.resize(scaleX, 100, true, false, false, false, 100)` (7 args, center anchor), then set `bgPath.left = origLeft`. Do NOT set `bgPath.height` — setting height after a non-proportional width resize triggers Illustrator's proportional rescale, undoing the width change (this breaks shrink operations while grow works fine).
- **Country pill shows "City, Country" not ISO code.** Format: `"Crawley, UK"`, `"Istanbul, Turkey"`, `"Dubai, UAE"` etc. Use the country abbreviation table in the JS.
- **Always write osascript to a .scpt file and call `osascript /tmp/file.scpt`.** Inline heredoc osascript fails with "Expected end of line" errors when the JS path contains spaces.
- **Unlock all layers at the start of every osascript block.** Locked layers are invisible to `textFrames`, `pageItems`, and placed item operations — operations silently fail on locked layers.
- **Skip cancelled events.** Never generate for `status = "Cancelled"`.
- **Multiple attendees:** If `staff_names` has multiple names (comma-separated), put ALL attendees in one artboard (stacked Name\rTitle pairs in a single text frame). Use event-only naming (no attendee suffix). Never generate separate files per person.
- **Attendee title style:** Use the full job title verbatim — never truncate (e.g. "Market Development Director" not "Dir."). Title line is white 48pt — always read and reapply styles from the placeholder paragraphs, never hardcode colours.
- **Never set `tfAttendee.height`** — it stretches the text frame. Set content and reapply character styles only; let the frame reflow naturally.
- **Multi-attendee vertical offset:** After setting content, if `attendees.length > 1`, call `tfAttendee.translate(0, (attendees.length - 1) * 100)` to shift the frame upward (y-up positive = up) and prevent it overlapping the pills below.
- **BG photo:** stretch clipping mask to full artboard (abW × abH), apply Gaussian blur radius 10, set clipGroup opacity to 15%. After updating, use `clipGroup.move(bgLayer, ElementPlacement.PLACEATEND)` to put it at the front of the BG layer (PLACEATEND = highest index = frontmost within that layer). The BG layer is the bottommost layer, so this makes the photo sit above the solid blue rect but below every other layer. **Layer item order:** index 0 = backmost, last index = frontmost. PLACEATEND = front, PLACEATBEGINNING = back.
- **No event logo:** If scraping fails or `event_website_url` is null, skip Step 7. The copy's placeholder group (pasted from master) remains at the correct position — that's acceptable.
- **No Unsplash result:** If photo search fails for the city, try the country name. If still no result, ask the user to provide a photo path.
- **"last pageItem" pattern:** After paste+translate, each layer has (master's item + copy's item). The copy is always the LAST index in `pageItems` and `textFrames` arrays. Never access by index 0 for editable content.
- **BG clipping group search: always filter by size `w>500 && h>500`.** Small pill icon clipping groups (world map icon etc.) also have `clipped=true` and appear in `doc.pageItems` before the large BG group — without the size filter you'll replace a tiny icon instead of the background photo.
- **BG clipping mask:** Mask path is always first child (index 0). Remove all children from index 1 upward. Never remove index 0.
- **Never use MCP export tool** — always export via `ExportOptionsJPEG` in osascript.
- **Filename spaces:** Illustrator converts spaces to dashes on export. Always `mv` to the final name immediately after export.
- **Artboard placement:** Always to the right of the rightmost existing artboard with 40px gap. Check ALL artboard rects before placing — never overlap.
- **Country ISO codes:** Display uppercase in the `[Country]` text field (e.g., `TR`). The world map icon in the pill is static — never modify it.
- **Date display:** If `start_date == end_date`, show a single date. Never show "12 May – 12 May".
