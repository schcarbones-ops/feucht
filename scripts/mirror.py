"""Download the public site and adapt its assets/router for GitHub Pages."""
import concurrent.futures, json, re, subprocess, tempfile
from pathlib import Path
ORIGIN = 'https://feuchtecheck.at'
BASE = '/feucht'
ROOT = Path(__file__).resolve().parents[1] / 'site'
CACHE = Path('/tmp/feucht-download-cache')
CACHE.mkdir(exist_ok=True)
def get(path):
    import hashlib
    key = CACHE / hashlib.sha256(path.encode()).hexdigest()
    if key.exists(): return key.read_bytes(), key.with_suffix('.mime').read_text()
    with tempfile.TemporaryDirectory() as temp:
        body = Path(temp) / 'body'
        mime = subprocess.check_output(['curl', '-fsSL', '--max-time', '60', '-o', str(body), '-w', '%{content_type}', ORIGIN + path], text=True)
        key.write_bytes(body.read_bytes())
        key.with_suffix('.mime').write_text(mime.split(';')[0])
        return key.read_bytes(), mime.split(';')[0]
def save(path, data):
    target = ROOT / path.lstrip('/')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
html, _ = get('/')
entry = re.search(r'<script type="module" crossorigin src="([^"]+)"', html.decode())[1]
js, _ = get(entry)
routes = sorted(set(re.findall(r'path:"(/[^"*]*)"', js.decode())))
assets = set(re.findall(r'(?:src|href)="(/(?:assets/|airo-[^/]+\.js|favicon)[^"]*)"', html.decode()))
assets.update(re.findall(r'["\x27`](/(?:airo-assets|images)/[^"\x27`\s<>]+)', js.decode()))
assets.update(re.findall(r'/images/[^\s"\x27`]+?\.(?:webp|png|jpg)', html.decode()+js.decode()))
assets.add('/airo-assets/uploads/pages-ratgeber-faq-bg-7d831f6b.webp')
assets.add('/airo-assets/images/pages/home/hero-basement')
assets.add('/airo-media.json')
for stylesheet in [p for p in assets if p.endswith('.css')]:
    css, _ = get(stylesheet)
    assets.update(re.findall(r'url\([\"\']?(/assets/[^)\"\']+)', css.decode()))
missing = []
image_map = {}
downloads = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    for path, future in [(p,pool.submit(get,p)) for p in sorted(assets)]:
        try: data, mime = future.result()
        except Exception:
            print('ASSET BLOCKED:',path)
            missing.append(path)
            continue
        if mime.startswith('image/') and not Path(path).suffix:
            ext = {'image/svg+xml':'.svg','image/png':'.png','image/webp':'.webp','image/jpeg':'.jpg'}.get(mime)
            if not ext: raise ValueError((path,mime))
            image_map[path] = path+ext
        downloads[path] = (data,mime)
def decode_email(hexvalue):
    data=bytes.fromhex(hexvalue)
    return ''.join(chr(x ^ data[0]) for x in data[1:])
def patch(text):
    text=re.sub(r'<span class="__cf_email__" data-cfemail="([a-f0-9]+)">.*?</span>',lambda m:decode_email(m[1]),text)
    text=re.sub(r'<a[^>]*data-cfemail="([a-f0-9]+)"[^>]*>.*?</a>',lambda m:'<a href="mailto:'+decode_email(m[1])+'">'+decode_email(m[1])+'</a>',text)
    text=re.sub(r'href="/cdn-cgi/l/email-protection#([a-f0-9]+)"',lambda m:'href="mailto:'+decode_email(m[1])+'"',text)
    for source,target in sorted(image_map.items(), key=lambda item:-len(item[0])):
        text=text.replace(source,target)
    # Root-relative static assets need the project prefix; route strings remain router-relative.
    text=text.replace('/airo-media.json', BASE+'/airo-media.json')
    text=re.sub(r'(?<=["\x27`(\s])/(airo-assets/|images/|assets/|favicon)',BASE+r'/\1',text)
    text=text.replace('https://feuchtecheck.at/airo-assets/',ORIGIN+'/airo-assets/')
    return text
for path,(data,mime) in downloads.items():
    target=image_map.get(path,path)
    if path.endswith(('.js','.css')):
        text=patch(data.decode())
        if path==entry:
            for fn in ['FF', '$F', 'v2']:
                text=text.replace('function '+fn+'(){','function '+fn+'(){return;')
            assert 'tH=u4(eH)' in text
            text=text.replace('tH=u4(eH)','tH=u4(eH,{basename:"/feucht"})')
            text=text.replace('$f.firstElementChild?$k.hydrateRoot($f,H2):$k.createRoot($f).render(H2);','$k.createRoot($f).render(H2);')
            text=text.replace('fetch("/api/', 'fetch(window.FEuchteCheckConfig.apiBase+"/api/')
            old_catch='catch{x("Etwas ist schiefgelaufen. Bitte versuchen Sie es erneut.")}finally{y(!1)}}},I='
            assert text.count(old_catch)==1
            text=text.replace(old_catch,'catch{try{const le=window.FEuchteCheckConfig.estimate(a);h(le.result),p(le.leadId),U("result",!0)}catch{x("Etwas ist schiefgelaufen. Bitte versuchen Sie es erneut.")}}finally{y(!1)}}},I=')
            old_send='catch{D("Senden fehlgeschlagen. Bitte versuchen Sie es erneut.")}finally{T(!1)}}};'
            assert text.count(old_send)==1
            text=text.replace(old_send,'catch{window.FEuchteCheckConfig.validPhone(w)?S(!0):D("Bitte geben Sie eine gültige Telefonnummer ein.")}finally{T(!1)}}};')
            text=text.replace('fetch(`/api/', 'fetch(`${window.FEuchteCheckConfig.apiBase}/api/')
        data=text.encode()
    save(target,data)
# Keep server-rendered content for every page and direct navigation/refresh.
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    for route,(data,mime) in zip(routes,pool.map(get,routes)):
        text=patch(data.decode())
        text=re.sub(r'href="/(?!/|feucht/)([^"#]*)"',lambda m:'href="'+BASE+'/'+m[1]+'"',text)
        text=text.replace('<script src="/analytics.js"></script>','')
        text=text.replace('src="/airo-', 'src="'+BASE+'/airo-')
        text=re.sub(r'<script[^>]*src="/cdn-cgi/[^"]+"[^>]*></script>', '', text)
        text=text.replace('<head>','<head>\n    <meta name="robots" content="noindex,nofollow" />\n    <script src="/feucht/config.js"></script>\n    <style>h1,h2,main a,main p,main li{overflow-wrap:anywhere}</style>')
        text='\n'.join(line.rstrip() for line in text.splitlines())+'\n'
        save('/index.html' if route=='/' else route+'/index.html',text.encode())
save('/config.js',(ROOT.parent/'scripts'/'config.template.js').read_bytes())
save('/.nojekyll',b'')
save('/404.html',(ROOT/'index.html').read_bytes())
(ROOT.parent/'routes.json').write_text(json.dumps(routes,indent=2)+'\n')
(ROOT.parent/'missing-assets.json').write_text(json.dumps(missing,indent=2)+'\n')
print(f'Saved {len(routes)} pages and {len(downloads)} assets. Missing assets: {len(missing)}')
if missing: raise SystemExit(1)
