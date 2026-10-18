"""Regression against the B0030 High browser QC case and joint-draw inputs."""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from biosensor_studio.features import analyze_series,design_probability
from biosensor_studio.loaders import load_csv

ROOT=Path(__file__).resolve().parents[1]
DEMO=ROOT/'docs/data/synthetic_demo.csv'


def test_nonresponsive_primary_and_alternative_shape_not_interpretable():
    df=load_csv(DEMO)
    a=analyze_series(df,'pLux','B0030_High_SYNTHETIC',n_boot=30)
    assert a.quality=='NONRESPONSIVE_HIGH'
    s=a.summary.set_index('Feature')
    for f in ['EC50_operational','EC50_Hill_FdeR','Hill_n','Hill_K','Smax_Hill']:
        assert not bool(s.loc[f,'Interpretable']), f
    for f in ['Basal','DynamicRange_total','DynamicRange_positive','Hill_R2','Hill_n_over_8']:
        assert bool(s.loc[f,'Interpretable']), f
    assert np.isfinite(s.loc['EC50_operational','Median'])
    assert np.isnan(design_probability(a,ec50_max=200)['probability'])


def test_usable_fder_estimators_remain_interpretable():
    df=load_csv(DEMO)
    a=analyze_series(df,'FdeR','R3R3_Exp1_SYNTHETIC',n_boot=30)
    assert a.quality=='USABLE'
    assert a.summary.Interpretable.all()


def test_joint_model_draws_preserve_covariance_and_threshold_one_third():
    data=load_csv(ROOT/'synthetic_posterior_joint_test.csv')
    a=analyze_series(data,'pLux','POSTERIOR_JOINT_TEST_SYNTHETIC',source='model',n_boot=150)
    assert a.quality=='USABLE'
    assert len(a.draws)==3
    assert a.draws.DynamicRange_positive.tolist()==[90.,180.,270.]
    assert a.draws.Basal.tolist()==[10.,20.,30.]
    p=design_probability(a,ec50_max=120,dr_min=170,basal_max=25)
    assert p['valid']==3
    assert p['probability']==1/3
    assert p['explanation']=='Fraction of complete posterior curves'


def test_ui_and_provenance_support_shared_interpretability_flag():
    js=(ROOT/'docs/app.js').read_text()
    assert js.count('item.Interpretable===false')==1
    assert js.count('x.Interpretable===false')==1
    assert 'Interpretable:!(' not in js
    assert "version:'GitHub Pages research beta v0.2.3'" in js
    assert (ROOT/'docs/py/features.py').read_bytes()==(ROOT/'biosensor_studio/features.py').read_bytes()
