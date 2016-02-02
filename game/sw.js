self.addEventListener("fetch", function(event) {
  event.respondWith(
    fetch(event.request)
    .then(r=>r.blob())
    .then(b=>new Response(
      b, {headers: {"content-security-policy": "default-src 'self'"}})));
});
