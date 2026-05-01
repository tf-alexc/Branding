$.evalFile(File($.fileName).parent + '/_helpers.jsx');
var args = readArgs();
var doc = app.activeDocument;

var presetName = args.preset_name
  || (args.preset === 'digital' ? '[Smallest File Size]' : '[Press Quality]');

var preset = null;
for (var i = 0; i < app.pdfExportPresets.length; i++) {
  if (app.pdfExportPresets[i].name === presetName) {
    preset = app.pdfExportPresets[i];
    break;
  }
}

var outFile = new File(args.path);
if (preset) {
  doc.exportFile(ExportFormat.PDF_TYPE, outFile, false, preset);
} else {
  doc.exportFile(ExportFormat.PDF_TYPE, outFile, false);
}

writeResult({ success: true, path: args.path, preset: presetName });
