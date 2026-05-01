$.evalFile(File($.fileName).parent + '/_helpers.jsx');
var args = readArgs();
var doc = app.open(new File(args.path));
writeResult({ success: true, name: doc.name, pages: doc.pages.length });
