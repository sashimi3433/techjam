const CACHE_NAME = 'moyumoyu-v1';
const urlsToCache = [
    '/',
    '/static/css/style.css',
    '/static/js/pwa.js',
    '/static/images/chara.png',
    // 必要に応じて他のリソースを追加
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                return cache.addAll(urlsToCache);
            })
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                return response || fetch(event.request);
            })
    );
});