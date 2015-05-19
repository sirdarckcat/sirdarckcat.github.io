caches.open('default').then(function(cache) {
  return cache.addAll([new Request('index.html', {mode: 'no-cors'})]);
});

self.addEventListener('fetch', function(event) {
  event.respondWith(caches.match(event.request).then(function(response) {
    if (response) return response;
    return fetch(event.request);
  }));
});
