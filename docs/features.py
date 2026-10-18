"""System-aware feature estimators operating on a shared dose-response schema.

FdeR: total DR + 4-parameter Hill fit with EC50 extracted from its fitted
finite-range 50% excursion on 1000 grid points (mirrors biosensorStats4).
pLux: positive excursion + monotone-envelope operational EC50 (mirrors P2).
Both alternatives are available as DIAGNOSTICS. This is an independent Python
implementation, not a byte-for-byte re-execution of MATLAB bootstrap/solvers.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import numpy as np
import pandas as pd
from scipy.optimize import least_squares
from scipy.special import expit
from scipy.stats import spearmanr

METRICS = ('Basal', 'DynamicRange_total', 'DynamicRange_positive',
           'EC50_operational', 'EC50_Hill_FdeR', 'Hill_n', 'Hill_K',
           'Hill_R2', 'Smax_Hill', 'Hill_n_over_8')


@dataclass
class Analysis:
    system: str
    series: str
    source: str
    dose_unit: str
    window: str
    quality: str
    warnings: list[str]
    observed: pd.DataFrame
    curves: pd.DataFrame
    draws: pd.DataFrame
    summary: pd.DataFrame
    primary_dr: str
    primary_ec50: str
    config: dict


def _hill(x: np.ndarray, p: np.ndarray) -> np.ndarray:
    """Numerically safe form of scaled four-parameter Hill response."""
    x = np.asarray(x, float)
    b0, n, k, scale = p
    ratio = np.zeros_like(x, dtype=float)
    positive = x > 0
    if np.any(positive):
        z = n * (np.log(x[positive]) - np.log(max(k, 1e-14)))
        ratio[positive] = 1.0 / (1.0 + np.exp(-np.clip(z, -700, 700)))
    return scale * (b0 + (1.0 - b0) * ratio)


def analytic_hill_slope(x: np.ndarray, p: np.ndarray) -> np.ndarray:
    """Analytic dy/dx on the full dose grid, matching frozen MATLAB semantics.

    For n<1 the derivative at inducer=0 diverges; its Smax is +Inf,
    excluded from finite CI summaries. Never approximate that singular
    derivative with a grid-dependent finite difference.
    """
    x = np.asarray(x, dtype=float)
    b0, n, k, scale = map(float, p)
    out = np.empty_like(x, dtype=float)
    pos = x > 0
    if np.any(pos):
        frac = expit(n * (np.log(x[pos]) - np.log(k)))
        out[pos] = scale * (1.0 - b0) * n * frac * (1.0 - frac) / x[pos]
    if np.any(~pos):
        if n < 1.0:
            out[~pos] = np.inf
        elif n > 1.0:
            out[~pos] = 0.0
        else:
            out[~pos] = scale * (1.0 - b0) / k
    return out


def hill_fit(x: np.ndarray, y: np.ndarray, profile: str = 'FdeR') -> dict:
    """Fit descriptive Hill with system-specific bounds, return diagnostics."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    invalid = dict(valid=False, EC50_Hill_FdeR=np.nan, Hill_n=np.nan,
                   Hill_K=np.nan, Hill_R2=np.nan, Smax_Hill=np.nan,
                   Hill_n_over_8=np.nan)
    if (len(x) < 4 or not np.all(np.isfinite(x)) or
            not np.all(np.isfinite(y)) or np.max(y) <= np.min(y) or
            np.max(y) <= 0):
        return invalid
    if profile == 'pLux':
        up_n = 8.0
        K0 = operational_ec50(x, y)
        if not np.isfinite(K0) or K0 <= 0:
            K0 = float(np.median(x[x > 0]))
        ymin, ymax = float(np.min(y)), float(np.max(y))
        initial = [np.clip(ymin / ymax, .001, .95), 2.0, K0, ymax]
        lower = [0, .2, .01, 0]
        upper = [1, up_n, max(x)*5, max(y)*10]
    else:
        # MATLAB original FdeR has unbounded n and K. Finite numerical
        # ceilings are safety controls, not the same optimization problem.
        up_n = 50.0
        initial = [.1, 2., max(float(np.median(x)), .001), float(np.max(y))]
        lower = [0, .001, 1e-9, 0]
        upper = [1., up_n, max(max(x), 1.) * 1e5, max(max(y), 1.) * 1e5]
    scale = max(float(np.max(y) - np.min(y)), 1.0)
    try:
        fit = least_squares(lambda p: (_hill(x, p) - y) / scale,
                            x0=np.asarray(initial),
                            bounds=(lower, upper),
                            max_nfev=500, xtol=1e-9, ftol=1e-9, gtol=1e-9)
        p = fit.x
        if not np.all(np.isfinite(p)) or not fit.success:
            return invalid
        yhat = _hill(x, p)
        rss = float(np.sum((y - yhat)**2))
        tss = float(np.sum((y - np.mean(y))**2))
        r2 = 1 - rss/tss if tss > 0 else np.nan
        fine = np.linspace(float(x.min()), float(x.max()), 1000)
        yfine = _hill(fine, p)
        midpoint = .5 * (float(np.max(yfine)) + float(np.min(yfine)))
        ec50 = float(fine[np.argmin(np.abs(yfine - midpoint))])
        smax = float(np.max(analytic_hill_slope(fine, p)))
        return dict(valid=True, EC50_Hill_FdeR=ec50, Hill_n=float(p[1]),
                    Hill_K=float(p[2]), Hill_R2=r2, Smax_Hill=smax,
                    Hill_n_over_8=float(p[1] > 8 - 1e-4))
    except (ValueError, FloatingPointError, OverflowError):
        return invalid


def operational_ec50(doses: np.ndarray, response: np.ndarray) -> float:
    """Exact conceptual P2 rule: 0-dose basal, positive excursion, cummax."""
    x = np.asarray(doses, dtype=float).ravel()
    y = np.asarray(response, dtype=float).ravel()
    order = np.argsort(x)
    x, y = x[order], y[order]
    zero = np.flatnonzero(np.isclose(x, 0, atol=1e-12, rtol=0))
    if len(zero) != 1:
        raise ValueError('Operational EC50 requires exactly one zero-dose row')
    basal = y[zero[0]]
    excursion = float(np.max(y) - basal)
    if not np.isfinite(excursion) or excursion <= 0:
        return np.nan
    target = basal + .5 * excursion
    envelope = np.maximum.accumulate(y)
    match = np.flatnonzero(envelope >= target)
    if not len(match):
        return np.nan
    k = int(match[0])
    if k == 0:
        return float(x[0])
    x0, x1 = float(x[k-1]), float(x[k])
    y0, y1 = float(envelope[k-1]), float(envelope[k])
    if abs(y1-y0) < np.finfo(float).eps:
        return (x0+x1)/2
    f = np.clip((target-y0)/(y1-y0), 0, 1)
    return x0 + float(f)*(x1-x0)


def curve_features(doses, y, system: str, fit_hill: bool = True) -> dict:
    x = np.asarray(doses, dtype=float)
    y = np.asarray(y, dtype=float)
    zero = np.flatnonzero(np.isclose(x, 0, atol=1e-12, rtol=0))
    if len(zero) != 1:
        raise ValueError('Exactly one explicit 0-inducer dose is required')
    basal = float(y[zero[0]])
    vals = dict(Basal=basal,
                DynamicRange_total=float(np.max(y)-np.min(y)),
                DynamicRange_positive=float(np.max(y)-basal),
                EC50_operational=operational_ec50(x, y))
    fit = hill_fit(x, y, 'pLux' if system == 'pLux' else 'FdeR') if fit_hill else {}
    for k in METRICS:
        if k not in vals:
            vals[k] = float(fit.get(k, np.nan))
    return vals


def _observed_curves(g: pd.DataFrame, n_boot: int, seed: int,
                     jitter: float, system: str) -> tuple[np.ndarray,np.ndarray,np.ndarray]:
    rng = np.random.default_rng(seed)
    doses = np.array(sorted(g['dose'].unique()), dtype=float)
    central = []
    boot = np.empty((n_boot, len(doses)))
    for col, d in enumerate(doses):
        vals = g.loc[g['dose'] == d, 'signal'].to_numpy(dtype=float)
        central.append(float(np.median(vals)))
        indices = rng.integers(0, len(vals), size=(n_boot, len(vals)))
        samples = vals[indices].copy()
        if jitter > 0 and len(vals) > 1:
            sd = float(np.std(vals, ddof=1))
            samples += jitter * sd * rng.standard_normal(samples.shape)
            samples = np.maximum(samples, 0)
        boot[:, col] = np.median(samples, axis=1)
    return doses, np.asarray(central), boot


def _posterior_curves(g: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Every model 'replicate' is one WHOLE posterior dose-response curve."""
    pivot = g.pivot(index='replicate', columns='dose', values='signal').sort_index(axis=1)
    if pivot.isna().any().any():
        raise ValueError('Every posterior draw must contain the full dose grid')
    doses = pivot.columns.to_numpy(dtype=float)
    draws = pivot.to_numpy(dtype=float)
    return doses, np.median(draws, axis=0), draws


def analyze_series(df: pd.DataFrame, system: str, series: str,
                   source: str = 'experiment', n_boot: int = 300,
                   seed: int = 20261016, jitter: Optional[float] = None,
                   fit_hill: bool = True) -> Analysis:
    group = df[(df.system == system) & (df.series == series) &
               (df.source == source)]
    if len(group) == 0:
        raise ValueError(f'No observations for {system}/{series}/{source}')
    if n_boot < 10 or n_boot > 20000:
        raise ValueError('Bootstrap size must lie in [10,20000]')
    if jitter is None:
        jitter = 0.07 if system == 'FdeR' else 0.0
    if jitter < 0 or jitter > 0.5:
        raise ValueError('Jitter must be in [0, 0.5]')
    if source == 'experiment':
        doses, y, boot_curves = _observed_curves(group, n_boot, seed, jitter, system)
    else:
        doses, y, boot_curves = _posterior_curves(group)
    point = curve_features(doses, y, system, fit_hill=fit_hill)
    fits = [curve_features(doses, curve, system, fit_hill=fit_hill)
            for curve in boot_curves]
    draws = pd.DataFrame(fits)
    primary_dr = 'DynamicRange_total' if system == 'FdeR' else 'DynamicRange_positive'
    primary_ec50 = 'EC50_Hill_FdeR' if system == 'FdeR' else 'EC50_operational'
    annotation = next((q for q in group.qc_annotation.unique() if q.strip()), '')
    rho = float(spearmanr(doses, y).statistic)
    quality = annotation if annotation else 'USABLE'
    warnings = []
    if np.nanmax(y) <= float(y[np.argmin(np.abs(doses))]):
        quality = 'NONRESPONSIVE' if not annotation else annotation
        warnings.append('No positive excursion above the 0-dose basal.')
    if system == 'pLux' and np.isfinite(rho) and rho < .70:
        if not annotation:
            quality = 'REVIEW'
        warnings.append(f'Spearman rho={rho:.3f} below pLux P2 QC value 0.70.')
    if annotation == 'NONRESPONSIVE_HIGH':
        warnings.append('Archived quality annotation: EC50 is NOT INTERPRETABLE.')
    if annotation == 'REVIEW':
        warnings.append('Archived quality annotation: do not treat EC50 as validated.')
    if fit_hill and np.mean(draws.Hill_n_over_8.fillna(0)) > .5:
        warnings.append('Many Hill fits require n near/above 8; review estimator dependence.')
    if fit_hill and system == 'FdeR':
        n_divergent = int(np.sum(np.isinf(draws.Smax_Hill.to_numpy(dtype=float))))
        if n_divergent:
            warnings.append(
                f'Analytical Hill slope diverges at zero for n<1 in {n_divergent}/{len(draws)} '
                'draws; nonfinite Smax draws are excluded from finite uncertainty summaries, '
                'matching frozen MATLAB behavior.')
    valid_fraction = float(np.isfinite(draws[primary_ec50]).mean())
    if valid_fraction < 0.8:
        quality = 'REVIEW' if quality == 'USABLE' else quality
        warnings.append('Fewer than 80% valid primary EC50 estimates.')
    if source == 'model':
        warnings.append('Model intervals are across supplied posterior draws; observation noise is excluded.')
    else:
        warnings.append('Experimental intervals resample biological replicates within doses.')
    if system == 'FdeR':
        warnings.append('Python Hill optimization may differ from frozen MATLAB lsqcurvefit; do not replace published estimates.')
    vals = []
    for feature in METRICS:
        a = draws[feature].to_numpy(dtype=float)
        a = a[np.isfinite(a)]
        vals.append(dict(Feature=feature,
                         Role=('PRIMARY' if feature in (primary_dr, primary_ec50) else 'DIAGNOSTIC'),
                         Point=point[feature],
                         Median=float(np.median(a)) if len(a) else np.nan,
                         CI2p5=float(np.percentile(a, 2.5)) if len(a) else np.nan,
                         CI97p5=float(np.percentile(a, 97.5)) if len(a) else np.nan,
                         ValidPct=100*len(a)/len(draws)))
    summary = pd.DataFrame(vals)
    observed = (group.groupby('dose').signal.agg(
        n='size', median='median', mean='mean', std='std').reset_index())
    observed['dose_unit'] = group.dose_unit.iloc[0]
    cbands = []
    for i, d in enumerate(doses):
        a = boot_curves[:, i]
        cbands.append(dict(dose=d, point=y[i], median=np.median(a),
                           low=np.percentile(a, 2.5), high=np.percentile(a, 97.5)))
    config = dict(system=system, series=series, source=source, seed=seed,
                  n_draws=len(draws), jitter=jitter,
                  observation_window=group.window.iloc[0],
                  quality=quality, primary_dr=primary_dr,
                  primary_ec50=primary_ec50,
                  estimators={'FdeR':'4-param scaled Hill fit, midpoint of fitted 0-max finite-range curve',
                              'pLux':'monotone-envelope operational EC50'} ,
                  implementation='Python independent method, not MATLAB numerical identity')
    return Analysis(system, series, source, group.dose_unit.iloc[0],
                    group.window.iloc[0], quality, warnings, observed,
                    pd.DataFrame(cbands), draws, summary,
                    primary_dr, primary_ec50, config)


def design_probability(analysis: Analysis, ec50_max: float | None = None,
                       dr_min: float | None = None,
                       basal_max: float | None = None) -> dict:
    """Empirical joint fraction over archived simulations OR bootstrap samples."""
    if analysis.quality not in ('USABLE', ''):
        return dict(probability=np.nan, valid=0, explanation='Response flagged; not interpretable as specification reliability.')
    conditions = []
    if ec50_max is not None:
        conditions.append(analysis.draws[analysis.primary_ec50].to_numpy() <= ec50_max)
    if dr_min is not None:
        conditions.append(analysis.draws[analysis.primary_dr].to_numpy() >= dr_min)
    if basal_max is not None:
        conditions.append(analysis.draws.Basal.to_numpy() <= basal_max)
    if not conditions:
        return dict(probability=np.nan, valid=0, explanation='Set at least one design threshold.')
    metrics = []
    if ec50_max is not None:
        metrics.append(analysis.primary_ec50)
    if dr_min is not None:
        metrics.append(analysis.primary_dr)
    if basal_max is not None:
        metrics.append('Basal')
    valid = np.ones(len(analysis.draws), dtype=bool)
    for metric in metrics:
        valid &= np.isfinite(analysis.draws[metric].to_numpy(dtype=float))
    mask = valid.copy()
    for c in conditions:
        mask &= c
    return dict(probability=float(np.mean(mask[valid])) if np.any(valid) else np.nan,
                valid=int(valid.sum()),
                explanation='Fraction of complete posterior curves' if analysis.source == 'model'
                            else 'Fraction of within-dose biological bootstrap curves')
