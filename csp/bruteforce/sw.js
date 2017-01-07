onfetch=e=>{
  var nonce = Math.floor(Math.random() * 999999999).toString(36);
  e.respondWith(fetch(e.request).then(r=>r.blob()).then(b=>new Response(b, {headers: {"content-security-policy":"object-src 'none';script-src 'nonce-"+nonce+"';"}})));
}
