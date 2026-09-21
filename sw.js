/* Service worker de Partes de campo UNEI.
   Guarda la app en el móvil para que abra sin cobertura.
   Al publicar una versión nueva, sube el número de CACHE. */

var CACHE = "partes-unei-v4";

var ARCHIVOS = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./jszip.min.js",
  "./jspdf.umd.min.js",
  "./icon-192.png",
  "./icon-512.png",
  "./icon-maskable-512.png",
  "./plantillas/index.json"
];

self.addEventListener("install", function (e) {
  e.waitUntil(
    caches.open(CACHE)
      .then(function (c) { return c.addAll(ARCHIVOS); })
      .then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener("activate", function (e) {
  e.waitUntil(
    caches.keys().then(function (ks) {
      return Promise.all(ks.map(function (k) { return k === CACHE ? null : caches.delete(k); }));
    }).then(function () { return self.clients.claim(); })
  );
});

self.addEventListener("fetch", function (e) {
  var req = e.request;
  if (req.method !== "GET") return;
  var url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  // Las plantillas se piden frescas cuando hay red, y se sirven de caché cuando no.
  if (url.pathname.indexOf("/plantillas/") >= 0) {
    e.respondWith(
      fetch(req).then(function (res) {
        if (res && res.ok) {
          var copia = res.clone();
          caches.open(CACHE).then(function (c) { c.put(req, copia); });
        }
        return res;
      }).catch(function () { return caches.match(req); })
    );
    return;
  }

  e.respondWith(
    caches.match(req).then(function (hit) {
      if (hit) return hit;
      return fetch(req).then(function (res) {
        if (res && res.ok) {
          var copia = res.clone();
          caches.open(CACHE).then(function (c) { c.put(req, copia); });
        }
        return res;
      }).catch(function () { return caches.match("./index.html"); });
    })
  );
});
