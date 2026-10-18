# BioSensor Feature Studio — GitHub Pages edition (v0.2.3 research beta)

Interactive, scientific dose–response characterization with **Python (NumPy/pandas/SciPy) running in the visitor's browser** via Pyodide/WebAssembly. The `docs/` directory can be hosted directly on GitHub Pages with no server-side Python and no authentication for visitors.

## Deploy on GitHub Pages (branch based)

1. Create a new GitHub repository, e.g. `biosensor-feature-studio` (public for public Pages hosting).
2. Upload **the contents of this ZIP** to the repository root. Keep `docs/` as a subfolder.
3. Open **Settings → Pages → Build and deployment**. Under **Source**, select **Deploy from a branch**; select **main** and **/docs**, then **Save**.
4. GitHub will provide a public link resembling `https://YOUR-ACCOUNT.github.io/biosensor-feature-studio/`. Allow a few minutes for publishing.
5. Open the page. On first load, the Pyodide runtime and Python scientific packages will download; subsequent loads may benefit from browser caching.

Do not create the URL in the paper until it has been published and verified. The 'GitHub repository' header link in `docs/index.html` defaults to GitHub's home page; replace it with the actual repository URL before release.

## What is dynamic?

- Users import dose-replicate CSVs **locally** without an application server.
- Select a biosensor system (`FdeR`, `pLux`) and construct/experiment.
- Calculate basal, total/positive dynamic ranges, FdeR's finite-range Hill EC50, pLux's monotone-envelope operational EC50, descriptive Hill parameters and Smax.
- Inspect response curves and bootstrap uncertainty intervals, view interpretation warnings, evaluate joint design thresholds, download summary/curves/provenance.
- Model-posterior inputs are accepted as **whole curves per draw** (consistent `replicate` ID across all doses).

The site ships **synthetic demonstration data only**. Upload your own normalized CSV to analyze unpublished data in the browser. No server receives uploaded data from this app. The browser *does* download scientific runtime and plotting libraries from external CDNs.

## Import schema

Required CSV columns: `system,series,dose,replicate,signal`. Optional: `source` (`experiment` default, or `model`), `dose_unit`, `window`, `qc_annotation`. The synthetic demo at `docs/data/synthetic_demo.csv` provides a template. Every series must include 0-dose and at least 4 dose levels, with consistent dose units. Signals should be normalized as appropriate **before** importing; this browser edition does not run raw instrument calibration or select time-series windows.

For archived MATLAB datasets, use the offline v0.1 converter or `prepare_data.py` with dependencies from `requirements-offline.txt`. **Do not put the original experimental MAT files in a public GitHub repository.** The converter is an offline helper, not part of the public browser application.

## Scientific scope and limitations

- FdeR primary descriptors: DR = maximum-minus-minimum; EC50 from fitted Hill response over finite observed dose range. Bootstrap with 0.07 SD jitter by default.
- pLux primary descriptors: DR = maximum-minus-zero-dose; EC50 from monotone-envelope crossing. Default bootstrap jitter 0.
- The Python optimizer, bootstrap randomness and numerical bounds are not identical to MATLAB's historical frozen pipeline. **The site is a functional research beta, not a numerical replacement for the final VBMC/PPC results** until cross-language regression testing is complete.
- `NONRESPONSIVE_HIGH` suppresses EC50 interpretation, even if a numerical crossing can be computed.
- Joint threshold frequencies are exploratory fractions over bootstrap samples or user-provided complete posterior curves; not clinically or experimentally validated success probabilities.
- No ODE integration, VBMC fitting, independent q_RBS uncertainty propagation or raw MAT parsing in the public browser v0.2.3 release.
- Source code and synthetic data can be public; keep unpublished original replicates and any private data out of the repository.

## Local preview

Serve the `docs` folder with a static server (rather than opening HTML from disk):

```bash
cd docs
python -m http.server 8000
```

Open `http://localhost:8000/`. **Internet access is required for the CDN scientific runtime on first load.**

## Files

- `docs/index.html`, `docs/styles.css`, `docs/app.js`: client-side UI.
- `docs/py/features.py`: same feature-analysis engine as Studio v0.1.
- `docs/data/synthetic_demo.csv`: synthetic, nonexperimental test data.
- `biosensor_studio`, `prepare_data.py`, `requirements-offline.txt`: optional Python tools outside public Pages path.

Before manuscript release: pin/check dependency versions, regression-test against frozen MATLAB numerical outputs, introduce a proper license, DOI/release/archive, and scientific citation/version metadata. All features are intentionally described as research-beta capabilities until tested.

## v0.2.2 scientific validation hotfix (18 October 2026)

- Replaces numerical `np.gradient` for Hill maximum sensitivity with the analytical derivative. For `n < 1`, the slope at 0 diverges; nonfinite Smax samples are excluded from Smax finite quantiles (as in frozen MATLAB `biosensorStats4.m`), and their count is reported. Other bootstrap features retain those same draws.
- Applies design feasibility validity only to characteristics actually constrained; basal-only/DR-only criteria no longer require a valid EC50.
- Suppresses non-interpretable primary EC50 numbers from summary tables when response QC is not `USABLE`; exported rows retain numerical calculations for audit with an explicit `Interpretable` status.
- Points the page header to the SB2CL repository.

A private baseline comparison (five FdeR blocks and ten pLux series, 65 feature summaries) is being used for validation. The reference MAT files and comparison reports are NOT bundled with the public site. This hotfix does NOT certify the complete web platform or secondary Hill/pLux bootstrap equivalence.


## v0.2.2 deployment hotfix

Restores the pinned Pyodide CDN runtime version v0.28.3 used by v0.2. A v0.2.1 string substitution accidentally changed the runtime reference to a nonexistent version (v0.2.18.3), preventing the browser engine from starting. No scientific algorithms changed.

## v0.2.3 quality-interpretability hotfix (18 October 2026)

On flagged nonresponsive or review curves, both operational and Hill EC50s,
Hill parameters and derived Hill maximum sensitivity are not biologically
interpretable. The interface suppresses these response-dependent estimates.
Exports retain raw algorithmic numbers for audit, but carry
`Interpretable=false` in CSV **and** provenance JSON. Basal, total range,
positive excursion and fit-quality statistics remain available as
descriptive or diagnostic quantities, not design validation.
No estimator, bootstrap, numerical result or posterior was modified.

For v0.2.3 browser QC checks and the three-draw synthetic posterior test,
see `QC_VALIDATION_v0_2_3.md`.
