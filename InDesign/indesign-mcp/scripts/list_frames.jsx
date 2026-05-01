$.evalFile(File($.fileName).parent + '/_helpers.jsx');
var doc = app.activeDocument;
var frames = [];

for (var p = 0; p < doc.pages.length; p++) {
  var items = doc.pages[p].allPageItems;
  for (var f = 0; f < items.length; f++) {
    var item = items[f];
    var label = item.label || item.name;
    if (!label) continue;
    var type = (item instanceof TextFrame) ? 'text' : 'image';
    var b = item.geometricBounds;
    frames.push({ name: label, type: type, page: p + 1,
      width: Math.round((b[3]-b[1])*10)/10, height: Math.round((b[2]-b[0])*10)/10 });
  }
}

writeResult({ frames: frames });
