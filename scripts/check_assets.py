"""Prevent publishing a snapshot whose required files are missing."""
import json, re
from pathlib import Path
root = Path(__file__).resolve().parents[1]
missing = json.loads((root/'missing-assets.json').read_text())
for page in (root/'site').rglob('*.html'):
    for url in re.findall(r'(?:src|href)="(/feucht/[^"?#]+)"',page.read_text()):
        target = root/'site'/url.removeprefix('/feucht/')
        if not target.exists(): missing.append(url)
if missing:
    raise SystemExit('Missing required files:\n'+'\n'.join(sorted(set(missing))))
print('All referenced local files exist.')
