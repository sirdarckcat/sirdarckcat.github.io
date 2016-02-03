navigator.serviceWorker.getRegistration().then(r=>r?document.write(location.href):navigator.serviceWorker.register('sw.js').then(r=>location.reload()));
