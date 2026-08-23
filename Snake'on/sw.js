/* Service worker — Snake'on
   Bump CACHE_VERSION à chaque déploiement pour forcer la mise à jour côté joueurs. */
const CACHE_VERSION = 'v5';
const CACHE = 'snakeon-' + CACHE_VERSION;

const ASSETS = [
  './index.html',
  './manifest.webmanifest',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/maskable-512.png',
  './icons/apple-touch-icon.png',
  './icons/favicon-64.png',
  './fonts/tektur-var.woff2',
  './fonts/rajdhani-400.woff2',
  './fonts/rajdhani-500.woff2',
  './fonts/rajdhani-600.woff2',
  './fonts/rajdhani-700.woff2'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE)
      .then((cache) => cache.addAll(ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// La page : réseau d'abord (pour recevoir les mises à jour), cache en secours (hors-ligne).
async function networkFirst(request) {
  const cache = await caches.open(CACHE);
  try {
    const response = await fetch(request);
    if (response && response.ok) cache.put('./index.html', response.clone());
    return response;
  } catch (err) {
    return (await cache.match('./index.html')) || (await cache.match('./')) || Response.error();
  }
}

// Les assets : cache d'abord (démarrage instantané), réseau en secours.
async function cacheFirst(request) {
  const cache = await caches.open(CACHE);
  const hit = await cache.match(request);
  if (hit) return hit;
  try {
    const response = await fetch(request);
    if (response && response.ok) cache.put(request, response.clone());
    return response;
  } catch (err) {
    return hit || Response.error();
  }
}

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') return;
  if (new URL(request.url).origin !== self.location.origin) return;
  if (request.mode === 'navigate') { event.respondWith(networkFirst(request)); return; }
  event.respondWith(cacheFirst(request));
});
