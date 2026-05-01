$.evalFile(File($.fileName).parent + '/_helpers.jsx');
var args = readArgs();
var doc = app.activeDocument;
var found = false;

var fitMap = {
  'fill_proportionally':      FitOptions.FILL_PROPORTIONALLY,
  'fit_content_proportionally': FitOptions.FIT_CONTENT_PROPORTIONALLY,
  'fit_frame_to_content':     FitOptions.FIT_FRAME_TO_CONTENT,
  'center_content':           FitOptions.CENTER_CONTENT
};
var fitOption = fitMap[args.fit] || FitOptions.FILL_PROPORTIONALLY;

for (var p = 0; p < doc.pages.length && !found; p++) {
  var items = doc.pages[p].allPageItems;
  for (var f = 0; f < items.length && !found; f++) {
    var item = items[f];
    if (item.label === args.frame || item.name === args.frame) {
      item.place(new File(args.path));
      item.fit(fitOption);
      found = true;
    }
  }
}

writeResult({ success: found, frame: args.frame });
