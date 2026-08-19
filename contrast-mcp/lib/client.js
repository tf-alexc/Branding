"use strict";

/**
 * HTTP client for the Contrast webinar API (https://www.getcontrast.io).
 *
 * The published reference at docs.getcontrast.io sits behind a login wall, so
 * the exact auth header and path prefix could not be read at build time. Rather
 * than hard-code a guess, this client resolves both at runtime: `discover()`
 * probes the plausible combinations, keeps the first that answers, and caches it
 * outside the repo. Every later call reuses the cached combination.
 *
 * If Contrast changes its scheme, delete the cache file (see CACHE_FILE) or call
 * the contrast_check_auth tool again to re-resolve.
 */

const fs = require("fs");
const os = require("os");
const path = require("path");

const BASE_URL = (process.env.CONTRAST_API_BASE_URL || "https://connect.getcontrast.io").replace(/\/+$/, "");
const CACHE_DIR = path.join(os.homedir(), ".contrast-mcp");
const CACHE_FILE = path.join(CACHE_DIR, "resolved.json");
const TIMEOUT_MS = Number(process.env.CONTRAST_TIMEOUT_MS || 30000);

/** Candidate authentication schemes, most likely first. */
const AUTH_SCHEMES = [
  { id: "bearer", header: "Authorization", format: (k) => `Bearer ${k}` },
  { id: "x-api-key", header: "X-API-Key", format: (k) => k },
  { id: "api-key", header: "Api-Key", format: (k) => k },
  { id: "raw-authorization", header: "Authorization", format: (k) => k },
];

/** Candidate path prefixes between the base URL and the resource path. */
const PATH_PREFIXES = ["/v1", "", "/api/v1", "/api"];

/** Resource paths, overridable individually via env (see README). */
const RESOURCES = {
  events: process.env.CONTRAST_PATH_EVENTS || "/events",
  recurring_events: process.env.CONTRAST_PATH_RECURRING_EVENTS || "/recurring-events",
  registrations: process.env.CONTRAST_PATH_REGISTRATIONS || "/registrations",
  views: process.env.CONTRAST_PATH_VIEWS || "/views",
  polls: process.env.CONTRAST_PATH_POLLS || "/polls",
  chat_messages: process.env.CONTRAST_PATH_CHAT_MESSAGES || "/chat-messages",
};

// ---------------------------------------------------------------------------
// Credentials
// ---------------------------------------------------------------------------

/**
 * Populate process.env from the nearest .env file. Called once at load so the
 * server works when launched by Claude Code without an inherited shell env.
 */
function loadDotEnv() {
  const candidates = [
    path.join(__dirname, "..", ".env"),
    path.join(__dirname, "..", "..", ".env"),
    path.join(process.cwd(), ".env"),
  ];
  for (const file of candidates) {
    if (!fs.existsSync(file)) continue;
    for (const line of fs.readFileSync(file, "utf8").split("\n")) {
      const match = line.match(/^\s*(?:export\s+)?([A-Z0-9_]+)\s*=\s*(.*)\s*$/);
      if (!match) continue;
      const value = match[2].replace(/^['"]|['"]$/g, "");
      if (process.env[match[1]] === undefined) process.env[match[1]] = value;
    }
  }
}
loadDotEnv();

function apiKey() {
  const key = process.env.CONTRAST_API_KEY;
  if (!key) {
    throw new Error(
      "CONTRAST_API_KEY is not set. Add it to contrast-mcp/.env (see .env.example) " +
        "or export it before launching the MCP server."
    );
  }
  return key;
}

/** Mask a key for safe inclusion in tool output and error messages. */
function maskKey(key) {
  if (!key || key.length < 8) return "****";
  return `${key.slice(0, 4)}...${key.slice(-4)}`;
}

// ---------------------------------------------------------------------------
// Resolved-scheme cache
// ---------------------------------------------------------------------------

function readCache() {
  try {
    const cached = JSON.parse(fs.readFileSync(CACHE_FILE, "utf8"));
    if (cached.base_url !== BASE_URL) return null; // base changed, re-resolve
    if (!AUTH_SCHEMES.some((s) => s.id === cached.scheme)) return null;
    return cached;
  } catch {
    return null;
  }
}

function writeCache(entry) {
  fs.mkdirSync(CACHE_DIR, { recursive: true });
  fs.writeFileSync(CACHE_FILE, JSON.stringify({ ...entry, base_url: BASE_URL }, null, 2));
}

function schemeById(id) {
  return AUTH_SCHEMES.find((s) => s.id === id);
}

// ---------------------------------------------------------------------------
// Requests
// ---------------------------------------------------------------------------

function buildUrl(prefix, resourcePath, query) {
  const url = new URL(`${BASE_URL}${prefix}${resourcePath}`);
  for (const [key, value] of Object.entries(query || {})) {
    if (value === undefined || value === null || value === "") continue;
    url.searchParams.set(key, String(value));
  }
  return url.toString();
}

/** Single raw HTTP call against an explicit scheme and prefix. */
async function rawRequest({ method = "GET", prefix, resourcePath, query, body, scheme }) {
  const url = buildUrl(prefix, resourcePath, query);
  const headers = {
    Accept: "application/json",
    [scheme.header]: scheme.format(apiKey()),
  };
  if (body !== undefined) headers["Content-Type"] = "application/json";

  const response = await fetch(url, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
    signal: AbortSignal.timeout(TIMEOUT_MS),
  });

  const text = await response.text();
  let parsed = null;
  try {
    parsed = text ? JSON.parse(text) : null;
  } catch {
    parsed = null;
  }

  return { url, status: response.status, ok: response.ok, body: parsed, text };
}

/**
 * Explain a failed discovery run. The order matters: an identical status across
 * every prefix and scheme means something upstream answered before Contrast did
 * (a corporate proxy, a WAF, an egress block), which is not a credential
 * problem and must not be reported as one.
 */
function diagnose(attempts) {
  const answered = attempts.filter((a) => typeof a.status === "number");

  if (answered.length === 0) {
    return "No attempt reached the network. Check connectivity to " + BASE_URL + ".";
  }

  const statuses = new Set(answered.map((a) => a.status));
  if (statuses.size === 1 && answered.length === attempts.length) {
    const only = [...statuses][0];
    return (
      `Every prefix and auth scheme returned the same status (${only}). That points at something ` +
      "answering ahead of Contrast, such as a proxy, VPN or firewall, rather than a rejected " +
      "credential. Confirm you can reach " + BASE_URL + " from this machine, then re-run."
    );
  }

  if (statuses.has(401) || statuses.has(403)) {
    return (
      "A path answered but rejected the credential. The key is likely wrong, revoked, or scoped " +
      "to a different Contrast workspace. Check it in Contrast under Settings, then update " +
      "contrast-mcp/.env."
    );
  }

  return (
    "No candidate path answered with 2xx. The base URL or resource paths are likely different from " +
    "the defaults. Override them with the CONTRAST_API_BASE_URL and CONTRAST_PATH_* env vars, or " +
    "call a known path directly with contrast_request."
  );
}

/**
 * Probe every prefix and auth scheme against the events collection and keep the
 * first combination that answers with 2xx. A 401/403 means the key or header is
 * wrong; a 404 means the prefix is wrong. Both are reported so a failure is
 * diagnosable rather than opaque.
 */
async function discover() {
  apiKey(); // fail fast with a clear message rather than probing 16 paths without a credential

  const attempts = [];
  for (const prefix of PATH_PREFIXES) {
    for (const scheme of AUTH_SCHEMES) {
      let result;
      try {
        result = await rawRequest({
          prefix,
          resourcePath: RESOURCES.events,
          query: { limit: 1 },
          scheme,
        });
      } catch (err) {
        attempts.push({ prefix, scheme: scheme.id, error: err.message });
        continue;
      }
      attempts.push({
        prefix,
        scheme: scheme.id,
        status: result.status,
        url: result.url,
        body_snippet: result.text ? result.text.slice(0, 200) : null,
      });
      if (result.ok) {
        writeCache({ prefix, scheme: scheme.id });
        return {
          resolved: true,
          base_url: BASE_URL,
          prefix,
          auth_scheme: scheme.id,
          auth_header: scheme.header,
          api_key: maskKey(process.env.CONTRAST_API_KEY),
          cache_file: CACHE_FILE,
          sample: result.body,
          attempts,
        };
      }
    }
  }

  return {
    resolved: false,
    base_url: BASE_URL,
    api_key: maskKey(process.env.CONTRAST_API_KEY),
    diagnosis: diagnose(attempts),
    attempts,
  };
}

/** Return the cached scheme/prefix, resolving on first use. */
async function resolved() {
  const cached = readCache();
  if (cached) return cached;
  const report = await discover();
  if (!report.resolved) {
    throw new Error(
      `Could not reach the Contrast API. ${report.diagnosis}\n` +
        `Attempts: ${JSON.stringify(report.attempts, null, 2)}`
    );
  }
  return { prefix: report.prefix, scheme: report.auth_scheme };
}

/** Authenticated request using the resolved scheme. Throws on non-2xx. */
async function request(method, resourcePath, { query, body } = {}) {
  const { prefix, scheme } = await resolved();
  const result = await rawRequest({
    method,
    prefix,
    resourcePath,
    query,
    body,
    scheme: schemeById(scheme),
  });

  if (!result.ok) {
    const detail = result.text ? ` Body: ${result.text.slice(0, 400)}` : "";
    throw new Error(`Contrast API ${result.status} for ${method} ${result.url}.${detail}`);
  }
  return result.body;
}

/** Pull the array of records out of whatever envelope the API returns. */
function records(payload) {
  if (Array.isArray(payload)) return payload;
  if (!payload || typeof payload !== "object") return [];
  for (const key of ["data", "results", "items", "records", "events", "registrations", "views", "polls", "messages"]) {
    if (Array.isArray(payload[key])) return payload[key];
  }
  return [];
}

/** Find the cursor or next-page token in whatever envelope the API returns. */
function nextCursor(payload) {
  if (!payload || typeof payload !== "object") return null;
  const meta = payload.meta || payload.pagination || payload;
  if (meta.has_more === false) return null;
  for (const key of ["next_cursor", "nextCursor", "next_page_token", "cursor", "next"]) {
    const value = meta[key];
    if (typeof value === "string" && value) return value;
  }
  return null;
}

/**
 * Fetch a collection, following cursors up to maxPages. Stops as soon as a page
 * carries no cursor, so a non-paginated endpoint costs exactly one request.
 */
async function list(resourceKey, { query = {}, maxPages = 10 } = {}) {
  const resourcePath = RESOURCES[resourceKey] || resourceKey;
  const out = [];
  let cursor;
  for (let page = 0; page < maxPages; page++) {
    const payload = await request("GET", resourcePath, {
      query: cursor ? { ...query, cursor } : query,
    });
    const batch = records(payload);
    out.push(...batch);
    cursor = nextCursor(payload);
    if (!cursor || batch.length === 0) break;
  }
  return out;
}

module.exports = {
  BASE_URL,
  CACHE_FILE,
  RESOURCES,
  AUTH_SCHEMES,
  PATH_PREFIXES,
  discover,
  request,
  list,
  records,
  maskKey,
};
