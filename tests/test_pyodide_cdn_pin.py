"""Protect the production runtime URL from accidental string substitutions."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CDN = 'https://cdn.jsdelivr.net/pyodide/v0.28.3/full/'

def test_production_pyodide_version_is_pinned_consistently():
    html = (ROOT / 'docs' / 'index.html').read_text(encoding='utf-8')
    js = (ROOT / 'docs' / 'app.js').read_text(encoding='utf-8')
    assert f'{CDN}pyodide.js' in html
    assert f"const PYODIDE_CDN = '{CDN}';" in js
    assert 'v0.2.18.3' not in html + js
    assert re.search(r'research beta v0\.2\.\d+', html, flags=re.IGNORECASE)

def test_js_and_html_same_version():
    html = (ROOT / 'docs' / 'index.html').read_text(encoding='utf-8')
    js = (ROOT / 'docs' / 'app.js').read_text(encoding='utf-8')
    html_versions = re.findall(r'cdn\.jsdelivr\.net/pyodide/(v[^/]+)/full/pyodide\.js', html)
    js_versions = re.findall(r'cdn\.jsdelivr\.net/pyodide/(v[^/]+)/full/', js)
    assert html_versions == ['v0.28.3']
    assert js_versions == ['v0.28.3']
