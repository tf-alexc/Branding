$.evalFile(File($.fileName).parent + '/_helpers.jsx');
var args = readArgs(); // { "save": false }
var doc = app.activeDocument;
var name = doc.name;
doc.close(args.save === true ? SaveOptions.YES : SaveOptions.NO);
writeResult({ success: true, closed: name });
