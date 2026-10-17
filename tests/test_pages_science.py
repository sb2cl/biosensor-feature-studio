"""Synthetic-only regression checks for public GitHub Pages release."""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from biosensor_studio.features import operational_ec50,curve_features,analyze_series,design_probability
from biosensor_studio.loaders import load_csv
DEMO=ROOT/'docs'/'data'/'synthetic_demo.csv'

def test_public_dataset_is_synthetic():
    d=load_csv(DEMO)
    assert len(d)==232
    assert set(d['origin'])=={'SYNTHETIC_DEMO_ONLY'}
    assert d.series.nunique()==5

def test_fder_system_specific_estimator():
    d=load_csv(DEMO)
    a=analyze_series(d,'FdeR','R3R3_Exp1_SYNTHETIC',n_boot=30)
    assert a.quality=='USABLE'
    assert a.primary_dr=='DynamicRange_total'
    assert a.primary_ec50=='EC50_Hill_FdeR'
    assert 80<a.summary.query('Feature=="EC50_Hill_FdeR"').Median.iloc[0]<140

def test_plux_operational_vs_hill():
    d=load_csv(DEMO)
    a=analyze_series(d,'pLux','B0032_High_SYNTHETIC',n_boot=40)
    assert a.primary_dr=='DynamicRange_positive'
    assert a.primary_ec50=='EC50_operational'
    assert 90<a.summary.query('Feature=="EC50_operational"').Median.iloc[0]<140

def test_qc_overrides_numeric_crossing():
    d=load_csv(DEMO)
    a=analyze_series(d,'pLux','B0030_High_SYNTHETIC',n_boot=30)
    assert a.quality=='NONRESPONSIVE_HIGH'
    assert np.isnan(design_probability(a,ec50_max=400)['probability'])

def test_model_draw_covariance_preserved():
    data=[]
    for i,fac in enumerate([1.,2.,3.]):
        for dose,base in [(0,10),(50,30),(100,80),(200,100)]:
            data.append(dict(system='pLux',series='SIM',source='model',dose=dose,replicate=str(i),signal=base*fac,dose_unit='nM',window='simulated',qc_annotation=''))
    a=analyze_series(pd.DataFrame(data),'pLux','SIM',source='model',n_boot=50)
    assert a.draws.DynamicRange_positive.tolist()==[90.,180.,270.]
    assert design_probability(a,dr_min=180)['probability']==pytest.approx(2/3)

def test_crossing_uses_monotone_envelope():
    assert operational_ec50(np.array([0.,20.,40.,100.]),np.array([10.,30.,25.,50.]))==pytest.approx(20.)
    assert np.isnan(operational_ec50(np.array([0.,20.,40.,100.]),np.array([15.,10.,5.,12.])))
