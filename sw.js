const CACHE_NAME = 'albaz-official-flagship-v7-2026-09-08-nav-hardfix';
const APP_SHELL = [
  './',
  './index.html',
  './site.webmanifest',
  './ALBAZ_NE_V2_2_USER_GUIDE_AR.html'
];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(APP_SHELL)));
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  if(event.request.method !== 'GET') return;

  const req=event.request;
  const isDocument=req.mode==='navigate'||req.destination==='document';

  if(isDocument){
    event.respondWith((async()=>{
      try{
        const fresh=await fetch(req,{cache:'no-store'});
        const cache=await caches.open(CACHE_NAME);
        cache.put('./index.html',fresh.clone());
        return fresh;
      }catch(err){
        return (await caches.match('./index.html')) || (await caches.match('./'));
      }
    })());
    return;
  }

  event.respondWith((async()=>{
    const cached=await caches.match(req);
    if(cached) return cached;
    const fresh=await fetch(req);
    const cache=await caches.open(CACHE_NAME);
    cache.put(req,fresh.clone());
    return fresh;
  })());
});
