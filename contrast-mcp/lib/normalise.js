"use strict";

/**
 * Turns a raw Contrast event record into the fields the branding skills need.
 *
 * The Contrast schema could not be read at build time, so every field is looked
 * up across the plausible key names rather than one fixed name. Unknown shapes
 * degrade to null instead of throwing, and the untouched record is always
 * returned alongside the brief so nothing is lost.
 */

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const FULL_MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

/** First present, non-empty value among the candidate keys. */
function pick(obj, keys) {
  if (!obj || typeof obj !== "object") return null;
  for (const key of keys) {
    const value = obj[key];
    if (value !== undefined && value !== null && value !== "") return value;
  }
  return null;
}

function parseDate(value) {
  if (!value) return null;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}

/**
 * Calendar day, month and year as seen in the given timezone. A 23:30 UTC start
 * is already the next day in Sydney, so reading the date off the UTC instant
 * would print the wrong day for evening webinars.
 */
function partsInZone(date, timezone) {
  try {
    const parts = new Intl.DateTimeFormat("en-GB", {
      timeZone: timezone || "UTC",
      year: "numeric",
      month: "numeric",
      day: "numeric",
    }).formatToParts(date);
    const get = (type) => Number(parts.find((p) => p.type === type).value);
    return { day: get("day"), month: get("month") - 1, year: get("year") };
  } catch {
    return { day: date.getUTCDate(), month: date.getUTCMonth(), year: date.getUTCFullYear() };
  }
}

/**
 * Date range in TrustFlight house style, read in the event's own timezone:
 *   same day        -> "12 May 2026"
 *   same month      -> "12–14 May 2026"      (en dash, no spaces)
 *   across months   -> "29 May – 2 Jun 2026" (en dash, spaces either side)
 */
function formatDateRange(startValue, endValue, timezone) {
  const start = parseDate(startValue);
  if (!start) return null;
  const end = parseDate(endValue) || start;

  const from = partsInZone(start, timezone);
  const to = partsInZone(end, timezone);

  const sameDay = from.day === to.day && from.month === to.month && from.year === to.year;
  if (sameDay) return `${from.day} ${FULL_MONTHS[from.month]} ${from.year}`;

  if (from.month === to.month && from.year === to.year) {
    return `${from.day}–${to.day} ${FULL_MONTHS[from.month]} ${from.year}`;
  }
  if (from.year === to.year) {
    return `${from.day} ${MONTHS[from.month]} – ${to.day} ${MONTHS[to.month]} ${from.year}`;
  }
  return `${from.day} ${MONTHS[from.month]} ${from.year} – ${to.day} ${MONTHS[to.month]} ${to.year}`;
}

/** Start time as "14:00 BST", or "14:00 UTC" when no timezone is supplied. */
function formatTime(value, timezone) {
  const date = parseDate(value);
  if (!date) return null;
  const tz = timezone || "UTC";
  try {
    const time = new Intl.DateTimeFormat("en-GB", {
      hour: "2-digit",
      minute: "2-digit",
      timeZone: tz,
      timeZoneName: "short",
      hour12: false,
    }).format(date);
    return time;
  } catch {
    return `${String(date.getUTCHours()).padStart(2, "0")}:${String(date.getUTCMinutes()).padStart(2, "0")} UTC`;
  }
}

function durationMinutes(startValue, endValue) {
  const start = parseDate(startValue);
  const end = parseDate(endValue);
  if (!start || !end) return null;
  const minutes = Math.round((end.getTime() - start.getTime()) / 60000);
  return minutes > 0 ? minutes : null;
}

/** Normalise a speaker entry, which may be a string or an object. */
function normaliseSpeaker(entry) {
  if (typeof entry === "string") return { name: entry, title: null, company: null, avatar_url: null };
  return {
    name: pick(entry, ["name", "full_name", "fullName", "display_name", "displayName"]),
    title: pick(entry, ["title", "job_title", "jobTitle", "role", "position", "headline"]),
    company: pick(entry, ["company", "company_name", "organisation", "organization"]),
    avatar_url: pick(entry, ["avatar_url", "avatarUrl", "photo_url", "picture", "image_url", "avatar"]),
  };
}

function speakers(event) {
  const raw = pick(event, ["speakers", "hosts", "presenters", "panelists", "guests"]);
  if (!raw) return [];
  return (Array.isArray(raw) ? raw : [raw]).map(normaliseSpeaker).filter((s) => s.name);
}

function startValue(event) {
  return pick(event, ["starts_at", "startsAt", "start_time", "startTime", "start_date", "startDate", "scheduled_at", "date"]);
}

function endValue(event) {
  return pick(event, ["ends_at", "endsAt", "end_time", "endTime", "end_date", "endDate"]);
}

/**
 * Everything a LinkedIn promo post or event graphic needs from one webinar,
 * plus the raw record for anything this mapping does not cover.
 */
function promoBrief(event) {
  const start = startValue(event);
  const end = endValue(event);
  const timezone = pick(event, ["timezone", "time_zone", "timeZone", "tz"]);

  return {
    id: pick(event, ["id", "uuid", "event_id", "eventId"]),
    slug: pick(event, ["slug", "handle", "public_id", "publicId"]),
    title: pick(event, ["title", "name", "event_name", "eventName", "subject"]),
    subtitle: pick(event, ["subtitle", "tagline", "headline"]),
    description: pick(event, ["description", "summary", "abstract", "excerpt", "body"]),
    status: pick(event, ["status", "state", "lifecycle"]),
    starts_at: start,
    ends_at: end,
    timezone: timezone || "UTC",
    date_formatted: formatDateRange(start, end, timezone),
    time_formatted: formatTime(start, timezone),
    duration_minutes: durationMinutes(start, end),
    is_upcoming: parseDate(start) ? parseDate(start).getTime() >= Date.now() : null,
    registration_url: pick(event, [
      "registration_url", "registrationUrl", "landing_page_url", "landingPageUrl",
      "public_url", "publicUrl", "url", "link", "watch_url",
    ]),
    replay_url: pick(event, ["replay_url", "replayUrl", "recording_url", "recordingUrl", "on_demand_url"]),
    cover_image_url: pick(event, [
      "cover_image_url", "coverImageUrl", "cover_image", "thumbnail_url",
      "thumbnailUrl", "image_url", "imageUrl", "banner_url",
    ]),
    speakers: speakers(event),
    registration_count: pick(event, ["registration_count", "registrationsCount", "registrations_count", "registrant_count"]),
    view_count: pick(event, ["view_count", "viewsCount", "views_count", "attendee_count", "attendees_count"]),
    raw: event,
  };
}

/** Sort by start time, soonest first, records without a date last. */
function byStartAscending(a, b) {
  const left = parseDate(startValue(a));
  const right = parseDate(startValue(b));
  if (!left && !right) return 0;
  if (!left) return 1;
  if (!right) return -1;
  return left.getTime() - right.getTime();
}

function isUpcoming(event) {
  const start = parseDate(startValue(event));
  return start ? start.getTime() >= Date.now() : false;
}

module.exports = {
  promoBrief,
  formatDateRange,
  formatTime,
  byStartAscending,
  isUpcoming,
  startValue,
  pick,
};
