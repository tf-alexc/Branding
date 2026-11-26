---
name: social-motion-generator
description: Make animated TrustFlight, Kenyon, Baines Simmons and Redline social media posts as Claude Motion films (MP4 or GIF), in the Graphics Generator's format and look from the Master Brand System. Covers event and tradeshow posts (Attending or Exhibiting) and national, public and bank holiday posts (Single slide or Multi-slide). Use whenever someone asks for an animated, moving or video version of a social post, event post, tradeshow post, holiday post or LinkedIn graphic.
---

# Social motion generator

Animated versions of the Graphics Generator's social posts, made as Motion artifacts. The static Graphics Generator is the source of truth for layout, sizes, colours and type; this skill adds timing. Simple transitions only: fades, eased slides, small scale-ins. No music, sound or voice. Films run 10 s at most; a Multi-slide holiday post 15 s at most.

The film code is fixed and lives in this skill: `build_film.py` writes every document a film needs from a short JSON spec, using `templates/` and `assets/`. Don't redesign the layout or the animation for a new post; fill in the spec. Exact sizes and timings are in `reference.md` if something needs checking or changing.

**What it makes (all 1200x1600, LinkedIn Single):**

| Kind | Option | Length | What happens |
|---|---|---|---|
| Tradeshow | Attending / Exhibiting | 10 s | Logo, event logo, tag, title, people, then date/location/venue (and booth) pills land by about 4 s and hold. Background slowly zooms, wavy lines sway |
| Holiday | Single slide | 10 s | Logo tab and URL, flag, "Celebrating" between rules, holiday title; holds over a slowly moving photo |
| Holiday | Multi-slide | 15 s | The single-slide post as the first slide, then at 4.5 s a short warm sentence, then at 10.7 s "Happy [holiday]!" held to the end, ideally over a second photo |

**Sources** (anyone in the organisation can open these):
- Design system: https://claude.ai/artifact/3TSvubnBz4WCsS1xD7o3b9
- Motion artifact type: https://claude.ai/artifact/S4skLPbN9WeoFmuiTfaEFy
- Events tracker API: `https://p01--events-tracker--xzp2zkf8b975.code.run/api/events`

## 1. Gather the facts

Fill what you can from the request, an event link or the events API, then ask once, in one message, for anything still missing. Never ask again for something already answered.

**Tradeshow**
- **Brand:** `trustflight`, `kenyon`, `bainessimmons` or `redline`. From the request, the event's `business_unit`, or the link.
- **Mode:** Attending (default) or Exhibiting. Exhibiting needs the booth number.
- **Event:** name (the title), dates, city and country (US: city, state code, USA), venue. Dates read `13–15 Apr 2027`, `29 May – 2 Jun 2027` (en dash); the script uppercases them. Only future dates.
- **People (up to 6):** names only. The script takes their title, brand and portrait from the design system's `employees.json`. Never invent attendees: if nobody is named (the API's `staff_names` is often empty), ask who is going. Someone not in `employees.json`: ask once for their photo and title.
- **Event logo:** the site's header logo, as PNG, white version if there is one. If the logo is dark on a light background, set `event_logo_white` (the generator's White knock-out). Warn the user if the only logo is small (under about 300px tall), as it will look soft.
- **Photo (optional):** the venue or city, from Pexels or Unsplash, free licence only (never Unsplash+, Wikipedia or Wikimedia). Never a photo showing another company's characters, rides or logos. Note the photographer for the caption credit. The API keys are `PEXELS_API_KEY` / `UNSPLASH_ACCESS_KEY` if set; if neither works, ask the user for a photo or go without (the plate alone is fine).

**Holiday**
- **Option:** Single slide or Multi-slide. Ask unless the request says; default Single slide.
- **Brand:** from the request; ask once if unclear.
- **Title:** the holiday's name ("Thanksgiving", "Christmas", "Bank Holiday"). Subtitle stays "Celebrating".
- **Flags:** `us`, `ca`, `gb`, several or none. Presets: Independence Day and Thanksgiving → `us`, Remembrance Day → `gb`, Christmas and New Year → none.
- **Photo:** the user's own if they send one (landscape photos are centre-cropped to portrait, so look at the crop). Otherwise the design system's preset `assets/imagery/holiday/holiday-<independence-day|thanksgiving|remembrance|christmas|new-year>.jpg`, or a free Pexels/Unsplash photo.
- **Multi-slide only:** the sentence for slide 2, the closing line, and (optional, encouraged) a second photo.
  - The sentence is one warm, human, professional sentence of 12-18 words, short enough to read in about 4 s. The script warns above 18.
  - The closing line is "Happy [holiday]!" unless the user wants another.
  - The second photo (`closing_photo`) cross-fades in as "Happy [holiday]!" appears. Pick one that fits the holiday but differs from the first (another scene, colour or distance), from the same sources and rules as the first photo. The logo colour is picked for each photo on its own. Leave it out and the first photo carries on.
  - Use the user's wording when given. Otherwise see "Holiday messaging" below.

### Holiday messaging

Holiday posts go out every year for four brands, so the wording must not repeat. Before writing, look at what that brand already said for the same holiday (the film names in the user's gallery, Artifact `list`, and the retyped lines in those films' `modules/retyped.json`) and don't reuse a sentence or its shape.

Suggest three different options in one message and let the user pick or mix. Each takes a different angle, for example:
- the people behind the work (crews, engineers, responders, trainers, the brand's own team);
- the brand's own world: safe flights home, the families waiting at arrivals, a quiet hangar on a holiday night, a course finished before the break;
- something specific to the holiday (harvest and a shared table for Thanksgiving, remembrance and service for Remembrance Day, a fresh start for New Year);
- a plain, short thank-you to customers and partners, in a new form.

Rules for every option:
- Write for the brand: TrustFlight (aviation software and the people who keep fleets airworthy), Kenyon (crisis and family assistance, bringing people home), Baines Simmons (aviation safety training and consulting), Redline (aviation security training).
- Vary the opening. Not every sentence starts "This [holiday], we're grateful…".
- Warm and plain: no puns that undercut the occasion, no hype, no em dashes, none of the banned words in the project's writing rules. Solemn holidays (Remembrance Day, Memorial Day) get a respectful line, never a cheerful one.
- Never mention a real event, number or person that isn't given.

## 2. Prepare the files

1. Download what the script needs from the design system with Artifact `read` (`url` = the design system, `paths` = the list), all in one call. It saves them under a folder ending in `project/`; that folder is `--ds` below.
   - Always: `project/assets/portraits/employees.json`, the brand's logos (`project/assets/logos/<file>` for both names in the table in `reference.md`).
   - Tradeshow: `project/assets/icons/icon-date.svg`, `icon-location.svg`, `icon-booth.svg` (Exhibiting), `project/assets/icons/flags/<country>.svg` (keys: usa, uk, canada, mexico, brazil, argentina, france, spain, italy, belgium, poland, china, thailand, australia; other countries get the pin icon, so leave `flag` out), and each person's `portraitWindow` file from `employees.json`.
   - Holiday: `project/assets/imagery/holiday/flag-<us|ca|gb>.svg` for each flag, and the preset photo if used.
2. Save the event logo and photo into the scratchpad (never the user's folders).
3. Write the spec to the scratchpad and run the script (Python 3 with Pillow and numpy):

```bash
python3 <this skill>/build_film.py prepare spec.json --ds <…/project> --out <scratchpad>/film
```

Tradeshow spec:

```json
{"kind": "tradeshow", "brand": "trustflight", "mode": "attending",
 "title": "MRO Americas", "event_logo": "/path/event-logo.png", "event_logo_white": false,
 "photo": "/path/city.jpg",
 "people": [{"name": "Thomas Lemaire"}, {"name": "Lee Russell"}],
 "dates": "13–15 Apr 2027", "location": "Orlando, FL, USA", "flag": "usa",
 "venue": "Orange County Convention Center", "booth": "1234"}
```

Holiday spec:

```json
{"kind": "holiday", "option": "multi-slide", "brand": "trustflight",
 "title": "Thanksgiving", "flags": ["us"], "photo": "/path/photo.jpg",
 "closing_photo": "/path/second-photo.jpg",
 "message": "To everyone who keeps aircraft flying and people safe this Thanksgiving, thank you.",
 "closing": "Happy Thanksgiving!"}
```

`option` is `single-slide` or `multi-slide` (the older names `base` and `complex` still work). `closing_photo` is optional (Multi-slide only). Optional keys: `brands` (a list of brand keys when one post covers several brands; it sets the film name), `film_title` (overrides the name), `title_px` (tradeshow title size; the script shrinks long titles itself), and per person `title`, `brand` or `portrait` to override `employees.json`.

The script picks the people layout from the head count, the holiday logo colour from the photo (white on dark, Midnight on light), the title sizes, and escapes names safely (O'Connell, &). It prints the files to upload.

## 3. Make the film

Follow the Motion type's own instructions as you go (read its SKILL.md, rough-cut.md, finalize.md, motion.md, film-api.md and design-systems.md once). This skill already settles Style, Colours and Length (the brand's Graphics Generator look, the brand palette, 10 s, or 15 s for Multi-slide), so there's no question form: say the picks in one line and go on.

1. **Create** the film: Artifact `publish` with `type_url` = the Motion type, `title` = the film title the script printed, `auto_open: "after_first_write"`. Film names follow `<Type> - <Brand(s)> - <name>`: `Tradeshow - Kenyon - Verticon 2027`, `Holiday - TrustFlight - Thanksgiving`, `Holiday - TrustFlight, Kenyon - Christmas`, and `Holiday - All - Thanksgiving` when all four brands are on the post. The script builds this; keep it if you name a film by hand.
2. **Upload** the files from `<out>/upload/` in one Artifact call: `url` = the film, `asset: true`, `file_paths: [...]`.
3. **Map the blob ids:** write `blobs.json` as `{"<file name>": "<32-character id>", ...}` from the upload reply, then run:

```bash
python3 <this skill>/build_film.py assets <scratchpad>/film --blobs blobs.json
```

4. **One batch** (ArtifactData `batch`, `url` = the film): `writes` = the contents of `<out>/writes.json`. It holds the meta, the rough scene list, styles, shared code, logo/icon/flag modules, the image records and the script.
5. **The scene:** ArtifactData `set` of `modules/scene-post.js` (tradeshow) or `modules/scene-holiday.js` (holiday) with `file_path` = `<out>/docs/scene.json`.
6. **Finish:** ArtifactData `set` of `modules/scenes.json` with `if_version` from the batch reply and `file_path` = `<out>/docs/scenes-final.json`. No score: the films are silent.

## 4. Deliver

Give the film's link. Say:
- Export (the download arrow on the film's page) saves an MP4 or GIF.
- The film is private until shared from the page's Share menu.
- What was assumed or made up (placeholder wording, a soft logo, the photo and its photographer).

Offer the LinkedIn caption: 50-150 words, up to five hashtags, only the five set emoji (📅 date, 🔹 list item, 📍 venue, 👉 read more, ✏️ get in touch), with the photo credit if a stock photo was used.

## Changing the films later

Small changes go straight into the film's modules (later turns follow the Motion type's `later.md`). If a change should apply to every future film (a timing, a layout rule), change `build_film.py` or `templates/` too, update `reference.md`, and tell the user so the shared skill can be re-published.

Words retyped by hand on a film's page are stored in `modules/retyped.json` and shown in place of the code's words. Read it before changing a line, and start from the retyped wording.
