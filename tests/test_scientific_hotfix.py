"""Synthetic scientific regression tests for the v0.2.1 hotfix."""
import sys
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pandas as pd
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from biosensor_studio.features import analytic_hill_slope,design_probability

def test_analytic_smax_diverges_only_for_hill_n_below_one():
    x=np.linspace(0.,100.,101)
    p=[.1,.8,20.,5000.]
    slope=analytic_hill_slope(x,p)
    assert np.isposinf(slope[0])
    assert np.isfinite(slope[1:]).all()
    assert np.isfinite(analytic_hill_slope(x,[.1,1.2,20.,5000.])).all()
    assert analytic_hill_slope(x,[.1,1.0,20.,5000.])[0]==pytest.approx(5000*.9/20)

def test_non_ec50_specification_does_not_censor_valid_dr_draw():
    a=SimpleNamespace(quality='USABLE',source='model',primary_ec50='EC50_operational',
        primary_dr='DynamicRange_positive',draws=pd.DataFrame({
          'EC50_operational':[np.nan,120.,np.nan],
          'DynamicRange_positive':[150.,130.,90.],
          'Basal':[100.,110.,120.]}))
    assert design_probability(a,dr_min=100)['probability']==pytest.approx(2/3)
    assert design_probability(a,basal_max=115)['probability']==pytest.approx(2/3)
    assert design_probability(a,ec50_max=125)['valid']==1
    assert design_probability(a,dr_min=100,ec50_max=125)['valid']==1

def test_deployed_engine_matches_offline_byte_for_byte():
    root=Path(__file__).resolve().parents[1]
    assert (root/'docs/py/features.py').read_bytes()==(root/'biosensor_studio/features.py').read_bytes()

def test_caution_is_embedded_in_deployed_interface():
    root=Path(__file__).resolve().parents[1]
    js=(root/'docs/app.js').read_text()
    assert 'Suppressed by QC' in js
    assert 'Interpretable' in js
