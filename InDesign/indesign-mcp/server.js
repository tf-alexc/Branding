#!/usr/bin/env node
"use strict";

const { Server } = require("@modelcontextprotocol/sdk/server/index.js");
const { StdioServerTransport } = require("@modelcontextprotocol/sdk/server/stdio.js");
const { CallToolRequestSchema, ListToolsRequestSchema } = require("@modelcontextprotocol/sdk/types.js");
const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const SCRIPTS_DIR = path.join(__dirname, "scripts");
const ARGS_FILE   = "/tmp/indesign_args.json";
const RESULT_FILE = "/tmp/indesign_result.json";
const INDESIGN_APP = "Adobe InDesign 2026";

function runScript(scriptName, args = {}) {
  const scriptPath = path.join(SCRIPTS_DIR, scriptName);

  fs.writeFileSync(ARGS_FILE, JSON.stringify(args));
  if (fs.existsSync(RESULT_FILE)) fs.unlinkSync(RESULT_FILE);

  const appleScript = `tell application "${INDESIGN_APP}" to do script POSIX file "${scriptPath}" language javascript`;
  const tmpAs = `/tmp/indesign_run_${Date.now()}.applescript`;
  fs.writeFileSync(tmpAs, appleScript);

  try {
    execSync(`osascript "${tmpAs}"`, { timeout: 60000 });
  } finally {
    fs.unlinkSync(tmpAs);
  }

  if (fs.existsSync(RESULT_FILE)) {
    return JSON.parse(fs.readFileSync(RESULT_FILE, "utf8"));
  }
  return { success: true };
}

const TOOLS = [
  {
    name: "indesign_open_template",
    description: "Open an InDesign template (.indt) or document (.indd). InDesign launches automatically if not running.",
    inputSchema: {
      type: "object",
      properties: {
        path: { type: "string", description: "Absolute path to the .indt or .indd file" },
      },
      required: ["path"],
    },
  },
  {
    name: "indesign_list_frames",
    description: "List all named frames in the active document.",
    inputSchema: { type: "object", properties: {} },
  },
  {
    name: "indesign_set_text",
    description: "Set the text content of a named frame.",
    inputSchema: {
      type: "object",
      properties: {
        frame: { type: "string", description: "Frame name/label" },
        text:  { type: "string", description: "Text content to set" },
        preserve_style: { type: "boolean", description: "Preserve existing paragraph style (default: true)" },
      },
      required: ["frame", "text"],
    },
  },
  {
    name: "indesign_place_image",
    description: "Place an image into a named frame.",
    inputSchema: {
      type: "object",
      properties: {
        frame: { type: "string", description: "Frame name/label" },
        path:  { type: "string", description: "Absolute path to the image file" },
        fit: {
          type: "string",
          enum: ["fill_proportionally", "fit_content_proportionally", "fit_frame_to_content", "center_content"],
          description: "Fit mode (default: fill_proportionally)",
        },
      },
      required: ["frame", "path"],
    },
  },
  {
    name: "indesign_toggle_layer",
    description: "Show or hide a layer in the active document.",
    inputSchema: {
      type: "object",
      properties: {
        layer:   { type: "string",  description: "Layer name" },
        visible: { type: "boolean", description: "true = show, false = hide" },
      },
      required: ["layer", "visible"],
    },
  },
  {
    name: "indesign_export_pdf",
    description: "Export the active document as a PDF.",
    inputSchema: {
      type: "object",
      properties: {
        path:        { type: "string", description: "Absolute path for the output PDF" },
        preset:      { type: "string", enum: ["print", "digital"], description: "Quality preset" },
        preset_name: { type: "string", description: "Exact InDesign PDF preset name (overrides preset)" },
      },
      required: ["path"],
    },
  },
  {
    name: "indesign_save_as",
    description: "Save the active document to a new path as .indd.",
    inputSchema: {
      type: "object",
      properties: {
        path: { type: "string", description: "Absolute path for the .indd file" },
      },
      required: ["path"],
    },
  },
  {
    name: "indesign_close_document",
    description: "Close the active document. Call this after exporting the PDF to clean up.",
    inputSchema: {
      type: "object",
      properties: {
        save: { type: "boolean", description: "Save before closing (default: false)" },
      },
    },
  },
];

const server = new Server(
  { name: "indesign-mcp", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools: TOOLS }));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  try {
    let result;
    switch (name) {
      case "indesign_open_template":    result = runScript("open_template.jsx",  args); break;
      case "indesign_list_frames":      result = runScript("list_frames.jsx",    args); break;
      case "indesign_set_text":         result = runScript("set_text.jsx",       args); break;
      case "indesign_place_image":      result = runScript("place_image.jsx",    args); break;
      case "indesign_toggle_layer":     result = runScript("toggle_layer.jsx",   args); break;
      case "indesign_export_pdf":       result = runScript("export_pdf.jsx",     args); break;
      case "indesign_save_as":          result = runScript("save_as.jsx",        args); break;
      case "indesign_close_document":   result = runScript("close_document.jsx", args); break;
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
