#!/usr/bin/env python3
"""Client for the Contrast webinar platform API (https://www.getcontrast.io).

Contrast is the webinar platform, not Contrast Security. The two are unrelated
products that share a name, so ignore any contrastsecurity.com documentation.

Standard library only, so there is nothing to install. Use it as a module:

    from contrast_api import list_webinars, promo_brief, get_webinar

    for w in list_webinars(when="upcoming"):
        print(w["title"], w["date_formatted"])

or from the command line:

    python3 contrast_api.py check-auth
    python3 contrast_api.py list-webinars --when upcoming
    python3 contrast_api.py promo-brief <id>
    python3 contrast_api.py get /events/abc123

The published API reference at docs.getcontrast.io sits behind a login wall, so
the auth header and path prefix are resolved at runtime rather than hard coded
to a guess. See README.md for how that works and how to override it.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = os.environ.get("CONTRAST_API_BASE_URL", "https://connect.getcontrast.io").rstrip("/")
TIMEOUT = float(os.environ.get("CONTRAST_TIMEOUT", "30"))
CACHE_FILE = Path.home() / ".contrast-api" / "resolved.json"

# Candidate auth schemes, most likely first. Each is (id, header, value template).
AUTH_SCHEMES = [
    ("bearer", "Authorization", "Bearer {key}"),
    ("x-api-key", "X-API-Key", "{key}"),
    ("api-key", "Api-Key", "{key}"),
    ("raw-authorization", "Authorization", "{key}"),
]

# Candidate path prefixes between the base URL and the resource path.
PATH_PREFIXES = ["/v1", "", "/api/v1", "/api"]

# Resource paths, individually overridable via env.
RESOURCES = {
    "events": os.environ.get("CONTRAST_PATH_EVENTS", "/events"),
    "recurring_events": os.environ.get("CONTRAST_PATH_RECURRING_EVENTS", "/recurring-events"),
    "registrations": os.environ.get("CONTRAST_PATH_REGISTRATIONS", "/registrations"),
    "views": os.environ.get("CONTRAST_PATH_VIEWS", "/views"),
    "polls": os.environ.get("CONTRAST_PATH_POLLS", "/polls"),
    "chat_messages": os.environ.get("CONTRAST_PATH_CHAT_MESSAGES", "/chat-messages"),
}


class ContrastError(RuntimeError):
    """Any failure talking to the Contrast API."""


# ---------------------------------------------------------------------------
# Credentials
# ---------------------------------------------------------------------------

def _load_dotenv() -> None:
    """Populate os.environ from the nearest .env, without overriding real env vars."""
    here = Path(__file__).resolve().parent
    for candidate in (here / ".env", here.parent / ".env", Path.cwd() / ".env"):
        if not candidate.is_file():
            continue
        for line in candidate.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, _, value = line.partition("=")
            name = name.strip().removeprefix("export ").strip()
            os.environ.setdefault(name, value.strip().strip("'\""))


_load_dotenv()


def api_key() -> str:
    key = os.environ.get("CONTRAST_API_KEY")
    if not key:
        raise ContrastError(
            "CONTRAST_API_KEY is not set. Add it to contrast-api/.env (see .env.example) "
            "or export it before running."
        )
    return key


def mask(key: str | None) -> str:
    if not key or len(key) < 8:
        return "****"
    return f"{key[:4]}...{key[-4:]}"


# ---------------------------------------------------------------------------
# Resolved-scheme cache
# ---------------------------------------------------------------------------

def _read_cache() -> dict | None:
    try:
        cached = json.loads(CACHE_FILE.read_text())
    except (OSError, ValueError):
        return None
    if cached.get("base_url") != BASE_URL:
        return None  # base changed, re-resolve
    if not any(s[0] == cached.get("scheme") for s in AUTH_SCHEMES):
        return None
    return cached


def _write_cache(prefix: str, scheme: str) -> None:
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps({"base_url": BASE_URL, "prefix": prefix, "scheme": scheme}, indent=2))


def _scheme_by_id(scheme_id: str):
    for candidate in AUTH_SCHEMES:
        if candidate[0] == scheme_id:
            return candidate
    raise ContrastError(f"Unknown auth scheme '{scheme_id}'.")


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

def _build_url(prefix: str, path: str, query: dict | None) -> str:
    url = f"{BASE_URL}{prefix}{path}"
    params = {k: str(v) for k, v in (query or {}).items() if v not in (None, "")}
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    return url


def _raw_request(method: str, prefix: str, path: str, scheme, query=None, body=None) -> dict:
    """One HTTP call against an explicit scheme and prefix. Never raises on HTTP status."""
    scheme_id, header, template = scheme
    url = _build_url(prefix, path, query)
    payload = None if body is None else json.dumps(body).encode()

    request = urllib.request.Request(url, data=payload, method=method)
    request.add_header("Accept", "application/json")
    request.add_header(header, template.format(key=api_key()))
    if payload is not None:
        request.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            text = response.read().decode("utf-8", "replace")
            status = response.status
    except urllib.error.HTTPError as err:
        text = err.read().decode("utf-8", "replace")
        status = err.code
    except urllib.error.URLError as err:
        return {"url": url, "status": None, "ok": False, "body": None, "text": "", "error": str(err.reason)}

    try:
        parsed = json.loads(text) if text else None
    except ValueError:
        parsed = None

    return {"url": url, "status": status, "ok": 200 <= status < 300, "body": parsed, "text": text}


def _diagnose(attempts: list[dict]) -> str:
    """Explain a failed discovery run.

    Order matters. An identical status across every prefix and scheme means
    something upstream answered before Contrast did (a proxy, VPN, firewall or
    egress allowlist), which is not a credential problem and must not be
    reported as one.
    """
    answered = [a for a in attempts if a.get("status") is not None]

    if not answered:
        # Nothing returned an HTTP status, so the failure is below HTTP: DNS, TLS,
        # or a proxy refusing the CONNECT tunnel. The underlying error names the cause.
        reasons = sorted({a["error"] for a in attempts if a.get("error")})
        detail = f" Reported: {'; '.join(reasons)}." if reasons else ""
        return (
            f"No attempt reached {BASE_URL}: the connection failed below HTTP, so this is a "
            f"network, DNS, VPN or proxy problem rather than a credential one.{detail}"
        )

    statuses = {a["status"] for a in answered}
    if len(statuses) == 1 and len(answered) == len(attempts):
        only = next(iter(statuses))
        return (
            f"Every prefix and auth scheme returned the same status ({only}). That points at "
            "something answering ahead of Contrast, such as a proxy, VPN or firewall, rather than "
            f"a rejected credential. Confirm you can reach {BASE_URL} from this machine, then re-run."
        )

    if statuses & {401, 403}:
        return (
            "A path answered but rejected the credential. The key is likely wrong, revoked, or "
            "scoped to a different Contrast workspace. Check it in Contrast, then update "
            "contrast-api/.env."
        )

    return (
        "No candidate path answered with 2xx. The base URL or resource paths are likely different "
        "from the defaults. Override them with CONTRAST_API_BASE_URL and the CONTRAST_PATH_* env "
        "vars, or call a known path directly with the `get` subcommand."
    )


def discover() -> dict:
    """Probe every prefix and auth scheme, keep the first that answers with 2xx.

    A 401/403 means the key or header is wrong; a 404 means the prefix is wrong.
    Every attempt is reported so a failure is diagnosable rather than opaque.
    """
    api_key()  # fail fast rather than probing every path without a credential

    attempts: list[dict] = []
    for prefix in PATH_PREFIXES:
        for scheme in AUTH_SCHEMES:
            result = _raw_request("GET", prefix, RESOURCES["events"], scheme, query={"limit": 1})
            attempts.append(
                {
                    "prefix": prefix,
                    "scheme": scheme[0],
                    "status": result["status"],
                    "url": result["url"],
                    "body_snippet": (result.get("text") or None) and result["text"][:200],
                    "error": result.get("error"),
                }
            )
            if result["ok"]:
                _write_cache(prefix, scheme[0])
                return {
                    "resolved": True,
                    "base_url": BASE_URL,
                    "prefix": prefix,
                    "auth_scheme": scheme[0],
                    "auth_header": scheme[1],
                    "api_key": mask(os.environ.get("CONTRAST_API_KEY")),
                    "cache_file": str(CACHE_FILE),
                    "sample": result["body"],
                    "attempts": attempts,
                }

    return {
        "resolved": False,
        "base_url": BASE_URL,
        "api_key": mask(os.environ.get("CONTRAST_API_KEY")),
        "diagnosis": _diagnose(attempts),
        "attempts": attempts,
    }


def _resolved() -> tuple[str, str]:
    cached = _read_cache()
    if cached:
        return cached["prefix"], cached["scheme"]
    report = discover()
    if not report["resolved"]:
        raise ContrastError(
            f"Could not reach the Contrast API. {report['diagnosis']}\n"
            f"Attempts: {json.dumps(report['attempts'], indent=2)}"
        )
    return report["prefix"], report["auth_scheme"]


def request(method: str, path: str, query: dict | None = None, body: dict | None = None):
    """Authenticated request using the resolved scheme. Raises on non-2xx."""
    prefix, scheme_id = _resolved()
    result = _raw_request(method, prefix, path, _scheme_by_id(scheme_id), query=query, body=body)
    if not result["ok"]:
        detail = f" Body: {result['text'][:400]}" if result.get("text") else ""
        status = result["status"] if result["status"] is not None else result.get("error")
        raise ContrastError(f"Contrast API {status} for {method} {result['url']}.{detail}")
    return result["body"]


# ---------------------------------------------------------------------------
# Envelopes and pagination
# ---------------------------------------------------------------------------

_RECORD_KEYS = ("data", "results", "items", "records", "events", "registrations",
                "views", "polls", "messages")
_CURSOR_KEYS = ("next_cursor", "nextCursor", "next_page_token", "cursor", "next")


def records(payload) -> list:
    """Pull the list of records out of whatever envelope the API returns."""
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return []
    for key in _RECORD_KEYS:
        if isinstance(payload.get(key), list):
            return payload[key]
    return []


def next_cursor(payload) -> str | None:
    """Find the cursor or next-page token in whatever envelope the API returns."""
    if not isinstance(payload, dict):
        return None
    meta = payload.get("meta") or payload.get("pagination") or payload
    if not isinstance(meta, dict):
        return None
    if meta.get("has_more") is False:
        return None
    for key in _CURSOR_KEYS:
        value = meta.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def list_resource(resource: str, query: dict | None = None, max_pages: int = 10) -> list:
    """Fetch a collection, following cursors. A non-paginated endpoint costs one request."""
    path = RESOURCES.get(resource, resource)
    out: list = []
    cursor = None
    for _ in range(max_pages):
        page_query = dict(query or {})
        if cursor:
            page_query["cursor"] = cursor
        payload = request("GET", path, query=page_query)
        batch = records(payload)
        out.extend(batch)
        cursor = next_cursor(payload)
        if not cursor or not batch:
            break
    return out


# ---------------------------------------------------------------------------
# Normalisation
# ---------------------------------------------------------------------------

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
FULL_MONTHS = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]

_START_KEYS = ("starts_at", "startsAt", "start_time", "startTime", "start_date",
               "startDate", "scheduled_at", "date")
_END_KEYS = ("ends_at", "endsAt", "end_time", "endTime", "end_date", "endDate")


def pick(record, keys):
    """First present, non-empty value among the candidate keys."""
    if not isinstance(record, dict):
        return None
    for key in keys:
        value = record.get(key)
        if value not in (None, "", [], {}):
            return value
    return None


def parse_date(value):
    """Parse an ISO 8601 timestamp, tolerating a trailing Z. Returns aware UTC or None."""
    if not value or not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _zone(name):
    if not name or ZoneInfo is None:
        return timezone.utc
    try:
        return ZoneInfo(name)
    except Exception:
        return timezone.utc


def format_date_range(start_value, end_value, tz_name=None):
    """Date range in TrustFlight house style, read in the event's own timezone.

    same day      -> "12 May 2026"
    same month    -> "12–14 May 2026"       (en dash, no spaces)
    across months -> "29 May – 2 Jun 2026"  (en dash, spaces either side)
    """
    start = parse_date(start_value)
    if not start:
        return None
    end = parse_date(end_value) or start

    tz = _zone(tz_name)
    a, b = start.astimezone(tz), end.astimezone(tz)

    if (a.day, a.month, a.year) == (b.day, b.month, b.year):
        return f"{a.day} {FULL_MONTHS[a.month - 1]} {a.year}"
    if a.month == b.month and a.year == b.year:
        return f"{a.day}–{b.day} {FULL_MONTHS[a.month - 1]} {a.year}"
    if a.year == b.year:
        return f"{a.day} {MONTHS[a.month - 1]} – {b.day} {MONTHS[b.month - 1]} {a.year}"
    return f"{a.day} {MONTHS[a.month - 1]} {a.year} – {b.day} {MONTHS[b.month - 1]} {b.year}"


def format_time(value, tz_name=None):
    """Start time in the event's timezone, for example "14:00 BST"."""
    parsed = parse_date(value)
    if not parsed:
        return None
    local = parsed.astimezone(_zone(tz_name))
    label = local.strftime("%Z") or "UTC"
    return f"{local:%H:%M} {label}"


def _speaker(entry):
    if isinstance(entry, str):
        return {"name": entry, "title": None, "company": None, "avatar_url": None}
    return {
        "name": pick(entry, ("name", "full_name", "fullName", "display_name", "displayName")),
        "title": pick(entry, ("title", "job_title", "jobTitle", "role", "position", "headline")),
        "company": pick(entry, ("company", "company_name", "organisation", "organization")),
        "avatar_url": pick(entry, ("avatar_url", "avatarUrl", "photo_url", "picture", "image_url", "avatar")),
    }


def speakers(event) -> list:
    raw = pick(event, ("speakers", "hosts", "presenters", "panelists", "guests"))
    if raw is None:
        return []
    entries = raw if isinstance(raw, list) else [raw]
    return [s for s in (_speaker(e) for e in entries) if s["name"]]


def is_upcoming(event) -> bool:
    start = parse_date(pick(event, _START_KEYS))
    return bool(start and start >= datetime.now(timezone.utc))


def promo_brief(event: dict, include_raw: bool = True) -> dict:
    """Everything a LinkedIn promo post or event graphic needs from one webinar.

    The Contrast schema could not be read at build time, so each field is looked
    up across the plausible key spellings rather than one fixed name, and the
    untouched record is returned as `raw` so nothing is lost.
    """
    start = pick(event, _START_KEYS)
    end = pick(event, _END_KEYS)
    tz_name = pick(event, ("timezone", "time_zone", "timeZone", "tz"))

    parsed_start, parsed_end = parse_date(start), parse_date(end)
    duration = None
    if parsed_start and parsed_end:
        minutes = round((parsed_end - parsed_start).total_seconds() / 60)
        duration = minutes if minutes > 0 else None

    brief = {
        "id": pick(event, ("id", "uuid", "event_id", "eventId")),
        "slug": pick(event, ("slug", "handle", "public_id", "publicId")),
        "title": pick(event, ("title", "name", "event_name", "eventName", "subject")),
        "subtitle": pick(event, ("subtitle", "tagline", "headline")),
        "description": pick(event, ("description", "summary", "abstract", "excerpt", "body")),
        "status": pick(event, ("status", "state", "lifecycle")),
        "starts_at": start,
        "ends_at": end,
        "timezone": tz_name or "UTC",
        "date_formatted": format_date_range(start, end, tz_name),
        "time_formatted": format_time(start, tz_name),
        "duration_minutes": duration,
        "is_upcoming": is_upcoming(event) if parsed_start else None,
        "registration_url": pick(event, (
            "registration_url", "registrationUrl", "landing_page_url", "landingPageUrl",
            "public_url", "publicUrl", "url", "link", "watch_url",
        )),
        "replay_url": pick(event, ("replay_url", "replayUrl", "recording_url", "recordingUrl", "on_demand_url")),
        "cover_image_url": pick(event, (
            "cover_image_url", "coverImageUrl", "cover_image", "thumbnail_url",
            "thumbnailUrl", "image_url", "imageUrl", "banner_url",
        )),
        "speakers": speakers(event),
        "registration_count": pick(event, ("registration_count", "registrationsCount",
                                           "registrations_count", "registrant_count")),
        "view_count": pick(event, ("view_count", "viewsCount", "views_count",
                                   "attendee_count", "attendees_count")),
    }
    if include_raw:
        brief["raw"] = event
    return brief


def _sort_key(event):
    """Sort by start time, soonest first, records without a date last."""
    start = parse_date(pick(event, _START_KEYS))
    return (start is None, start or datetime.max.replace(tzinfo=timezone.utc))


# ---------------------------------------------------------------------------
# High-level helpers
# ---------------------------------------------------------------------------

def list_webinars(when: str = "upcoming", limit: int = 25, status: str | None = None,
                  include_raw: bool = False) -> list[dict]:
    """Webinars as promo briefs, soonest first. `when` is upcoming, past or all."""
    events = list_resource("events", query={"limit": max(limit, 50), "status": status})
    if when == "upcoming":
        events = [e for e in events if is_upcoming(e)]
    elif when == "past":
        events = [e for e in events if not is_upcoming(e)]
    events.sort(key=_sort_key)
    return [promo_brief(e, include_raw=include_raw) for e in events[:limit]]


def get_webinar(event_id: str) -> dict:
    """One webinar by id or slug, falling back to a collection scan if there is no detail route."""
    try:
        payload = request("GET", f"{RESOURCES['events']}/{urllib.parse.quote(str(event_id))}")
        found = payload[0] if isinstance(payload, list) and payload else payload
        if isinstance(found, dict):
            found = found.get("data", found) if "data" in found else found
        if isinstance(found, dict) and found:
            return found
    except ContrastError as err:
        if " 404 " not in str(err):
            raise

    for event in list_resource("events", query={"limit": 200}):
        brief = promo_brief(event, include_raw=False)
        if str(brief["id"]) == str(event_id) or str(brief["slug"]) == str(event_id):
            return event
    raise ContrastError(f"No Contrast webinar found with id or slug '{event_id}'.")


def list_for_event(resource: str, event_id: str | None = None, limit: int = 100) -> list:
    """Sub-collection lookup: try a nested route first, then a filtered collection."""
    if event_id:
        nested_path = f"{RESOURCES['events']}/{urllib.parse.quote(str(event_id))}{RESOURCES[resource]}"
        try:
            nested = records(request("GET", nested_path, query={"limit": limit}))
            if nested:
                return nested
        except ContrastError as err:
            if " 404 " not in str(err):
                raise
    query = {"limit": limit}
    if event_id:
        query["event_id"] = event_id
    return list_resource(resource, query=query)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _dump(value) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False, default=str))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="contrast_api.py",
        description="Query the Contrast webinar API. Run check-auth first.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("check-auth", help="Verify the credential and resolve the auth header and path prefix")

    p_list = sub.add_parser("list-webinars", help="List webinars as promo briefs, soonest first")
    p_list.add_argument("--when", choices=["upcoming", "past", "all"], default="upcoming")
    p_list.add_argument("--limit", type=int, default=25)
    p_list.add_argument("--status", default=None, help="Filter on the API's status field")
    p_list.add_argument("--raw", action="store_true", help="Include the untouched API record")

    p_get = sub.add_parser("webinar", help="Full record for one webinar")
    p_get.add_argument("id")

    p_brief = sub.add_parser("promo-brief", help="Promo-ready fields for one webinar")
    p_brief.add_argument("id")
    p_brief.add_argument("--raw", action="store_true", help="Include the untouched API record")

    for name, help_text in [
        ("registrations", "List registrations"),
        ("views", "List views and attendance records"),
        ("polls", "List polls and their results"),
        ("chat-messages", "List chat and Q&A messages"),
    ]:
        p_sub = sub.add_parser(name, help=help_text)
        p_sub.add_argument("--event-id", default=None, help="Restrict to one webinar")
        p_sub.add_argument("--limit", type=int, default=100)

    p_recurring = sub.add_parser("recurring-events", help="List recurring webinar series")
    p_recurring.add_argument("--limit", type=int, default=25)

    p_raw = sub.add_parser("get", help="Call any API path directly with the resolved credential")
    p_raw.add_argument("path", help="Resource path, for example /events/abc123")
    p_raw.add_argument("--query", default=None, help="Query parameters as a JSON object")

    args = parser.parse_args(argv)

    try:
        if args.command == "check-auth":
            report = discover()
            _dump(report)
            if not report["resolved"]:
                print(f"\nNot resolved. {report['diagnosis']}", file=sys.stderr)
                return 1
            print(
                f"\nResolved. Auth header: {report['auth_header']}, "
                f"path prefix: '{report['prefix']}'.\nCached at {report['cache_file']}",
                file=sys.stderr,
            )
            return 0

        if args.command == "list-webinars":
            _dump(list_webinars(when=args.when, limit=args.limit, status=args.status, include_raw=args.raw))
        elif args.command == "webinar":
            _dump(get_webinar(args.id))
        elif args.command == "promo-brief":
            _dump(promo_brief(get_webinar(args.id), include_raw=args.raw))
        elif args.command == "recurring-events":
            _dump(list_resource("recurring_events", query={"limit": args.limit}))
        elif args.command in ("registrations", "views", "polls", "chat-messages"):
            resource = args.command.replace("-", "_")
            _dump(list_for_event(resource, args.event_id, args.limit))
        elif args.command == "get":
            query = json.loads(args.query) if args.query else None
            _dump(request("GET", args.path, query=query))
        return 0

    except ContrastError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
