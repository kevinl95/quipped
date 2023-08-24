// This is the "Offline copy of pages" service worker

const CACHE = "quip-offline";

importScripts('https://storage.googleapis.com/workbox-cdn/releases/5.1.2/workbox-sw.js');

self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "SKIP_WAITING") {
    self.skipWaiting();
  }
});

workbox.routing.registerRoute(
  new RegExp('/*'),
  new workbox.strategies.StaleWhileRevalidate({
    cacheName: CACHE
  })
);

// Listen the periodic background sync events to update the cached resources.
self.addEventListener('periodicsync', event => {
  if (event.tag === 'update-cached-content') {
      event.waitUntil(updateCachedContent());
  }
});

async function updateCachedContent() {
  const requests = await findCacheEntriesToBeRefreshed();
  const cache = await caches.open(CACHE);

  for (const request of requests) {
      try {
          // Fetch the new version.
          const fetchResponse = await fetch(request);
          // Refresh the cache.
          await cache.put(request, fetchResponse.clone());
      } catch (e) {
          // Fail silently, we'll just keep whatever we already had in the cache.
      }
  }
}

// Find the entries that are already cached and that we do want to update. This way we only
// update these ones and let the user visit new pages when they are online to populate more things
// in the cache.
async function findCacheEntriesToBeRefreshed() {
  const cache = await caches.open(CACHE);
  const requests = await cache.keys();
  return requests.filter(request => {
      return !DONT_UPDATE_RESOURCES.some(pattern => request.url.includes(pattern));
  });
}