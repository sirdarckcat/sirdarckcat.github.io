self.addEventListener("fetch", function(event) {
  event.respondWith(
    fetch(event.request)
    .then(r=>new Response(
      r, {headers: {"content-security-policy": "default-src 'self'"}})));
});
