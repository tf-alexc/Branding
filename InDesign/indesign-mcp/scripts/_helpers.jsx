// Shared helpers — included at the top of every script via $.evalFile()

function readArgs() {
  var f = new File('/tmp/indesign_args.json');
  f.open('r'); var s = f.read(); f.close();
  return eval('(' + s + ')');
}

function writeResult(obj) {
  function str(v) {
    if (v === null || v === undefined) return 'null';
    var t = typeof v;
    if (t === 'boolean') return v ? 'true' : 'false';
    if (t === 'number') return String(v);
    if (t === 'string') return '"' + v.replace(/\\/g,'\\\\').replace(/"/g,'\\"').replace(/\n/g,'\\n').replace(/\r/g,'\\r').replace(/\t/g,'\\t') + '"';
    if (v instanceof Array) {
      var a = [];
      for (var i = 0; i < v.length; i++) a.push(str(v[i]));
      return '[' + a.join(',') + ']';
    }
    var p = [];
    for (var k in v) if (v.hasOwnProperty(k)) p.push('"' + k + '":' + str(v[k]));
    return '{' + p.join(',') + '}';
  }
  var f = new File('/tmp/indesign_result.json');
  f.open('w'); f.write(str(obj)); f.close();
}
