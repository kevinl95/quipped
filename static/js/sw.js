// This is the "Offline copy of pages" service worker

const CACHE = "pwabuilder-offline";

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

const status = await navigator.permissions.query({
  // @ts-ignore
  name: 'periodic-background-sync',
});

if (status.state === 'granted') {
  navigator.serviceWorker.ready.then(async (sw: any) => {
    await sw.periodicSync.register('periodicsync', {
      minInterval: 24 * 60 * 60 * 1000,
    });
  })
    .catch(error => {
      console.error('[BackgroundSync] Error: ' + JSON.stringify(error, null, 2));
    });
}
else {
  console.error('[BackgroundSync] Does not have permission');
}
}