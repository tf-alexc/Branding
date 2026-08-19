#!/usr/bin/env node
"use strict";

/**
 * MCP server for the Contrast webinar platform (https://www.getcontrast.io).
 *
 * Built for webinar planning and promotion: list what is scheduled, pull one
 * webinar's details, and hand a promo-ready brief to the LinkedIn and event
 * graphic skills.
 */

const { Server } = require("@modelcontextprotocol/sdk/server/index.js");
const { StdioServerTransport } = require("@modelcontextprotocol/sdk/server/stdio.js");
const { CallToolRequestSchema, ListToolsRequestSchema } = require("@modelcontextprotocol/sdk/types.js");

const client = require("./lib/client.js");
const { promoBrief, byStartAscending, isUpcoming } = require("./lib/normalise.js");

const TOOLS = [
  {
    name: "contrast_check_auth",
    description:
      "Verify the Contrast API credential and resolve the working auth header and path prefix. " +
      "Run this first after installing or after rotating the API key. Reports every combination " +
      "it tried so a failure is diagnosable.",
    inputSchema: {
      type: "object",
      properties: {
        force: {
          type: "boolean",
          description: "Re-probe even if a working combination is already cached (default: true)",
        },
      },
    },
  },
  {
    name: "contrast_list_webinars",
    description:
      "List webinars from Contrast, soonest first. Use this to see what is scheduled before " +
      "planning promo posts. Returns normalised fields (title, formatted date and time, " +
      "speakers, registration URL) plus the raw record.",
    inputSchema: {
      type: "object",
      properties: {
        when: {
          type: "string",
          enum: ["upcoming", "past", "all"],
          description: "Filter by start time (default: upcoming)",
        },
        limit: { type: "number", description: "Maximum webinars to return (default: 25)" },
        status: { type: "string", description: "Filter on the API's status field, for example 'published'" },
        include_raw: {
          type: "boolean",
          description: "Include the untouched API record for each webinar (default: false)",
        },
      },
    },
  },
  {
    name: "contrast_get_webinar",
    description: "Fetch one webinar by id or slug, with all fields the API returns.",
    inputSchema: {
      type: "object",
      properties: {
        id: { type: "string", description: "Contrast event id or slug" },
      },
      required: ["id"],
    },
  },
  {
    name: "contrast_promo_brief",
    description:
      "Build a promo-ready brief for one webinar: title, house-style date and time, speakers with " +
      "titles, registration URL, description and cover image. This is the intended handoff into the " +
      "asip-webinar-generator, linkedin-event-generator and carousel-builder skills.",
    inputSchema: {
      type: "object",
      properties: {
        id: { type: "string", description: "Contrast event id or slug" },
      },
      required: ["id"],
    },
  },
  {
    name: "contrast_list_recurring_events",
    description: "List recurring webinar series, for planning a repeating slot rather than a one-off.",
    inputSchema: {
      type: "object",
      properties: {
        limit: { type: "number", description: "Maximum series to return (default: 25)" },
      },
    },
  },
  {
    name: "contrast_list_registrations",
    description: "List registrations, optionally for one webinar. Returns the count alongside the records.",
    inputSchema: {
      type: "object",
      properties: {
        event_id: { type: "string", description: "Restrict to one webinar" },
        limit: { type: "number", description: "Maximum registrations to return (default: 100)" },
      },
    },
  },
  {
    name: "contrast_list_views",
    description: "List views (attendance) records, optionally for one webinar.",
    inputSchema: {
      type: "object",
      properties: {
        event_id: { type: "string", description: "Restrict to one webinar" },
        limit: { type: "number", description: "Maximum view records to return (default: 100)" },
      },
    },
  },
  {
    name: "contrast_list_polls",
    description: "List polls and their results, optionally for one webinar. Useful raw material for follow-up posts.",
    inputSchema: {
      type: "object",
      properties: {
        event_id: { type: "string", description: "Restrict to one webinar" },
        limit: { type: "number", description: "Maximum polls to return (default: 50)" },
      },
    },
  },
  {
    name: "contrast_list_chat_messages",
    description: "List chat messages and Q&A, optionally for one webinar.",
    inputSchema: {
      type: "object",
      properties: {
        event_id: { type: "string", description: "Restrict to one webinar" },
        limit: { type: "number", description: "Maximum messages to return (default: 100)" },
      },
    },
  },
  {
    name: "contrast_request",
    description:
      "Escape hatch: call any Contrast API path directly with the resolved credential. Use this for " +
      "endpoints the named tools do not cover, or if Contrast changes a path. The path is appended to " +
      "the resolved base URL and prefix.",
    inputSchema: {
      type: "object",
      properties: {
        path: { type: "string", description: "Resource path, for example '/events/abc123'" },
        method: { type: "string", enum: ["GET", "POST", "PATCH", "PUT", "DELETE"], description: "Default: GET" },
        query: { type: "object", description: "Query string parameters" },
        body: { type: "object", description: "JSON request body for write methods" },
      },
      required: ["path"],
    },
  },
];

// ---------------------------------------------------------------------------
// Handlers
// ---------------------------------------------------------------------------

/** Fetch one event, falling back to a collection scan if there is no detail route. */
async function getEvent(id) {
  try {
    const payload = await client.request("GET", `${client.RESOURCES.events}/${encodeURIComponent(id)}`);
    const found = Array.isArray(payload) ? payload[0] : payload && payload.data ? payload.data : payload;
    if (found && typeof found === "object") return found;
  } catch (err) {
    if (!/ 404 /.test(err.message)) throw err;
  }

  const all = await client.list("events", { query: { limit: 200 } });
  const match = all.find((e) => {
    const brief = promoBrief(e);
    return String(brief.id) === id || String(brief.slug) === id;
  });
  if (!match) throw new Error(`No Contrast webinar found with id or slug '${id}'.`);
  return match;
}

async function listWebinars({ when = "upcoming", limit = 25, status, include_raw = false }) {
  const events = await client.list("events", { query: { limit: Math.max(limit, 50), status } });

  let filtered = events;
  if (when === "upcoming") filtered = events.filter(isUpcoming);
  else if (when === "past") filtered = events.filter((e) => !isUpcoming(e));

  const webinars = filtered
    .sort(byStartAscending)
    .slice(0, limit)
    .map((event) => {
      const brief = promoBrief(event);
      if (!include_raw) delete brief.raw;
      return brief;
    });

  return { when, count: webinars.length, total_fetched: events.length, webinars };
}

/** Sub-collection lookup: try a nested route first, then a filtered collection. */
async function listForEvent(resourceKey, eventId, limit) {
  if (eventId) {
    try {
      const payload = await client.request(
        "GET",
        `${client.RESOURCES.events}/${encodeURIComponent(eventId)}${client.RESOURCES[resourceKey]}`,
        { query: { limit } }
      );
      const nested = client.records(payload);
      if (nested.length) return nested;
    } catch (err) {
      if (!/ 404 /.test(err.message)) throw err;
    }
  }
  const query = { limit };
  if (eventId) query.event_id = eventId;
  return client.list(resourceKey, { query });
}

const server = new Server(
  { name: "contrast-mcp", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools: TOOLS }));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args = {} } = request.params;
  try {
    let result;
    switch (name) {
      case "contrast_check_auth":
        result = await client.discover();
        break;

      case "contrast_list_webinars":
        result = await listWebinars(args);
        break;

      case "contrast_get_webinar":
        result = await getEvent(args.id);
        break;

      case "contrast_promo_brief":
        result = promoBrief(await getEvent(args.id));
        break;

      case "contrast_list_recurring_events":
        result = await client.list("recurring_events", { query: { limit: args.limit || 25 } });
        break;

      case "contrast_list_registrations": {
        const records = await listForEvent("registrations", args.event_id, args.limit || 100);
        result = { count: records.length, registrations: records };
        break;
      }

      case "contrast_list_views": {
        const records = await listForEvent("views", args.event_id, args.limit || 100);
        result = { count: records.length, views: records };
        break;
      }

      case "contrast_list_polls": {
        const records = await listForEvent("polls", args.event_id, args.limit || 50);
        result = { count: records.length, polls: records };
        break;
      }

      case "contrast_list_chat_messages": {
        const records = await listForEvent("chat_messages", args.event_id, args.limit || 100);
        result = { count: records.length, messages: records };
        break;
      }

      case "contrast_request":
        result = await client.request(args.method || "GET", args.path, {
          query: args.query,
          body: args.body,
        });
        break;

      default:
        return { content: [{ type: "text", text: `Unknown tool: ${name}` }], isError: true };
    }
    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    return { content: [{ type: "text", text: `Error: ${err.message}` }], isError: true };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch(console.error);
