#!/usr/bin/env node
"use strict";

/**
 * Standalone connectivity check. Run `npm run check-auth` from contrast-mcp/ to
 * confirm the credential works without going through Claude Code.
 */

const client = require("../lib/client.js");

client
  .discover()
  .then((report) => {
    console.log(JSON.stringify(report, null, 2));
    if (report.resolved) {
      console.log(`\nResolved. Auth header: ${report.auth_header}, path prefix: '${report.prefix}'.`);
      console.log(`Cached at ${report.cache_file}`);
    } else {
      console.error(`\nNot resolved. ${report.diagnosis}`);
      process.exitCode = 1;
    }
  })
  .catch((err) => {
    console.error(`Error: ${err.message}`);
    process.exitCode = 1;
  });
