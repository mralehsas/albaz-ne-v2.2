const CACHE_NAME = 'albaz-ne-v2-2-v2-3d-fix';
const STATIC_ASSETS = [
  './site.webmanifest',
  './ALBAZ_NE_V2_2_FULL_CRITERION_AR.pdf',
  './globe-fix.js'
];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS)));
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
    ))
  );
  self.clients.claim();
});

async function injectGlobeFix(response){
  const type = response.headers.get('content-type') || '';
  if(!type.includes('text/html')) return response;
  const html = await response.text();
  const tag = '<script src="./globe-fix.js?v=2"></script>';
  const patched = html.includes('globe-fix.js')
    ? html
    : html.replace('</body>', tag + '\n</body>');
  const headers = new Headers(response.headers);
  headers.delete('content-length');
  headers.set('cache-control','no-store, max-age=0');
  return new Response(patched, {
    status: response.status,
    statusText: response.statusText,
    headers
  });
}

self.addEventListener('fetch', event => {
  if(event.request.method !== 'GET') return;

  const req = event.request;
  const isPage = req.mode === 'navigate' || req.destination === 'document';

  if(isPage){
    event.respondWith((async () => {
      try{
        const fresh = await fetch(req, {cache:'no-store'});
        const copy = fresh.clone();
        const cache = await caches.open(CACHE_NAME);
        await cache.put('./index.html', copy);
        return injectGlobeFix(fresh);
      }catch(_err){
        const cached = await caches.match('./index.html');
        if(cached) return injectGlobeFix(cached);
        throw _err;
      }
    })());
    return;
  }

  event.respondWith(
    caches.match(req).then(hit => hit || fetch(req).then(response => {
      const copy = response.clone();
      caches.open(CACHE_NAME).then(cache => cache.put(req, copy));
      return response;
    }))
  );
});
