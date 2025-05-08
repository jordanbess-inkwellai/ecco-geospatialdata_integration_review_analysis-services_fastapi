// service-worker.js

// Listen for the install event
self.addEventListener('install', (event) => {
  console.log('Service Worker installed');
});

// Listen for the fetch event
self.addEventListener('fetch', (event) => {
  // This is where the cache logic will be added
});