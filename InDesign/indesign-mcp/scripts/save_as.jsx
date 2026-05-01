$.evalFile(File($.fileName).parent + '/_helpers.jsx');
var args = readArgs();
var doc = app.activeDocument;
doc.saveAs(new File(args.path));
writeResult({ success: true, path: args.path });
