// Facade Suite – Service Worker (offline partiel)
// Note: ce fichier doit rester dans /public pour être servi à la racine (/sw.js)

const CACHE_NAME = 'facade-suite-v1'

// Petite base offline : shell + manifest
const URLS_TO_CACHE = ['/', '/index.html', '/manifest.json']

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(URLS_TO_CACHE)
    })
  )
})

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((name) => {
          if (name !== CACHE_NAME) return caches.delete(name)
          return undefined
        })
      )
    })
  )
})

self.addEventListener('fetch', (event) => {
  // Network-first pour éviter de servir une app obsolète.
  // Fallback cache si offline.
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // On ne met en cache que les requêtes GET.
        if (event.request.method === 'GET') {
          const copy = response.clone()
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy))
        }
        return response
      })
      .catch(() => caches.match(event.request))
  )
})
