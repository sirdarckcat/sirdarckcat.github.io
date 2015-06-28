onfetch = function(e) {
  var url = new URL(e.request.url);
  console.log('got a request for', url.href);
  // Range Lab
  var steps, stepsMatch;
  if (stepsMatch = url.search.match(/[?&]steps=([^&]+)/)) {
    steps = stepsMatch[1];
    console.log('request has steps=', steps);
    var ranges = {};
    steps.split(/;/).forEach(function(step) {
      var parts = step.split(':');
      ranges[parts[0]]=parts;
    });
    var step, range = e.request.headers.get('range');
    if ((step = ranges[range]) || (step = ranges['default'])) {
      switch(step[1]) {
        case 'response':
          var binData = new Uint8Array(atob(step[2]).split('').map(function(strArray) {
            return strArray.charCodeAt();
          }));
          e.respondWith(new Response(binData, JSON.parse(unescape(step[3]))));
          break;
        case 'fetch':
          e.respondWith(fetch(unescape(step[2]), JSON.parse(unescape(step[3]))));
          break;
        case 'fetch+response':
          e.respondWith(
            fetch(unescape(step[2]), JSON.parse(unescape(step[3]))).then(function(res) {
              return res.arrayBuffer();
            }).then(function(b) {
              return new Response(b.slice(step[4], step[5]), JSON.parse(unescape(step[6])));
            }));
      }
    }
    return;
  }
  // Basic truncation example
  if (url.pathname == '/wikipedia/ru/c/c6/Glorious.ogg') {
    if (e.request.headers.get('range') == 'bytes=0-') {
      console.log('responding with fake response');
      e.respondWith(
        new Response(
          'Ogg', {status: 206, headers: {'content-range': 'bytes 0-3/5000'}}))
    } else {
      console.log('ignoring request');
    }
    return;
  }
};
