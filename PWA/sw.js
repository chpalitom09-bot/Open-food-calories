// Service worker - Open Food Calories
// Placé dans PWA/, il contrôle le site depuis la racine (scope défini au moment
// de l'enregistrement dans index.html). Certains hébergeurs statiques (GitHub
// Pages) ne renvoient pas l'en-tête "Service-Worker-Allowed" nécessaire à un
// scope élargi : voir la note au bas de sw-register.js pour la solution.

const VERSION = 'ofc-v1';
const SHELL_CACHE = `${VERSION}-shell`;
const DATA_CACHE = `${VERSION}-data`;

const SHELL_ASSETS = [
  '../index.html',
  '../logo.png',
  './manifest.json'
];

// Installation : met en cache le strict nécessaire pour un affichage hors ligne.
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(SHELL_CACHE)
      .then(cache => cache.addAll(SHELL_ASSETS))
      .then(() => self.skipWaiting())
  );
});

// Activation : purge les anciennes versions de cache.
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(key => key.startsWith('ofc-') && key !== SHELL_CACHE && key !== DATA_CACHE)
          .map(key => caches.delete(key))
      )
    ).then(() => self.clients.claim())
  );
});

function isDataRequest(url) {
  return url.pathname.endsWith('.json');
}

self.addEventListener('fetch', event => {
  const { request } = event;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  // Données (Open-food-calories.json) : réseau d'abord, cache en secours.
  if (isDataRequest(url)) {
    event.respondWith(
      fetch(request)
        .then(response => {
          const clone = response.clone();
          caches.open(DATA_CACHE).then(cache => cache.put(request, clone));
          return response;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  // Reste du site (app shell) : cache d'abord, réseau en secours + mise à jour.
  event.respondWith(
    caches.match(request).then(cached => {
      const network = fetch(request)
        .then(response => {
          if (response && response.ok) {
            const clone = response.clone();
            caches.open(SHELL_CACHE).then(cache => cache.put(request, clone));
          }
          return response;
        })
        .catch(() => cached);
      return cached || network;
    })
  );
});

// Permet à la page de forcer l'activation immédiate d'une nouvelle version.
self.addEventListener('message', event => {
  if (event.data === 'SKIP_WAITING') self.skipWaiting();
});
