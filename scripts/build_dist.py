"""Build a root-hosted copy of site/ for classic hosting (e.g. Hostinger public_html) with the PHP mail endpoint."""
import shutil, zipfile, re
from pathlib import Path
root = Path(__file__).resolve().parents[1]
dist = root/'dist'
if dist.exists(): shutil.rmtree(dist)
shutil.copytree(root/'site', dist)
for p in dist.rglob('*'):
    if p.suffix in ('.html','.js','.css','.json'):
        t = p.read_text(encoding='utf-8')
        n = t.replace('basename:"/feucht"','basename:"/"').replace('/feucht/','/')
        n = re.sub(r'(["\'(])/feucht(["\')])', r'\1/\2', n)
        if n != t: p.write_text(n, encoding='utf-8')
cfg = (dist/'config.js').read_text()
cfg = cfg.replace('apiBase: "https://feuchtecheck.at"','apiBase: ""').replace('requestEndpoint: ""','requestEndpoint: "/api/besichtigung.php"')
(dist/'config.js').write_text(cfg)
(dist/'api').mkdir()
shutil.copy(root/'scripts/hostinger/besichtigung.php', dist/'api/besichtigung.php')
(dist/'.htaccess').write_text('DirectoryIndex index.html\nErrorDocument 404 /404.html\n')
left = [str(p) for p in dist.rglob('*') if p.suffix in ('.html','.js','.css') and re.search(r'/feucht/|basename:"/feucht"', p.read_text(encoding='utf-8'))]
assert not left, left
out = root/'feuchtecheck-hostinger.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(dist.rglob('*')):
        if p.is_file(): z.write(p, p.relative_to(dist))
print('built', out, out.stat().st_size//1024, 'KB')
