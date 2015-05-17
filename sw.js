var dbPromise = new Promise(function(resolve, reject) {
  var dbRequest = indexedDB.open("RequestDatabase", 1);
  dbRequest.onupgradeneeded = function(e) {
    e.target.result.createObjectStore("requests", {autoIncrement: true});
    resolve(e.target.result);
  };
  dbRequest.onsuccess = function(e) {
    resolve(e.target.result);
  };
  dbRequest.onerror = reject;
});

self.addEventListener('fetch', function(event) {
  var url = new URL(event.request.url);
  if (url.pathname.match(/\/sw\/fetch$/))
    event.respondWith(fetch(new Request(
      unescape(url.search.match(/(?:&|^\?)url=([^&]+)/)[1]),
      JSON.parse(unescape(url.search.match(/(?:&|^\?)init=([^&]+)/)[1])))));
  if (url.pathname.match(/\/sw\/response$/))
    event.respondWith(new Response(
      unescape(url.search.match(/(?:&|^\?)response=([^&]+)/)[1]),
      JSON.parse(unescape(url.search.match(/(?:&|^\?)init=([^&]+)/)[1]))));
  if (url.pathname.match(/\/sw\/request$/))
    dbPromise.then(function(db) {
      db.transaction(["requests"], "readwrite").objectStore("requests").add(JSON.stringify(event.request));
    });
});
