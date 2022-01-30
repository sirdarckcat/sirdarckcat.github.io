const CACHE_VERSION = 'v0test1';
oninstall = event => {
  event.waitUntil(
    caches.open(CACHE_VERSION).then(cache => cache.addAll([
        // './tf-core.js',
        // './tf-backend-cpu.js',
        // './ring-buffer.js',
        // './processor1.js',
        // './eear.js',
        // './index.html'
      ])
    )
  );
};

onactivate = event => {
  event.waitUntil(clients.claim());
};

onfetch = event => {
  event.respondWith((async () => {
    const cache = await caches.open(CACHE_VERSION);
    let response = await cache.match(event.request);
    if (!response) {
      response = await fetch(event.request);
    }
    const newHeaders = new Headers(response.headers);
    newHeaders.append('Cross-Origin-Opener-Policy', 'same-origin');
    newHeaders.append('Cross-Origin-Embedder-Policy', 'require-corp');
    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: newHeaders
    });
  })());
};
