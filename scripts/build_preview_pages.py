"""Build static previews of the two last funnel screens from saved copies of the live pages.
No API logic: forms are inert. Usage: build_preview_pages.py <result.html> <confirmation.html>"""
import re, sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
BASE = '/feucht'
def build(src, out, title):
    h = Path(src).read_text(encoding='utf-8')
    m = re.search(r'<div id="app"[^>]*>(.*)</div>\s*<script type="text/javascript"', h, re.S)
    body = m.group(1)
    body = re.sub(r'src="\./[^"]*_files/horizontal"', f'src="{BASE}/airo-assets/images/logo/horizontal.png"', body)
    body = re.sub(r'src="\./[^"]*_files/trust-ssl"', f'src="{BASE}/airo-assets/images/footer/trust-ssl.webp"', body)
    body = body.replace('href="https://feuchtecheck.at/', f'href="{BASE}/')
    body = re.sub(r'href="/feucht/(?=")', '/feucht/', body)
    body = re.sub(r'Wir rufen Sie unter [^ ]*? an\.', 'Wir rufen Sie unter der angegebenen Nummer an.', body)
    body = body.replace('disabled=""', 'disabled="" aria-disabled="true"')
    page = f'''<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex"><title>{title} | FeuchteCheck.at</title>
<link rel="icon" href="{BASE}/favicon.ico"><link rel="stylesheet" href="{BASE}/assets/index-B5CS45CU.css">
</head><body class="fs-unmask-airo-app-builder"><div id="app">{body}</div></body></html>
'''
    p = root/'site'/out/'index.html'; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(page, encoding='utf-8')
build(sys.argv[1], 'check/ergebnis', 'Ihre Ersteinschätzung')
build(sys.argv[2], 'check/bestaetigung', 'Anfrage gesendet')
