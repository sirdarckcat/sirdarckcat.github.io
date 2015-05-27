onfetch = function(e) {
  var url = new URL(e.request.url);
  console.log('got a request for', url.href);
  if (url.pathname == '/wikipedia/ru/c/c6/Glorious.ogg') {
    if (e.request.headers.get('range') == 'bytes=0-') {
      console.log('responding with fake response');
      e.respondWith(
        new Response(
          'Ogg', {status: 206, headers: {'content-range': 'bytes 0-3/5000'}}))
    } else {
      console.log('ignoring request');
    }
  }
};
