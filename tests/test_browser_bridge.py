"""Keep the Python code embedded in JavaScript syntactically valid."""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]

def test_bridge_compiles():
    js=(ROOT/'docs'/'app.js').read_text()
    start=js.index('await py.runPythonAsync(`import sys, io')+len('await py.runPythonAsync(`')
    end=js.index('`);state.py=py;',start)
    source=js[start:end].replace('\\n','\n')
    compile(source,'pyodide_bridge.py','exec')

def test_public_site_links_only_synthetic_data():
    html=(ROOT/'docs'/'index.html').read_text()
    js=(ROOT/'docs'/'app.js').read_text()
    assert './data/synthetic_demo.csv' in js
    assert 'original_frozen_observations' not in html+js
    assert 'Data_pFdeR_final' not in html+js
