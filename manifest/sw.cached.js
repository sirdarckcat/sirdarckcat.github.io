self.addEventListener('install', function(event) {
  event.waitUntil(caches.open('default').then(function(cache) {
    return cache.addAll([new Request('index.html', {mode: 'no-cors'})]);
  }));
});

self.addEventListener('fetch', function(event) {
  event.respondWith(caches.match(event.request));
});
