/* sphinx lab — cross-origin isolation for a host that cannot set headers.
 *
 * SharedArrayBuffer requires the document to be cross-origin isolated, which
 * normally requires two response headers. Static hosts like GitHub Pages cannot
 * set them. A service worker can: it intercepts each request and re-emits the
 * response with the headers attached, so the page becomes isolated on the next
 * navigation. The lab uses that to hold one shared copy of its 512 MB of
 * transform planes instead of one copy per worker, which takes the attack from
 * 33 transforms per step to 17.
 *
 * Nothing here is cached or rewritten beyond the two headers.
 */
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", e => e.waitUntil(self.clients.claim()));

self.addEventListener("fetch", event => {
  // leave range/cache-probe requests alone; rewriting them breaks media loading
  if (event.request.cache === "only-if-cached" && event.request.mode !== "same-origin") return;
  event.respondWith(
    fetch(event.request)
      .then(r => {
        if (r.status === 0) return r;                 // opaque response, nothing to do
        const h = new Headers(r.headers);
        h.set("Cross-Origin-Embedder-Policy", "require-corp");
        h.set("Cross-Origin-Opener-Policy", "same-origin");
        return new Response(r.body, { status: r.status, statusText: r.statusText, headers: h });
      })
      .catch(err => { console.error("[sw]", err); throw err; })
  );
});
