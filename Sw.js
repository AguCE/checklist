/* Service worker de Partes de campo UNEI.
   Guarda la app en el móvil para que abra sin cobertura.
   Al publicar una versión nueva, sube el número de CACHE y los móviles
   se actualizarán solos la próxima vez que abran la app con datos. */

var CACHE = "partes-unei-v1";

var ARCHIVOS = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./icon-192.png",
  "./icon-512.png",
  "./icon-maskable-512.png"
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
    caches.keys()
      .then(function (claves) {
        return Promise.all(claves.map(function (k) {
          return k === CACHE ? null : caches.delete(k);
        }));
      })
      .then(function () { return self.clients.claim(); })
  );
});

self.addEventListener("fetch", function (e) {
  var req = e.request;
  if (req.method !== "GET") return;

  var url = new URL(req.url);

  // Solo servimos desde caché lo nuestro. Las fuentes de Google y las
  // llamadas a SharePoint van a la red tal cual; si no hay, la app
  // funciona igual con la tipografía del sistema y deja el parte pendiente.
  if (url.origin !== self.location.origin) return;

  e.respondWith(
    caches.match(req).then(function (hit) {
      if (hit) return hit;
      return fetch(req).then(function (res) {
        if (res && res.ok) {
          var copia = res.clone();
          caches.open(CACHE).then(function (c) { c.put(req, copia); });
        }
        return res;
      }).catch(function () {
        return caches.match("./index.html");
      });
    })
  );
});