# contrast-mcp

MCP server for the [Contrast](https://www.getcontrast.io) webinar platform, used to plan
TrustFlight webinars and pull the details needed for LinkedIn promo posts and event graphics.

Contrast is the webinar platform itself, not Contrast Security. The two are unrelated products
that share a name, so ignore any `contrastsecurity.com` documentation you find while searching.

---

## Install

```bash
cd contrast-mcp
npm install
cp .env.example .env
# paste the real key into .env, then:
npm run check-auth
```

`check-auth` proves the credential works before Claude ever calls the server. It prints the
resolved auth header and path prefix, or an explanation of what failed.

### Register with Claude Code

The repo ships a project scoped `.mcp.json`, so launching Claude Code from the repo root picks the
server up automatically. Approve it when prompted, then confirm with `/mcp`.

To register it globally instead:

```bash
claude mcp add contrast --scope user -- node /Users/alexcraiu/Desktop/Claude\ Playground/contrast-mcp/server.js
```

---

## Credentials

The key is read from `CONTRAST_API_KEY`, sourced from the environment or from a `.env` file next to
the server (`contrast-mcp/.env`) or at the repo root. `.env` is gitignored.

Never commit the key, and never paste it into a chat, an issue or a commit message. If it has been
exposed, rotate it in Contrast and update `.env`.

---

## Tools

| Tool | Purpose |
|------|---------|
| `contrast_check_auth` | Verify the credential and resolve the auth header and path prefix. Run first. |
| `contrast_list_webinars` | List webinars, soonest first, filtered by `upcoming`, `past` or `all`. |
| `contrast_get_webinar` | Full record for one webinar by id or slug. |
| `contrast_promo_brief` | Promo ready fields for one webinar. The handoff into the graphics skills. |
| `contrast_list_recurring_events` | Recurring webinar series, for planning a repeating slot. |
| `contrast_list_registrations` | Registrations, optionally for one webinar, with a count. |
| `contrast_list_views` | Views and attendance records. |
| `contrast_list_polls` | Polls and their results. |
| `contrast_list_chat_messages` | Chat and Q&A messages. |
| `contrast_request` | Escape hatch: call any path directly with the resolved credential. |

### Typical planning flow

1. `contrast_check_auth` once after install or after rotating the key.
2. `contrast_list_webinars` with `when: "upcoming"` to see what is scheduled.
3. `contrast_promo_brief` on the chosen webinar.
4. Feed the brief into `asip-webinar-generator` for the thumbnail and ad sizes, or
   `linkedin-event-generator` for an event graphic, or `carousel-builder` for a recap carousel.

`contrast_promo_brief` returns dates already formatted to house style, so the graphics skills do not
need to reformat them:

- same day: `12 May 2026`
- same month: `12–14 May 2026` (en dash, no spaces)
- across months: `29 May – 2 Jun 2026` (en dash, spaces either side)

Dates and times are read in the webinar's own timezone, so an evening webinar does not report the
wrong day.

---

## How the API shape is resolved

The Contrast API reference at `docs.getcontrast.io` sits behind a login wall and could not be read
when this server was written. Two things were therefore left to be resolved at runtime rather than
hard coded to a guess:

**Auth header.** On first use the server probes `Authorization: Bearer <key>`, `X-API-Key`, `Api-Key`
and a raw `Authorization: <key>`, keeps the first that answers with 2xx, and caches the result in
`~/.contrast-mcp/resolved.json`. Later calls reuse it. Delete that file, or call
`contrast_check_auth`, to re-resolve after a change.

**Path prefix.** The same probe tries `/v1`, no prefix, `/api/v1` and `/api` against the base URL
`https://connect.getcontrast.io`.

Resource paths default to `/events`, `/recurring-events`, `/registrations`, `/views`, `/polls` and
`/chat-messages`, matching the resource names Contrast documents. Each one is individually
overridable via a `CONTRAST_PATH_*` env var (see `.env.example`) if a path turns out to differ, and
`contrast_request` reaches anything the named tools miss.

Field names are read defensively. Each field in a promo brief is looked up across the plausible key
spellings (`starts_at`, `startsAt`, `start_time`, `start_date`, and so on), and the untouched API
record is always returned as `raw`, so nothing is lost if the real schema differs from the
assumptions here.

### If `check-auth` fails

The report distinguishes the three causes rather than blaming the key for all of them:

- **Same status for every combination.** Something answered ahead of Contrast: a proxy, VPN,
  firewall or egress allowlist. Confirm you can reach `connect.getcontrast.io` from the machine.
- **401 or 403 on a path that answered.** The key is wrong, revoked, or scoped to another workspace.
- **404 everywhere.** The base URL or the resource paths differ. Override them with
  `CONTRAST_API_BASE_URL` and the `CONTRAST_PATH_*` vars.

Each attempt in the report includes the URL tried and the first 200 characters of the response body,
which usually names the real cause.
