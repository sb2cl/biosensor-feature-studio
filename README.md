# BioSensor Feature Studio

**Version 1.0.0 - citable research software release.**

[![Zenodo DOI: v1.0.0](https://zenodo.org/badge/DOI/10.5281/zenodo.23461067.svg)](https://doi.org/10.5281/zenodo.23461067)

Public application: https://sb2cl.github.io/biosensor-feature-studio/  
Source: https://github.com/sb2cl/biosensor-feature-studio  
Developed at the Synthetic Biology and Biosystems Control Lab (SB2CL),
Institute ai2, Universitat Politècnica de València, Spain.

## What the software does

A browser-based, locally executing workflow for **normalized** genetic
biosensor dose-response input. Python (NumPy, pandas, SciPy) runs through
Pyodide; Plotly displays the results. No server endpoint accepts user-uploaded
scientific CSV data. The browser **does** contact external CDNs for the
Pyodide runtime and Plotly libraries; use appropriate network/privacy policy.

- Load calibrated per-dose biological replicate data (`source=experiment`) or
  sets of complete curves indexed by posterior draw (`source=model`).
- Estimate basal, primary/secondary dynamic range and EC50, Hill parameters
  and maximum Hill sensitivity with FdeR/pLux-specific estimator profiles.
- Resample replicates **within each dose** for experimental bootstrap or
  summarize **whole posterior curves** without disrupting dose correlations.
- Flag nonresponsive/suspect responses; keep calculated but scientifically
  noninterpretable parameters in provenance with `Interpretable=false`.
- Evaluate exploratory joint thresholds on basal, DR and EC50 over valid
  resampled or posterior curves; export summary CSV, curve CSV and JSON.

## Start using the web app

Open https://sb2cl.github.io/biosensor-feature-studio/ and select a synthetic
demo. To analyze data, download the templates in **01 / DATA**, replace the
synthetic rows, and upload a normalized CSV from your own computer.

Required columns: `system,series,dose,replicate,signal`. Optional:
`source` (`experiment` or `model`), `dose_unit`, `window`, `qc_annotation`,
and additional metadata. Use `FdeR` for inducer in **uM** and `pLux` for
inducer in **nM**; signals must already be normalized to **MEFL/cell**.
See [template guide](docs/data/CSV_TEMPLATE_GUIDE.md).

Each model `replicate` identifies one complete posterior curve with the same
dose grid as the other draws. The application does not generate ODE
trajectories or sample a calibrated parameter posterior internally.

## Reproduce tests locally

Python 3.11 or later is recommended for offline tests. From the root:

```bash
python -m pip install -r requirements-offline.txt
python -m pytest tests -q
node --check docs/app.js
```

`node` is needed for JavaScript syntax validation, not for running the app.
For a static local preview:

```bash
cd docs
python -m http.server 8000
```

Open http://localhost:8000/ with an internet connection for CDN assets.
GitHub Pages is configured to serve `main` / `docs`.

## Scientific scope and limitations

- **FdeR primary DR:** maximum minus minimum, over the observed dose grid.
  **FdeR primary EC50:** finite-range midpoint of a fitted Hill response.
- **pLux primary DR:** maximum minus explicit zero-dose basal.
  **pLux primary EC50:** monotone-envelope operational crossing.
- 95% intervals are descriptive bootstrap or supplied-posterior summaries,
  not experimental success guarantees. Posterior intervals exclude
  observational uncertainty unless contained in the supplied curves.
- The browser accepts already processed MEFL/cell values. It does **not**
  ingest raw fluorescence/time series, calibrate a plate reader, select time
  windows, integrate biological ODEs, fit a VBMC posterior, or propagate
  external RBS translation-factor uncertainty automatically.
- This is an independent Python implementation, not a certified bitwise or
  draw-by-draw reproduction of the archived FdeR/pLux MATLAB pipelines.
  The frozen analyses remain the source for quantitative paper PPCs and
  design maps. Cross-language regression and validation boundaries are
  documented in [validation status](VALIDATION_STATUS_v1_0_0.md).
- Response QC uses simple annotations and summary/shape diagnostics;
  passing an automated QC check is not proof of a valid biological response.

## License, attribution, and citation

**Code:** MIT. Copyright (c) 2026 Universitat Politècnica de València.
**Software authors:** Yadira Boada and Alejandro Vignoni, in that order.
ORCID and scholarly affiliations are in [CITATION.cff](CITATION.cff) and
[AUTHORS.md](AUTHORS.md).

The SB2CL and university names and logos do not imply trademark or
endorsement permission for reuse; see [brand notice](BRANDING_AND_ASSETS.md).
No actual experimental private measurements or MATLAB/posterior archives
are bundled in this public software distribution; the demo data are synthetic.

**Version 1.0.0 Zenodo DOI:** [10.5281/zenodo.23461067](https://doi.org/10.5281/zenodo.23461067).

**Recommended software citation:** Boada, Y., & Vignoni, A. (2026).
*BioSensor Feature Studio* (v1.0.0) [Computer software]. Zenodo.
https://doi.org/10.5281/zenodo.23461067

This DOI refers to the archived v1.0.0 snapshot; subsequent commits on
`main` (including citation-only changes) do not modify the immutable
`v1.0.0` release or its Zenodo archive. See the [release guide](RELEASE_ZENODO_GUIDE.md)
for how to cite a specific version.
