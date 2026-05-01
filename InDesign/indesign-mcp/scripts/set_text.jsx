$.evalFile(File($.fileName).parent + '/_helpers.jsx');
var args = readArgs();
var doc = app.activeDocument;
var found = false;

for (var p = 0; p < doc.pages.length && !found; p++) {
  var items = doc.pages[p].allPageItems;
  for (var f = 0; f < items.length && !found; f++) {
    var item = items[f];
    if ((item.label === args.frame || item.name === args.frame) && item instanceof TextFrame) {
      var style = (args.preserve_style !== false && item.paragraphs.length > 0)
        ? item.paragraphs[0].appliedParagraphStyle : null;
      item.contents = args.text;
      if (style) item.paragraphs[0].appliedParagraphStyle = style;
      found = true;
    }
  }
}

writeResult({ success: found, frame: args.frame });
