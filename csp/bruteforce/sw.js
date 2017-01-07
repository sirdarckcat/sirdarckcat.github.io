onfetch=e=>{
  var nonce = Math.floor(Math.random() * 999999999).toString(36);
  e.respondWith(
    caches.match(e.request)
      .then(r=>r?r.blob():fetch(e.request)
            .then(r=>caches.open('v1')
                  .then(c=>(c.put(e.request,r.clone()),r)))
            .then(r=>r.blob()))
    .then(b=>new Response(b, {headers: {"content-security-policy":"object-src 'none';script-src 'nonce-"+nonce+"';"}})));
}

oninstall=e=>event.waitUntil(caches.open('v1'));
