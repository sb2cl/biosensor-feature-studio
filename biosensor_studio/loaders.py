"""Strict adapters for the archived FdeR and pLux MATLAB files and tidy CSV.

Scientific scope:
- FdeR: reads FINAL, already window-extracted, replicate-level expressionSamples.
- pLux: computes one temporal mean per biological replicate over 360-480 min.
- No per-dose QC censoring, dose correction or negative-control subtraction.
"""
from __future__ import annotations

from pathlib import Path
import io
import numpy as np
import pandas as pd
import h5py
from scipy.io import loadmat

COLUMNS = ['system', 'series', 'source', 'dose', 'dose_unit', 'replicate',
           'signal', 'signal_unit', 'window', 'qc_annotation', 'origin']
FDER_BLOCKS = ('R3R3_Exp1', 'R4R3_Exp1', 'R4R3_Exp2', 'R4R4_Exp2', 'R3R3_Exp3')
PLUX_RBSS = ('B0030', 'B0032', 'B0034', 'J61100', 'J61101')


def _as_path_or_buffer(obj):
    if hasattr(obj, 'read'):
        return obj
    return str(obj)


def load_fder_mat(path_or_file) -> pd.DataFrame:
    """Import the frozen FdeR final_experimental_blocks MAT, not raw Data_pFdeR."""
    rows = []
    with h5py.File(_as_path_or_buffer(path_or_file), 'r') as h:
        if 'blocks' not in h:
            raise ValueError('Not a frozen FdeR experimental blocks MAT (missing blocks).')
        for key in FDER_BLOCKS:
            if key not in h['blocks']:
                continue
            grp = h['blocks'][key]
            if 'inductions' not in grp or 'expressionSamples' not in grp:
                raise ValueError('Missing induction or replicate matrix for ' + key)
            doses = np.asarray(grp['inductions'], dtype=float).ravel()
            y = np.asarray(grp['expressionSamples'], dtype=float)
            if y.shape[1] == len(doses):
                y = y.T
            elif y.shape[0] != len(doses):
                raise ValueError(f'{key}: ambiguous expressionSamples shape {y.shape}')
            if not np.any(np.isclose(doses, 0)):
                raise ValueError(f'{key}: explicit 0 uM dose is missing')
            for i, d in enumerate(doses):
                for j, val in enumerate(y[i]):
                    if np.isfinite(val):
                        rows.append(('FdeR', key, 'experiment', float(d), 'uM',
                                     str(j + 1), float(val), 'MEFL/cell',
                                     'Step1 indices 72:108', '', 'FdeR final blocks MAT'))
    if not rows:
        raise ValueError('No supported FdeR experimental blocks found.')
    return validate_tidy(pd.DataFrame(rows, columns=COLUMNS))


def load_plux_mat(path_or_file) -> pd.DataFrame:
    """Import original pLux Data_struct_pLux.mat as frozen P2 windowed replicates."""
    raw = loadmat(_as_path_or_buffer(path_or_file), squeeze_me=True,
                  struct_as_record=False, variable_names=['Data'])
    if 'Data' not in raw:
        raise ValueError('pLux MAT must contain Data.')
    data = np.atleast_1d(raw['Data']).ravel()
    if len(data) != 5:
        raise ValueError(f'Expected five pLux experiments, found {len(data)}')
    rows = []
    for idx, e in enumerate(data):
        t = np.asarray(e.time_OD, dtype=float).ravel()
        window = np.isfinite(t) & (t >= 360) & (t <= 480)
        if not np.any(window):
            raise ValueError(f'pLux experiment {idx+1} has no 360-480 min samples')
        strains = np.atleast_1d(e.medios.strains).ravel()
        if len(strains) < 3:
            raise ValueError(f'pLux experiment {idx+1} lacks its control strain')
        if 'pafso21' not in str(strains[2].Id).lower():
            raise ValueError(f'pLux experiment {idx+1}: unexpected negative control')
        for copy_idx, copy in enumerate(('High', 'Low')):
            s = strains[copy_idx]
            series = f'{PLUX_RBSS[idx]}_{copy}'
            if idx == 0:
                qc = 'NONRESPONSIVE_HIGH' if copy == 'High' else 'REVIEW'
            else:
                qc = ''
            for datum in np.atleast_1d(s.data).ravel():
                dose = float(np.asarray(datum.Inducc).ravel()[0])
                Y = np.asarray(datum.MEFLcell, dtype=float)
                if Y.ndim == 1:
                    Y = Y[:, None]
                if Y.shape[0] != len(t):
                    raise ValueError(f'{series}: time and MEFLcell dimensions differ')
                means = np.nanmean(Y[window, :], axis=0)
                if not np.any(np.isfinite(means)):
                    raise ValueError(f'{series}: no finite observations at {dose} nM')
                for rep_id, v in enumerate(means):
                    if np.isfinite(v):
                        rows.append(('pLux', series, 'experiment', dose, 'nM',
                                     str(rep_id + 1), float(v), 'MEFL/cell',
                                     'time_OD 360-480 min', qc, 'pLux Data_struct MAT'))
    return validate_tidy(pd.DataFrame(rows, columns=COLUMNS))


def validate_tidy(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize and validate row-level series. Do not silently discard doses."""
    out = df.copy()
    required = {'system', 'series', 'dose', 'signal', 'replicate'}
    missing = required - set(out.columns)
    if missing:
        raise ValueError('Missing required columns: ' + ', '.join(sorted(missing)))
    defaults = dict(source='experiment', dose_unit='', signal_unit='MEFL/cell',
                    window='unspecified', qc_annotation='', origin='uploaded CSV')
    for key, default in defaults.items():
        if key not in out.columns:
            out[key] = default
    for key in ['system', 'series', 'source', 'replicate', 'dose_unit',
                'signal_unit', 'window', 'qc_annotation', 'origin']:
        out[key] = out[key].fillna('').astype(str)
    out['source'] = out['source'].str.lower().str.strip()
    if not out['source'].isin(['experiment', 'model']).all():
        raise ValueError('source must be either experiment or model')
    for key in ('dose', 'signal'):
        out[key] = pd.to_numeric(out[key], errors='raise')
    if not np.isfinite(out[['dose', 'signal']].to_numpy(dtype=float)).all():
        raise ValueError('dose and signal must be finite; correct missing values upstream')
    if (out['dose'] < 0).any():
        raise ValueError('Negative inducer concentrations are invalid')
    if (out['signal'] < 0).any():
        raise ValueError('Negative response: use calibrated nonnegative MEFL/cell input')
    if (out['series'].str.strip() == '').any():
        raise ValueError('Every row needs series identification')
    if not out['system'].isin(['FdeR', 'pLux']).all():
        raise ValueError('system must be FdeR or pLux (capitalization matters)')
    for (system, series, src), g in out.groupby(['system', 'series', 'source']):
        if not np.any(np.isclose(g['dose'].unique(), 0)):
            raise ValueError(f'{system}/{series}/{src} lacks explicit zero-inducer control')
        if g['dose_unit'].nunique() != 1:
            raise ValueError(f'{system}/{series}/{src} mixes dose units')
        if len(g['dose'].unique()) < 3:
            raise ValueError(f'{system}/{series}/{src} needs at least three dose levels')
        dups = g.duplicated(['dose', 'replicate'])
        if dups.any():
            raise ValueError(f'{system}/{series}/{src} duplicates dose-replicate combinations')
        if src == 'model':
            count = g.groupby('replicate')['dose'].nunique()
            if count.nunique() != 1 or count.iloc[0] != g['dose'].nunique():
                raise ValueError(f'{series}: model replicate/draw must cover identical dose grid')
    return out[COLUMNS].sort_values(['system','series','source','dose','replicate']).reset_index(drop=True)


def load_csv(file_or_path) -> pd.DataFrame:
    return validate_tidy(pd.read_csv(file_or_path))


def load_any(file_or_path, name: str | None = None) -> pd.DataFrame:
    name = name or getattr(file_or_path, 'name', str(file_or_path))
    lower = Path(name).name.lower()
    if lower.endswith('.csv'):
        return load_csv(file_or_path)
    if lower.endswith('.mat'):
        if 'plux' in lower:
            return load_plux_mat(file_or_path)
        if 'experimental_blocks' in lower:
            return load_fder_mat(file_or_path)
        # Safe trial: avoid accidentally accepting arbitrary MAT structures.
        try:
            return load_fder_mat(file_or_path)
        except (OSError, ValueError, KeyError, TypeError):
            return load_plux_mat(file_or_path)
    raise ValueError('Use .csv, FdeR final experimental blocks .mat or pLux Data_struct .mat')


def inventory(df: pd.DataFrame) -> pd.DataFrame:
    return (df.groupby(['system','series','source','dose_unit','window'],dropna=False)
            .agg(doses=('dose','nunique'), observations=('signal','size'),
                 biological_replicates=('replicate','nunique'))
            .reset_index())
