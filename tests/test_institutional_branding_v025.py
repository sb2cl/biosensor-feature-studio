from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_institutional_identity():
    html=(ROOT/'docs/index.html').read_text(encoding='utf8')
    assert 'Developed by SB2CL' in html
    assert 'Universitat Politècnica de València' in html
    assert 'https://www.ai2.upv.es/en/sb2cl/' in html
    assert 'https://github.com/sb2cl/biosensor-feature-studio' in html
    assert 'Research beta v0.2.5' in html
    assert (ROOT/'docs/assets/sb2cl-lab-logo.png').is_file()

def test_export_provenance_version():
    js=(ROOT/'docs/app.js').read_text(encoding='utf8')
    assert 'v0.2.5' in js
    assert 'v0.2.4' not in js

def test_existing_scientific_code_unaffected():
    # This is pinned in the build test by byte-to-byte comparisons.
    assert (ROOT/'docs/py/features.py').is_file()
    assert (ROOT/'biosensor_studio/features.py').is_file()
