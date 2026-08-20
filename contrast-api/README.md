# contrast-api

Python client for the [Contrast](https://www.getcontrast.io) webinar platform, used to plan
TrustFlight webinars and pull the details needed for LinkedIn promo posts and event graphics.

Contrast is the webinar platform itself, not Contrast Security. The two are unrelated products that
share a name, so ignore any `contrastsecurity.com` documentation you find while searching.

Standard library only. There is nothing to install.

---

## Setup

```bash
cd contrast-api
cp .env.example .env      # paste the real key in
python3 contrast_api.py check-auth
```

`check-auth` proves the credential works and caches the resolved auth header and path prefix. Run it
once after setup and again after rotating the key.

The key is read from `CONTRAST_API_KEY`, sourced from the environment or from a `.env` file next to
the script or at the repo root. `.env` is gitignored. Never commit the key or paste it into a chat,
an issue or a commit message. If it has been exposed, rotate it in Contrast and update `.env`.

---

## Command line

```bash
python3 contrast_api.py check-auth
python3 contrast_api.py list-webinars --when upcoming --limit 10
python3 contrast_api.py list-webinars --when past
python3 contrast_api.py webinar asip-launch          # full record, by id or slug
python3 contrast_api.py promo-brief asip-launch      # promo-ready fields
python3 contrast_api.py recurring-events
python3 contrast_api.py registrations --event-id evt_1
python3 contrast_api.py views --event-id evt_1
python3 contrast_api.py polls --event-id evt_1
python3 contrast_api.py chat-messages --event-id evt_1
python3 contrast_api.py get /events/evt_1 --query '{"limit": 1}'
```

Every subcommand prints JSON on stdout and diagnostics on stderr, so output pipes cleanly into `jq`
or another script. A failure exits non-zero.

`get` is the escape hatch: it calls any path with the resolved credential, for endpoints the named
subcommands do not cover or if Contrast changes a path.

---

## As a module

```python
from contrast_api import list_webinars, get_webinar, promo_brief, list_for_event, request

for webinar in list_webinars(when="upcoming", limit=5):
    print(webinar["title"], webinar["date_formatted"], webinar["registration_url"])

brief = promo_brief(get_webinar("asip-launch"))
regs = list_for_event("registrations", event_id="evt_1")
raw = request("GET", "/events", query={"limit": 10})
```

`promo_brief()` keeps the untouched API record under `raw` by default. The CLI omits it unless you
pass `--raw`, to keep terminal output readable.

---

## What you get back

`list-webinars` and `promo-brief` return normalised fields rather than the raw payload:

| Field | Notes |
|-------|-------|
| `id`, `slug`, `title`, `subtitle`, `description`, `status` | |
| `starts_at`, `ends_at`, `timezone` | As the API reports them |
| `date_formatted` | House style, read in the webinar's own timezone |
| `time_formatted` | For example `14:00 BST` |
| `duration_minutes`, `is_upcoming` | Derived |
| `registration_url`, `replay_url`, `cover_image_url` | |
| `speakers` | List of `{name, title, company, avatar_url}` |
| `registration_count`, `view_count` | Present only if the API supplies them |
| `raw` | The untouched API record |

Dates follow house style, so the graphics skills do not reformat them:

- same day: `12 May 2026`
- same month: `12–14 May 2026` (en dash, no spaces)
- across months: `29 May – 2 Jun 2026` (en dash, spaces either side)

Dates and times are read in the webinar's own timezone, so an evening webinar does not report the
wrong day.

---

## Typical planning flow

1. `check-auth` once after setup.
2. `list-webinars --when upcoming` to see what is scheduled.
3. `promo-brief <id>` on the chosen webinar.
4. Feed the brief into `asip-webinar-generator` for the thumbnail and ad sizes,
   `linkedin-event-generator` for an event graphic, or `carousel-builder` for a recap carousel.

For post-webinar content, `polls` and `chat-messages` are the audience telling you what they cared
about, and `views` against `registrations` gives the show-up rate.

---

## How the API shape is resolved

The Contrast API reference at `docs.getcontrast.io` sits behind a login wall and could not be read
when this client was written. Two things were therefore left to be resolved at runtime rather than
hard coded to a guess:

**Auth header.** On first use the client probes `Authorization: Bearer <key>`, `X-API-Key`,
`Api-Key` and a raw `Authorization: <key>`, keeps the first that answers with 2xx, and caches the
result in `~/.contrast-api/resolved.json`. Later calls reuse it. Delete that file, or run
`check-auth`, to re-resolve.

**Path prefix.** The same probe tries `/v1`, no prefix, `/api/v1` and `/api` against the base URL
`https://connect.getcontrast.io`.

Resource paths default to `/events`, `/recurring-events`, `/registrations`, `/views`, `/polls` and
`/chat-messages`, matching the resource names Contrast documents. Each is individually overridable
via a `CONTRAST_PATH_*` env var (see `.env.example`), and `get` reaches anything else.

Field names are read defensively. Each field in a brief is looked up across the plausible key
spellings (`starts_at`, `startsAt`, `start_time`, `start_date`, and so on), and `raw` always carries
the original record, so nothing is lost if the real schema differs from the assumptions here.

Sub-collections try a nested route first (`/events/<id>/registrations`) and fall back to the flat
collection filtered by `event_id`. Paginated collections are followed by cursor; a non-paginated
endpoint costs exactly one request.

### If check-auth fails

The report distinguishes the causes rather than blaming the key for all of them:

- **Nothing returned an HTTP status.** The connection failed below HTTP: DNS, TLS, VPN, or a proxy
  refusing the tunnel. The underlying error is quoted in the diagnosis.
- **The same status for every combination.** Something answered ahead of Contrast, such as a proxy
  or firewall. Confirm you can reach `connect.getcontrast.io` from the machine.
- **401 or 403 on a path that answered.** The key is wrong, revoked, or scoped to another workspace.
- **404 everywhere.** The base URL or resource paths differ. Override them with
  `CONTRAST_API_BASE_URL` and the `CONTRAST_PATH_*` vars.

Each attempt in the report includes the URL tried and the first 200 characters of the response body,
which usually names the real cause.
