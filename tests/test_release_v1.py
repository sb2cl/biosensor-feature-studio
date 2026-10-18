"""Release metadata, reproducibility, and source-package safety checks."""
from pathlib import Path
import re
import numpy as np
import pandas as pd
import pytest
from biosensor_studio.loaders import load_csv, validate_tidy
from biosensor_studio.features import analyze_series, design_probability

R = Path(__file__).resolve().parents[1]
DEMO = R/'docs/data/synthetic_demo.csv'

def test_metadata_copyright_authors_and_version():
    license_text=(R/'LICENSE').read_text(encoding='utf-8')
    cff=(R/'CITATION.cff').read_text(encoding='utf-8')
    authors=(R/'AUTHORS.md').read_text(encoding='utf-8')
    assert license_text.startswith('MIT License')
    assert 'Copyright (c) 2026 Universitat Polit\u00e8cnica de Val\u00e8ncia' in license_text
    assert 'permission notice shall be included in all' in license_text
    assert 'version: 1.0.0' in cff
    assert 'license: MIT' in cff
    assert 'https://orcid.org/0000-0001-5677-2702' in cff
    assert 'https://orcid.org/0000-0001-9977-7132' in cff
    assert cff.index('family-names: Boada') < cff.index('family-names: Vignoni')
    assert authors.index('Yadira Boada') < authors.index('Alejandro Vignoni')
    assert not (R/'.zenodo.json').exists()
    assert '10.5281/zenodo.' not in cff

def test_ui_and_json_export_share_release_version():
    html=(R/'docs/index.html').read_text(encoding='utf-8')
    app=(R/'docs/app.js').read_text(encoding='utf-8')
    assert 'Release v1.0.0' in html
    assert 'v1.0.0 research software' in html
    assert "version:'BioSensor Feature Studio v1.0.0'" in app
    assert 'v0.2.5' not in html+app
    assert (R/'docs/py/features.py').read_bytes() == (R/'biosensor_studio/features.py').read_bytes()

def test_downloadable_template_links_exist_and_asset_present():
    h=(R/'docs/index.html').read_text(encoding='utf-8')
    assert (R/'docs/assets/sb2cl-lab-logo.png').stat().st_size>100
    assert 'BRANDING_AND_ASSETS.md' in (R/'README.md').read_text(encoding='utf-8')
    for filename in ['template_experiment.csv','template_posterior.csv']:
        assert (R/'docs/data'/filename).is_file()
        assert f'href="./data/{filename}"' in h

@pytest.mark.parametrize('system,series', [
    ('FdeR','R3R3_Exp1_SYNTHETIC'),
    ('pLux','B0032_High_SYNTHETIC')])
def test_synthetic_bootstrap_same_seed_is_exactly_repeatable(system,series):
    d=load_csv(DEMO)
    a=analyze_series(d,system,series,n_boot=40,seed=20261016)
    b=analyze_series(d,system,series,n_boot=40,seed=20261016)
    pd.testing.assert_frame_equal(a.draws,b.draws,check_exact=True)
    pd.testing.assert_frame_equal(a.summary,b.summary,check_exact=True)
    assert a.quality=='USABLE'

@pytest.mark.parametrize('seed',[20261016,20261017,20261018])
def test_experimental_synthetic_multi_seed_has_valid_primary_output(seed):
    df=load_csv(DEMO)
    a=analyze_series(df,'FdeR','R3R3_Exp1_SYNTHETIC',n_boot=60,seed=seed)
    e=a.summary.set_index('Feature').loc['EC50_Hill_FdeR']
    assert a.quality=='USABLE'
    assert np.isfinite(e['Median'])
    assert 0 < e['CI2p5'] <= e['Median'] <= e['CI97p5'] < 1400
    assert bool(e['Interpretable'])

def test_posterior_draws_joint_are_not_mixed_across_dose():
    df=load_csv(R/'docs/data/template_posterior.csv')
    a=analyze_series(df,'pLux','POSTERIOR_JOINT_TEST_SYNTHETIC',
                     source='model',n_boot=30)
    prob=design_probability(a,ec50_max=120,dr_min=170,basal_max=25)
    assert len(a.draws)==3 and prob['valid']==3
    assert prob['probability']==pytest.approx(1/3)

def test_no_private_reference_artifacts_bundled():
    for patt in ['*.mat','*.h5','*.hdf5']:
        assert not list(R.rglob(patt)), patt
    for dname in ['private_data','private_validation','private_frozen']:
        assert not (R/dname).exists()

@pytest.mark.parametrize('name,signals,expected', [
    ('FLAT', [100,100,100,100,100], 'NONRESPONSIVE'),
    ('NONMONOTONE', [100,400,110,120,105], 'REVIEW'),
])
def test_unannotated_weak_curves_are_not_accepted_as_usable(name,signals,expected):
    import warnings
    rows=[dict(system='pLux',series=name,source='experiment',dose=d,
               replicate=str(j),signal=y)
          for d,y in zip([0,20,50,100,200],signals) for j in range(3)]
    d=validate_tidy(pd.DataFrame(rows))
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', category=RuntimeWarning)
        a=analyze_series(d,'pLux',name,n_boot=30)
    assert a.quality==expected
    s=a.summary.set_index('Feature')
    assert not bool(s.loc['EC50_operational','Interpretable'])
    assert np.isnan(design_probability(a,dr_min=100)['probability'])
