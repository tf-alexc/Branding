$.evalFile(File($.fileName).parent + '/_helpers.jsx');
var args = readArgs();
var doc = app.activeDocument;
var found = false;

for (var i = 0; i < doc.layers.length; i++) {
  if (doc.layers[i].name === args.layer) {
    doc.layers[i].visible = (args.visible !== false);
    found = true;
    break;
  }
}

writeResult({ success: found, layer: args.layer, visible: args.visible });
