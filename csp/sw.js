onfetch = function(e) {
  if (e.request.url == 'https://www.google.com/search?q=foo') {
    // respond with favicon.ico
    e.respondWith(fetch('https://www.google.com/favicon.ico', {mode: 'no-cors'}));
  }
  if (e.request.url == 'https://www.google.com/search?q=bar') {
    // respond with a redirect to favicon.ico
    e.respondWith(fetch('https://www.google.com/url?q=/favicon.ico', {mode: 'no-cors'}));
  }
};
