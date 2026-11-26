# Social motion generator: reference

Exact specs behind `build_film.py` and `templates/`. They copy the Graphics Generator (design system `project/templates/graphics-generator/GraphicsGenerator.dc.html`, rules in `project/assets/docs/templates/graphics-generator/RULES.md`). Change the code and this file together.

## Brands

Only the logo and URL change between brands. Plate, strip, colours, type and timing are the same for all four.

| Spec `brand` | Logo on dark | Logo on light (holiday tab only) | URL |
|---|---|---|---|
| `trustflight` | `trustflight-logo-horizontal-white.svg` | `trustflight-logo-horizontal-midnight.svg` | TRUSTFLIGHT.COM |
| `kenyon` | `kenyon-120-logo-white.svg` (anniversary lockup) | `kenyon-120-logo-rgb.svg` | KENYONINTERNATIONAL.COM |
| `bainessimmons` | `baines-logo-white.svg` | `baines-logo-midnight.svg` | BAINESSIMMONS.COM |
| `redline` | `redline-logo-white.svg` | `redline-logo-midnight.svg` | TRUSTREDLINE.CO.UK |

Film settings: 1200x1600, 30 fps, background `#031022`, palette Dark Blue `#031022`, Electric `#03D4FF`, white, Sapphire `#1E5BB5`. Fonts: Titillium Web (300, 400, 700) for display, Open Sans (400, 700) for text, loaded by the player from Google Fonts. Logos, icons and flags are SVG text modules shown as `<img>` data URIs (never uploaded, never inlined as markup).

## Tradeshow layout

| Element | Spec |
|---|---|
| Plate | `assets/plate-clean.jpg` (the generator's `course-bg-tall.jpg` with the wavy lines removed), cover, inset -2px |
| Wavy lines | `assets/plate-lines.webp` (the lines alone, transparent) over the plate, under the photo: left -70, top 700, 1340x960 (oversized so the sway never shows an edge), transform-origin bottom centre |
| Photo | top/left -40px, 1280x1680, cover, opacity 0.2, blur 4px |
| Brand logo | top 95, left 90, height 60.75 |
| Column | top 300, left 90, width 1020, flex column, gap 28 |
| Event logo | height 250 (width capped 1020), left-aligned. `event_logo_white`: `filter:brightness(0) invert(1)` |
| Tag | ATTENDING / EXHIBITING, Titillium Bold 24.4px, 0.12em, 66px high, padding 0 37, 2px Electric outline, Midnight 50% fill |
| Title | Titillium Light 92px, line-height 1.1, white. Long titles shrink: `min(92, 2040 / (0.52 × characters))` px, two rows max |
| People: 1 (`ts-solo`) | the generator's row layout at 150%: portrait left, name, title and brand on the right. Frame 189.75x265.65 (3px Electric); name 58.65px; title and brand 34.5px |
| People: 2 (`ts-cols`) | 2-column grid, gap 46. Each column: big portrait on top, name, title and brand underneath (left-aligned, gap 22). Frame 230x322; name Titillium 46px Electric; title and brand Open Sans 27px |
| People: 3 (`ts-cols ts-cols3`) | as 2, in 3 columns: frame 200x280, name 38px, title 22px |
| People: 4 | the generator's wrapping row (frame 126.5x177.1, name 39.1px, title 23px) |
| People: 5-6 | the generator's 2-column grid (frame 105.8x148.35, name 31.05px, title 18.4px) |
| Portraits | the `portraitWindow` crop; `object-fit:cover; object-position:center 18%; transform:scale(1.2); transform-origin:center 18%` |
| Column fit | `W.fit(col, pills)` at the end of the async `init`: after fonts load, scales the column from its top-left so it ends 56px above the pill row |
| Pills | left 90, bottom 130, width 1020, wrap, gap 18; 72px high, padding 0 30 0 20, Dark Blue, 2px Electric, radius 36; icon 40px (flag round); Open Sans Bold 22px, 0.1em. Order: dates, location (flag, or pin with no flag), venue, booth (Exhibiting only) |
| URL | bottom 70, left 90, Titillium 17px, 0.28em |
| Strip | bottom, full width, 10px, Sapphire to Electric |

## Tradeshow timing (10 s, scene `post`)

The post lands by about 4 s, then holds. Approved pace: 6 s was too slow, 2.3 s too fast.

| Time (s) | What moves |
|---|---|
| 0 → 10 | Backdrop (plate, lines, photo) scales 1.15 → 1.0 at a constant rate, so it never looks stopped |
| 0 → 10 | Wavy lines sway: translateX ±26px (5 s period), translateY ±14px (4 s), scaleY ±6% from the bottom (4.5 s), skewX ±2° (6 s) |
| -0.6 → 0.4 | Brand logo fades in, drops 14px |
| -0.3 → 1.0 | Strip grows left to right |
| -0.3 → 0.7 | Event logo fades in, rises 34px |
| 0.2 → 0.9 | URL fades in |
| 0.6 → 1.3 | Tag fades in, scales 0.86 → 1 with a small overshoot |
| 1.0 | Title words fade in from the right (dx 30, 0.6 s) |
| 1.9 (+0.35 each) | Portrait frame scales 0.7 → 1 over 0.6 s (overshoot); name and title follow 0.15 s later: slide 28px from the right (1 or 4-6 people) or rise 22px (2-3 people) |
| 2.9 (+0.25 each) | Pills rise 26px and fade in over 0.6 s |

Entrances start slightly before 0 so the first frame (thumbnail, first MP4 frame) is already branded. Nothing fades out, so the last frame matches the static post.

## Holiday layout

| Element | Spec |
|---|---|
| Photo | full bleed, top/left -2px, 1204x1604, cover |
| Fade | `linear-gradient(180deg, transparent 0-42%, rgba(6,41,85,0.55) 62%, rgba(3,16,34,0.92) 82%, #031022 100%)` |
| Logo tab | top/left -2px, height 222, padding 0 90 0 92, outline only: 2px right and bottom border at 35% opacity, bottom-right radius 64; logo 60px high. Photo luminance in the top-left 600x220 under 0.55 → white logo and outline, otherwise the light-background logo and a Midnight outline (`hd-light`) |
| Centred block | left/right 60, bottom 250 |
| Flags | row, 54.6px high, radius 8, gap 20, 40px above the subtitle |
| Subtitle | Titillium Light 52.5px, caps, 0.12em, between 2px rules that fade outward, 18px above the title |
| Title | Titillium Bold, caps, 0.04em, line-height 1.02, two rows max; size tier 150 / 124 / 100 / 80 / 62px from the title length (`W.titlePx`) |
| URL | centred, bottom 84, Titillium 24px, 0.28em. Static: fades in with the logo, never moves. No strip, pills or CTA |
| Complex beat 2 | one centred sentence, left/right 90, vertically centred, Titillium Light 80px white, line-height 1.14. No eyebrow or lead-in in another style, and not the intro's rules-and-caps style |
| Complex beat 3 | "Happy [holiday]!" in the title style, sized by `W.titlePx` |

## Holiday timing

Base (10 s, scene `holiday`):

| Time (s) | What moves |
|---|---|
| 0 → end | Photo zooms out 1.15 → 1.0 and rises 40px at a constant rate |
| -0.6 → 0.4 | Logo and URL fade in (logo drops 14px); tab outline -0.3 → 0.7 |
| 0.7 → 1.3 | Flag fades in, scales 0.8 → 1 with a small overshoot |
| 1.2 → 2.0 | Rules grow outward; subtitle fades in as its tracking tightens 0.3em → 0.12em |
| 2.0 → 3.0 | Title fades in, rising only 12px, scaling 0.985 → 1 (keep it subtle) |

Complex (19 s) adds:

| Time (s) | What moves |
|---|---|
| 6.0 → 6.7 | Flag, subtitle and title fade out and lift 30px. Logo tab and URL stay |
| 7.0 → ~9.2 | The sentence fades in word by word from the right (stagger 0.09 s, 0.6 s, dx 30) |
| ~9.2 → 13.0 | Hold (reading time) |
| 13.0 → 13.6 | Sentence fades out, lifts 30px |
| 14.0 → 15.0 | "Happy [holiday]!" fades in, rising only 12px, scaling 0.985 → 1 |
| 15 → 19 | Hold |

## Rebuilding the plate layers

`assets/plate-clean.jpg` and `assets/plate-lines.webp` come from the design system's `project/assets/imagery/course-bg-tall.jpg`. If that plate changes:

```python
from PIL import Image, ImageFilter
import numpy as np
im = Image.open('course-bg-tall.jpg').convert('RGB').resize((1200, 1600), Image.LANCZOS)
a = np.asarray(im).astype(np.float32)
m9 = np.asarray(im.filter(ImageFilter.MedianFilter(9))).astype(np.float32)
sm = np.asarray(im.crop((0, 700, 1200, 1600)).resize((60, 45), Image.BILINEAR).resize((1200, 900), Image.BICUBIC)).astype(np.float32)
clean = a.copy(); clean[700:] = sm
for i in range(80): clean[700 + i] = a[700 + i] * (1 - i / 80) + sm[i] * (i / 80)
clean += np.random.default_rng(1).normal(0, 0.6, clean.shape)
Image.fromarray(np.clip(clean, 0, 255).astype(np.uint8)).save('plate-clean.jpg', quality=90)
d = np.clip(a - m9, 0, None).max(axis=2); d[:760] = 0
al = np.clip(d / np.percentile(d[800:], 99.5), 0, 1); al[al < 0.08] = 0
Image.fromarray(np.dstack([a, al * 255]).astype(np.uint8)[740:]).save('plate-lines.webp', quality=85)
```

## Example films

Made while building the skill (private to their owner unless shared): TrustFlight tradeshow https://claude.ai/artifact/84frbVjkVAQzS4WvpRzQUG, Kenyon https://claude.ai/artifact/AXVqhDxsCmCMEbf9gjeqjB, Baines Simmons https://claude.ai/artifact/U2ZB4gr2xueBpZqTaHPtQZ, Redline https://claude.ai/artifact/AhT2rTsnK6g3sUzVeSdJpb, Thanksgiving Base https://claude.ai/artifact/1WAJBxFSMFa6dG3QY4bVHg, Thanksgiving Complex https://claude.ai/artifact/6U9Dj6QjLFAYtrXHxQsDuA.
