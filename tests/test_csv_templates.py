"""Regression checks for the 01 / DATA downloadable CSV templates."""
from pathlib import Path
import sys
import re
import pytest
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from biosensor_studio.loaders import load_csv
from biosensor_studio.features import analyze_series, design_probability

REQUIRED={'system','series','source','dose','replicate','signal'}

@pytest.mark.parametrize('name,source,nrows',[('template_experiment.csv','experiment',36),('template_posterior.csv','model',27)])
def test_template_schema(name,source,nrows):
    p=ROOT/'docs'/'data'/name
    df=load_csv(p)
    assert len(df)==nrows
    assert REQUIRED.issubset(df.columns)
    assert set(df.source)=={source}
    assert set(df.system)=={'FdeR','pLux'}
    assert set(df.origin)=={'SYNTHETIC_TEMPLATE_ONLY'}
    assert set(df.signal_unit)=={'MEFL/cell'}
    for (_,_,_), g in df.groupby(['system','series','source']):
        assert (g.dose==0).any()
        assert g.dose.nunique()>=4
        if source=='model':
            assert g.groupby('replicate').dose.nunique().nunique()==1
            assert g.groupby('replicate').dose.nunique().iloc[0]==g.dose.nunique()


def test_experiment_template_can_be_analyzed():
    d=load_csv(ROOT/'docs'/'data'/'template_experiment.csv')
    for system in ['FdeR','pLux']:
        series=next(s for s in d[d.system==system].series.unique())
        a=analyze_series(d,system,series,n_boot=30)
        assert a.quality=='USABLE'
        assert a.summary.query('Feature=="Basal"').Median.iloc[0]>0


def test_posterior_template_preserves_joint_specification_test():
    d=load_csv(ROOT/'docs'/'data'/'template_posterior.csv')
    a=analyze_series(d,'pLux','POSTERIOR_JOINT_TEST_SYNTHETIC',source='model',n_boot=30)
    assert a.quality=='USABLE'
    assert len(a.draws)==3
    p=design_probability(a,ec50_max=120,dr_min=170,basal_max=25)
    assert p['probability']==pytest.approx(1/3)
    assert p['valid']==3


def test_links_reference_downloadable_templates():
    html=(ROOT/'docs'/'index.html').read_text(encoding='utf-8')
    for name in ['template_experiment.csv','template_posterior.csv']:
        assert f'href="./data/{name}"' in html
        assert (ROOT/'docs'/'data'/name).is_file()
    assert '<div class="section-label">01 / DATA</div>' in html
    assert re.search(r'Research beta v0\.2\.\d+', html)


def test_templates_have_no_private_files_or_data():
    for name in ['template_experiment.csv','template_posterior.csv']:
        text=(ROOT/'docs'/'data'/name).read_text(encoding='utf-8')
        for private_name in ['Data_pFdeR_final','Data_struct_pLux.mat','Exp7_screened','\\Users\\','Dropbox']:
            assert private_name not in text
