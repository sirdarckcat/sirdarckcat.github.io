caches.open('default').then(function(cache) {
  return fetch(new Request('index.html', {mode: 'no-cors'})).then(function(response) {
    return cache.put(new Request('index.html', {mode: 'no-cors'}), response);
  });
});

self.addEventListener('fetch', function(event) {
  event.respondWith(caches.match(event.request).then(function(response) {
    if (response) return response;
    return fetch(event.request);
  }));
});
