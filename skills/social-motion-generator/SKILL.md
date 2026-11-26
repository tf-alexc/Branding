---
name: social-motion-generator
description: Make animated TrustFlight-family social media posts as Claude Motion films, using the format, look and layout of the Graphics Generator in the Master Brand System. Covers event and tradeshow attendance posts (Attending / Exhibiting) and national, public and bank holiday posts. Use whenever the user asks for an animated, moving or video version of a social post, event post, tradeshow post, holiday post or LinkedIn graphic.
---

# Social motion generator

Animated versions of the Graphics Generator's social posts, built as Motion artifacts (Claude Motion). The static generator is the source of truth for layout, sizes, colours and type; this skill only adds timing. Simple transitions only: fades, eased slides, small scale-ins. No music, no sound, no voice.

**Formats live so far:** Tradeshow (R21) and Holiday (R33-R39), both LinkedIn Single, 1200x1600. Other purposes (blog, webinar, course) follow the same pattern later. The holiday post has its own section near the end.

**Design system:** https://claude.ai/artifact/3TSvubnBz4WCsS1xD7o3b9
**Layout rules:** `project/assets/docs/templates/graphics-generator/RULES.md` (R20-R32, R40-R41)
**Layout markup:** `project/templates/graphics-generator/GraphicsGenerator.dc.html` (the `is1600` stage, `isCourse` / `isTradeshow` blocks)
**Motion type:** https://claude.ai/artifact/S4skLPbN9WeoFmuiTfaEFy
**Events API:** `https://p01--events-tracker--xzp2zkf8b975.code.run/api/events`
**Reference films (one per brand, same code):**
- TrustFlight: https://claude.ai/artifact/84frbVjkVAQzS4WvpRzQUG (MRO Americas 2027)
- Kenyon: https://claude.ai/artifact/AXVqhDxsCmCMEbf9gjeqjB (Verticon 2027)
- Baines Simmons: https://claude.ai/artifact/U2ZB4gr2xueBpZqTaHPtQZ (UKFSC Safety Information Exchange 478)
- Redline: https://claude.ai/artifact/AhT2rTsnK6g3sUzVeSdJpb (Public Protection Week)

## Brands

Only the brand logo and the URL change between brands. Plate, strip, colours, type and timing are the same for all four (the generator does the same).

| Brand | Logo (white) | URL |
|---|---|---|
| TrustFlight | `trustflight-logo-horizontal-white.svg` | TRUSTFLIGHT.COM |
| Kenyon | `kenyon-120-logo-white.svg` (anniversary lockup, per CLAUDE.md) | KENYONINTERNATIONAL.COM |
| Baines Simmons | `baines-logo-white.svg` | BAINESSIMMONS.COM |
| Redline | `redline-logo-white.svg` | TRUSTREDLINE.CO.UK |

In the scene, the brand logo is always the module `brand-logo.txt`. A new film is the reference film for its brand with the event, people, pills and assets swapped.

Event logos: use the site's white version when there is one. A dark-on-light logo gets the generator's White knock-out (`style="filter:brightness(0) invert(1)"` on `.ts-evlogo`). Upscale any logo under 300px tall to 300px before upload, and warn the user if it was small to begin with (it will be soft).

Long titles (R18, two rows max): drop the title size from 92px. Roughly, at 1020px wide, a 2-row title fits about 2040 / (0.47 × characters) px. The UKFSC title (58 characters) uses 68px.

Photos: never use a photo showing another company's characters or rides (Disney etc.).

To build a new film, `get` the brand's reference film's `base.css`, `shared.js` and `scene-post.js` with ArtifactData (`out_dir` to the scratchpad), then in Python swap by exact string replacement: the `W.person(...)` lines, the `.post-p1`, `.post-p2` list, the `W.pill(...)` lines, the event logo file, the title and the URL. Set the people layout class on `.ts-people` (`ts-solo`, `ts-cols`, `ts-cols ts-cols3`, or none for 4-6). Write the results back with `file_path` entries in a batch.

---

## Step 1: Gather the facts

Same inputs as the static generator. Fill everything you can before asking, then ask once for what is missing.

- **Event:** from the events API, an event link the user gives (R28), or their message. Name, dates, city, country (US: add the state, R30), venue, booth (Exhibiting only).
- **Mode:** Attending (default) or Exhibiting. Exhibiting adds the BOOTH pill.
- **Brand:** from the event's `business_unit`, the request or the link. Logo per CLAUDE.md (Kenyon: `kenyon-120-logo-white.svg`).
- **People (up to 6):** from `assets/portraits/employees.json`, title exactly as written. Use the `portraitWindow` file. The API's `staff_names` is names only. If nobody is named, ask who is attending. Never put placeholder people in a post that will be published.
- **Event logo:** the site header logo (white version if there is one), fetched at about 500px high as PNG.
- **Background photo:** venue, else city, from Pexels or Unsplash (free licences only). Keep the photographer for the caption credit.

Date pill format: `13–15 APR 2027` (same month), `29 MAY – 2 JUN 2027` (across months), uppercase, en dash. Only future dates (R13).

## Step 2: Prepare assets locally

Work in the scratchpad. Pull from the design system with Artifact `read` (`paths`):

- `project/assets/imagery/course-bg-tall.jpg` (the plate)
- `project/assets/logos/<brand>-logo-horizontal-white.svg` (or the brand's white logo)
- `project/assets/icons/icon-date.svg`, `icon-location.svg`, `icon-booth.svg` (Exhibiting)
- `project/assets/icons/flags/<country>.svg`
- `project/assets/portraits/<brand>/<slug>-window.jpg` for each person

Then with Python/PIL:

- Photo: cover-crop to 1200x1600, 8-bit sRGB JPEG q78, no metadata.
- Plate: split into `plate-clean.jpg` (no wavy lines) and `plate-lines.webp` (the lines alone, transparent) so the lines can move. The reference film already holds both (assets `plate-clean.jpg`, `plate-lines.webp`); copy them across rather than re-splitting. To redo it:

```python
from PIL import Image, ImageFilter
import numpy as np
im = Image.open('course-bg-tall.jpg').convert('RGB').resize((1200, 1600), Image.LANCZOS)
a = np.asarray(im).astype(np.float32)
m9 = np.asarray(im.filter(ImageFilter.MedianFilter(9))).astype(np.float32)
# clean plate: lower half smoothed (down/up-scale), feathered over 80px, light dither
sm = np.asarray(im.crop((0, 700, 1200, 1600)).resize((60, 45), Image.BILINEAR).resize((1200, 900), Image.BICUBIC)).astype(np.float32)
clean = a.copy(); clean[700:] = sm
for i in range(80): clean[700 + i] = a[700 + i] * (1 - i / 80) + sm[i] * (i / 80)
clean += np.random.default_rng(1).normal(0, 0.6, clean.shape)
Image.fromarray(np.clip(clean, 0, 255).astype(np.uint8)).save('plate-clean.jpg', quality=90)
# lines: what is brighter than its 9px median, below y=760, cropped from y=740
d = np.clip(a - m9, 0, None).max(axis=2); d[:760] = 0
al = np.clip(d / np.percentile(d[800:], 99.5), 0, 1); al[al < 0.08] = 0
Image.fromarray(np.dstack([a, al * 255]).astype(np.uint8)[740:]).save('plate-lines.webp', quality=85)
```
- Portraits: re-save as JPEG q86.
- Event logo: keep as RGBA PNG.

SVGs are never uploaded. Strip `<?xml …?>` and any `<metadata>` block (the location icon carries a large C2PA block) and write each as a text module.

## Step 3: Create and fill the film

Follow the Motion type's own SKILL.md and reference pages (questions.md, rough-cut.md, finalize.md, motion.md, film-api.md, design-systems.md). The request names the design system and the Graphics Generator look, so there is no Style/Colors/Length form: state the picks in one line and go.

1. Create: Artifact `publish` with the Motion `type_url`, title `<Event> attending` (or exhibiting), `auto_open: "after_first_write"`.
2. First batch (ArtifactData): `film/meta`, `modules/scenes.json` (`stage: rough`), short `modules/base.css`, `film/script` = `window.CUT = kit.scenes();`.
3. Upload rasters in one Artifact call: `asset: true`, `file_paths: [plate, photo, event logo, portraits]`.
4. Second batch: one `assets/<file>` doc per upload (`{ref, mime, w, h}`), one `modules/<name>.txt` per SVG, full `base.css`, `shared.js`. Build the asset and SVG docs as JSON files with Python and pass them as `file_path` entries, so no SVG is retyped by hand.
5. `modules/scene-post.js` with one `set`.
6. Final batch: `scenes.json` with `stage: final`. No `score.js` (silent).

### scenes.json

```
width 1200, height 1600, fps 30, background #031022
palettes [["#031022","#03D4FF","#FFFFFF","#1E5BB5"]], theirs 1
fonts: display Titillium Web [300,400,700], sans Open Sans [400,700], both "or": "instrument-sans"
one scene, id "post", dur 12
```

### Layout (copy from the generator, don't adjust)

| Element | Spec |
|---|---|
| Plate | `plate-clean.jpg`, cover, inset -2px |
| Wavy lines | `plate-lines.webp` over the plate, under the photo: left -70, top 700, 1340x960 (oversized so the sway never shows an edge), transform-origin bottom centre |
| Photo | top/left -40px, 1280x1680, cover, opacity 0.2, blur 4px |
| Brand logo | top 95, left 90, height 60.75 |
| Column | top 300, left 90, width 1020, flex column, gap 28 |
| Event logo | height 250 (width capped 1020), left-aligned |
| Tag | ATTENDING / EXHIBITING, Titillium Bold 24.4px, 0.12em, 66px high, padding 0 37, 2px Electric outline, Midnight 50% fill |
| Title | Titillium Light 92px, line-height 1.1, white |
| People: 1 (`ts-solo`) | the generator's row layout at 150%: portrait left, name, title and brand on the right. Frame 189.75x265.65 (3px Electric), gap 24.15; name 58.65px; title and brand 34.5px |
| People: 2 (`ts-cols`) | 2-column grid, gap 46. Each column: big portrait on top, name, title and brand underneath (left-aligned, gap 22). Frame 230x322; name Titillium 46px Electric; title and brand Open Sans 27px |
| People: 3 (`ts-cols ts-cols3`) | as 2, in 3 columns: frame 200x280, name 38px, title 22px |
| People: 4 | the generator's wrapping row (frame 126.5x177.1, name 39.1px, title 23px) |
| People: 5-6 | the generator's 2-column grid (frame 105.8x148.35, name 31.05px, title 18.4px) (R25) |
| Column fit (R11) | `W.fit(col, pills)` at the end of the async `init`: after fonts load, scales the column from its top-left so it ends 56px above the pill row. Never let the column reach the pills |
| Pills | left 90, bottom 130, width 1020, wrap, gap 18; 72px high, padding 0 30 0 20, Dark Blue `#031022`, 2px Electric, radius 36; icon 40px (flag round); Open Sans Bold 22px, 0.1em |
| URL | bottom 70, left 90, Titillium 17px, 0.28em (TRUSTFLIGHT.COM etc.) |
| Strip | bottom, full width, 10px, Sapphire `#1E5BB5` to Electric `#03D4FF` |

Portrait `img`: `object-fit:cover; object-position:center 18%; transform:scale(1.2); transform-origin:center 18%` (R40).

### Timing (10 s, one scene)

The whole post lands at about 4 s, then holds. Approved pace: 6 s was too slow, 2.3 s too fast.

| Time (s) | What moves |
|---|---|
| 0 → 10 | Backdrop settles from scale 1.15 to 1.0 at a constant (linear) rate across the whole film, so it keeps moving to the last frame. No easing: an ease-out makes it look stopped by the end. Keep it clearly visible. |
| 0 → 10 | Wavy lines sway continuously and visibly: translateX ±26px (5 s period), translateY ±14px (4 s), scaleY ±6% from the bottom (4.5 s), skewX ±2° (6 s). `W.lines(el, t)` in `shared.js` |
| -0.6 → 0.4 | Brand logo fades in, drops 14px |
| -0.3 → 1.0 | Strip grows left to right |
| -0.3 → 0.7 | Event logo fades in, rises 34px |
| 0.2 → 0.9 | URL fades in |
| 0.6 → 1.3 | Tag fades in, scales 0.86 → 1 with a small overshoot |
| 1.0 | Title words fade in from the right (`TextFx.fadeFromRight`, dx 30, 0.6 s) |
| 1.9 (+0.35 each) | Portrait frame scales 0.7 → 1 over 0.6 s (overshoot), name and title follow 0.15 s later: slide 28px from the right (1 person) or rise 22px (2-3 people, frame scales from its bottom edge) |
| 2.9 (+0.25 each) | Pills rise 26px and fade in over 0.6 s |
| ~4 → 10 | Hold on the finished post |

Entrances start slightly before 0 so frame 0 (the thumbnail and first MP4 frame) is already branded. Nothing fades out at the end, so the last frame equals the static post.

### Code pattern

`shared.js` sets `window.W` with `svg(kit, module, cls)` (an `<img>` with a `data:image/svg+xml` src from the module text), `backdrop`, `person`, `pill`. The reference film's `shared.js`, `base.css` and `scene-post.js` are the template: read them with ArtifactData `get` and change only the content strings and the asset names.

## Holiday posts (national, public and bank holidays)

Every holiday comes in two options. Ask which one unless the request says; default to Base.

- **Base** (10 s): the generator's holiday post built up and held over a moving photo. Reference: https://claude.ai/artifact/1WAJBxFSMFa6dG3QY4bVHg (TrustFlight, Thanksgiving 2026).
- **Complex** (19 s), three beats: (1) the Base intro; (2) a warm thank-you message; (3) "Happy [holiday]!" at the centre, held to the end. Reference: https://claude.ai/artifact/6U9Dj6QjLFAYtrXHxQsDuA.

Build new holiday films from the matching reference: same `base.css` and `shared.js`, and in `scene-holiday.js` swap the title, subtitle, flag module, brand logo module, URL, photo and (Complex) the celebrating list and the closing line.

### Facts

- **Holiday and title:** the holiday's name as the title (e.g. "Thanksgiving", "Christmas", "Bank Holiday"). Subtitle "Celebrating" (Commemorating is disabled, R38, so Remembrance Day also uses Celebrating).
- **Brand:** from the request; ask once if it isn't clear. A US holiday defaults to TrustFlight.
- **Flag (R39):** US, CA, UK or none, multi-select. Presets: Independence Day and Thanksgiving → US, Remembrance Day → UK, Christmas and New Year → none. Flags: `assets/imagery/holiday/flag-<us|ca|gb>.svg` (strip the C2PA `<metadata>` block before writing the module).
- **Photo:** the user's own photo if they send one (R36; landscape photos are centre-cropped to 1200x1600, so check the crop keeps the subject). Otherwise the preset in `assets/imagery/holiday/holiday-<id>.jpg` (independence-day, thanksgiving, remembrance, christmas, new-year), or the user's own (R36). Otherwise Unsplash or Pexels, free licence only, no other company's characters or logos.

### Layout (from the generator, don't adjust)

| Element | Spec |
|---|---|
| Photo | full bleed, top/left -2px, 1204x1604, cover |
| Fade | `linear-gradient(180deg, transparent 0-42%, rgba(6,41,85,0.55) 62%, rgba(3,16,34,0.92) 82%, #031022 100%)` |
| Logo tab | top/left -2px, height 222, padding 0 90 0 92, outline only: 2px right and bottom border at 35% opacity, bottom-right radius 64. Logo 60px high. Sample the photo's mean luminance in the top-left 600x220: under 0.55 → white logo and white outline, otherwise Midnight logo (`*-midnight.svg`) and Midnight outline (class `hd-light` on the tab) |
| Centred block | left/right 60, bottom 250, centred column |
| Flags | row, 54.6px high, radius 8, gap 20, 40px above the subtitle |
| Subtitle | Titillium Light 52.5px, caps, 0.12em, between 2px rules that fade outward, gap 36, 18px above the title |
| Title | Titillium Bold, caps, 0.04em, line-height 1.02, balanced wrap, two rows max. Size tier 150 / 124 / 100 / 80 / 62px from the title length (`W.titlePx`) |
| URL | centred, bottom 84, Titillium 24px, 0.28em. No bottom strip, no pills, no CTA |
| Beat 2 (Complex) | `.hd-warm.holiday-m1`: one centred sentence at left/right 90, vertically centred, Titillium Light 80px white, line-height 1.14, balanced wrap. No eyebrow or lead-in in another style (no Electric line), and never the intro's "Celebrating" rules-and-caps style. Copy is warm and human but professional, opening with the holiday: e.g. "This Thanksgiving, we’re grateful for our customers, our partners, and the team who keep our skies safe." Keep it to one sentence of about 15-18 words. Take the user's wording if given |
| Beat 3 (Complex) | `.hd-msg.holiday-m2`: "Happy [holiday]!" in the title style (Titillium Bold caps, 0.04em), sized by `W.titlePx` |

### Timing (Base: 10 s, one scene `holiday`)

| Time (s) | What moves |
|---|---|
| 0 → 10 | Photo zooms out 1.15 → 1.0 and rises 40px → 0 at a constant rate, so it keeps moving to the end |
| -0.6 → 0.4 | Logo fades in, drops 14px; tab outline fades in -0.3 → 0.7 |
| 0.7 → 1.3 | Flag fades in and scales 0.8 → 1 with a small overshoot |
| 1.2 → 2.0 | Rules grow outward from the subtitle |
| 1.3 → 2.0 | Subtitle fades in while its tracking tightens 0.3em → 0.12em |
| 2.0 → 3.0 | Title fades in, rising only 12px and scaling 0.985 → 1 (keep it subtle) |
| ~3 → 10 | Hold over the moving photo |

The URL is static: it fades in with the brand logo (-0.6 → 0.4) and never moves.

**Complex option (19 s)** keeps the Base intro as is (photo zoom runs over 0 → 19), then:

| Time (s) | What moves |
|---|---|
| 6.0 → 6.7 | Flag, subtitle and title fade out together and lift 30px (ease in). Logo tab and URL stay |
| 7.0 → ~9.2 | Beat 2: the sentence fades in word by word from the right (`TextFx.fadeFromRight`, stagger 0.09 s, 0.6 s, dx 30) |
| ~9.2 → 13.0 | Hold on beat 2 (time to read it) |
| 13.0 → 13.6 | Beat 2 fades out and lifts 30px |
| 14.0 → 15.0 | Beat 3: "Happy [holiday]!" fades in, rising only 12px and scaling 0.985 → 1 (keep it subtle) |
| 15 → 19 | Hold on beat 3 over the moving photo |

## Step 4: Deliver

Give the film's link and say Export (download arrow) saves MP4 or GIF. Remind the user the artifact is private until shared. Offer the LinkedIn caption per the README rules (50-150 words, up to five hashtags, only the five set emoji), with the photo credit.

## Known issues

- The Unsplash key in the local environment (`UNSPLASH_ACCESS_KEY`) was rejected on 25 Nov 2026; Pexels works.
- The browser pane is not signed in to claude.ai, so the film can't be checked from there. Ask the user to scrub it.
