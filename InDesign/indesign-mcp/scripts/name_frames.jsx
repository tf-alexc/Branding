/**
 * name_frames.jsx
 * Run this once on any InDesign template to inspect and name all frames.
 * It writes a JSON report to /tmp/indesign_frames.json listing every
 * text frame and image frame on every page, with its current label,
 * position, and size — so you can decide what names to assign.
 *
 * HOW TO USE:
 *   1. Open your template in InDesign.
 *   2. File > Scripts > Script Panel, then run this file.
 *   3. Open /tmp/indesign_frames.json to see all frames.
 *   4. Edit the NAMES map below to assign meaningful names to frames
 *      you want the MCP to control, then re-run with APPLY_NAMES = true.
 */

// ─── CONFIG ──────────────────────────────────────────────────────────────────

var APPLY_NAMES = true;

var NAMES = {
  // Page 1
  "0_114": "p1_headline",
  "0_45":  "p1_tagline",
  "0_115": "p1_hero_description",
  "0_96":  "p1_company_intro",
  "0_116": "p1_products_intro",
  "0_91":  "p1_stat_customers",
  "0_92":  "p1_stat_countries",
  "0_110": "p1_category_1",
  "0_104": "p1_category_2",
  "0_101": "p1_category_3",
  "0_107": "p1_category_4",
  "0_69":  "p1_product_1_desc",
  "0_53":  "p1_product_2_desc",
  "0_57":  "p1_product_3_desc",
  "0_65":  "p1_product_4_desc",
  "0_49":  "p1_product_5_desc",
  "0_61":  "p1_product_6_desc",
  // Page 2
  "1_102": "p2_services_intro",
  "1_99":  "p2_crisis_header",
  "1_77":  "p2_crisis_desc",
  "1_100": "p2_closing",
  "1_105": "p2_cta",
  "1_72":  "p2_contact_web",
  "1_69":  "p2_contact_email",
  "1_66":  "p2_contact_uk",
  "1_63":  "p2_contact_us"
};

// ─── JSON POLYFILL (ExtendScript has no native JSON) ─────────────────────────

var JSON = (function () {
  function stringify(val, replacer, indent) {
    var t = typeof val;
    if (val === null) return "null";
    if (t === "boolean") return val ? "true" : "false";
    if (t === "number") return isFinite(val) ? String(val) : "null";
    if (t === "string") return '"' + val.replace(/\\/g, "\\\\").replace(/"/g, '\\"').replace(/\n/g, "\\n").replace(/\r/g, "\\r").replace(/\t/g, "\\t") + '"';
    if (t === "object") {
      if (val instanceof Array) {
        var items = [];
        for (var i = 0; i < val.length; i++) items.push(stringify(val[i]));
        return "[" + items.join(", ") + "]";
      }
      var pairs = [];
      for (var k in val) {
        if (val.hasOwnProperty(k)) pairs.push('"' + k + '": ' + stringify(val[k]));
      }
      return "{\n  " + pairs.join(",\n  ") + "\n}";
    }
    return "null";
  }
  return { stringify: stringify };
})();

// ─── SCRIPT ──────────────────────────────────────────────────────────────────

var doc = app.activeDocument;

if (!doc) {
  alert("No document is open.");
} else {
  var report = [];

  for (var p = 0; p < doc.pages.length; p++) {
    var page = doc.pages[p];

    for (var f = 0; f < page.allPageItems.length; f++) {
      var item = page.allPageItems[f];
      var type = "unknown";

      if (item instanceof TextFrame) {
        type = "text";
      } else if (item instanceof Rectangle || item instanceof Oval || item instanceof Polygon) {
        type = item.contentType == ContentType.GRAPHIC_TYPE ? "image" : "shape";
      }

      var bounds = item.geometricBounds; // [top, left, bottom, right]
      var key = p + "_" + f;

      var entry = {
        key: key,
        page: p + 1,
        index: f,
        type: type,
        label: item.label || "",
        name: item.name || "",
        top: Math.round(bounds[0] * 10) / 10,
        left: Math.round(bounds[1] * 10) / 10,
        width: Math.round((bounds[3] - bounds[1]) * 10) / 10,
        height: Math.round((bounds[2] - bounds[0]) * 10) / 10
      };

      if (type == "text") {
        var preview = item.contents.replace(/\r/g, " ").replace(/\n/g, " ");
        entry.text_preview = preview.length > 80 ? preview.substring(0, 80) + "..." : preview;
      }

      report.push(entry);

      // Apply name if APPLY_NAMES is true and key exists in NAMES map
      if (APPLY_NAMES && NAMES[key]) {
        item.label = NAMES[key];
        item.name = NAMES[key];
      }
    }
  }

  // Write JSON report
  var outFile = new File("/tmp/indesign_frames.json");
  outFile.open("w");
  outFile.write(JSON.stringify(report, null, 2));
  outFile.close();

  if (APPLY_NAMES) {
    doc.save();
    alert("Names applied and document saved. Report written to /tmp/indesign_frames.json");
  } else {
    alert("Frame report written to /tmp/indesign_frames.json\n\nOpen it, then fill in the NAMES map in this script and re-run with APPLY_NAMES = true.");
  }
}
