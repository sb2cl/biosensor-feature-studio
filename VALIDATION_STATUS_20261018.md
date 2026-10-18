# BioSensor Feature Studio v0.2.1 — validation status (18 October 2026)

This file records the result of a **PRIVATE** regression performed against archived FdeR and pLux MATLAB MAT/CSV datasets; those raw reference datasets must NOT be committed to the public repository. **The web application remains a research beta; full scientific validation has not yet been completed.**

## First cross-language regression (one Python seed)

- FdeR: five original experimental blocks; 1,000 bootstrap replicates with 0.07 SD jitter per dose.
- pLux: ten original experimental series; 20,000 primary nonparametric bootstrap replicates, no jitter.
- All 65 feature medians were within the predeclared **provisional 3% tolerance** (or 3 uM for FdeR EC50).
- All 65 reported CI95 upper and lower endpoints differed by <3% relative to the archived MATLAB endpoint in this run.
- pLux: all 40 deterministic primary-feature point values passed the stricter numerical precision check.
- Largest FdeR CI endpoint deviation: **1.53%**, R3R3 Exp3 Hill exponent upper endpoint.
- Largest pLux CI endpoint deviation: **0.52%**, B0030 High operational EC50 upper endpoint; this response is **nonresponsive**, so its numerical EC50 is not scientifically interpretable.

## v0.2.1 numerical correction

In R4R3 Exp1, v0.2 finite differences overestimated the upper Smax 95% endpoint (432.90 versus frozen MATLAB 319.15 MEFL/cell/uM) when Hill exponent n<1. The frozen MATLAB analytical derivative diverges at the zero-dose endpoint; its finite-CI summaries exclude these infinite values. Python v0.2.1 uses the same analytical derivative and finite-summary policy:

| Smax | MATLAB | Python v0.2.1 |
| --- | ---: | ---: |
| Median | 296.73 | 296.02 |
| CI2.5 | 277.99 | 278.57 |
| CI97.5 | 319.15 | 319.89 |

122/1,000 Python bootstrap draws have n<1 in this case; their Smax values are correctly nonfinite and excluded from finite Smax summaries **without excluding those draws from other feature summaries**. The archived MATLAB run used its own random bootstrap seed.

## Other changes

- `design_probability()` checks validity for the actually requested specifications, not unrequested EC50 values.
- The web's results table suppresses *primary* EC50 when QC is not `USABLE` (raw numerical values remain in audit exports with an explicit `Interpretable=false`).
- Public GitHub URL added to the header; engine's browser and offline copies remain byte-identical.
- 12 synthetic tests pass, including slope singularity, threshold conditioning, and embedded Python syntax; JavaScript syntax check also passes.

## Still required for a full JBE v1.0 statement

1. Three independent bootstrap seeds and Monte Carlo uncertainty of all reported interval endpoints.
2. Secondary pLux Hill estimator and its separate 3,000-replicate bootstrap.
3. Adversarial QC for *new, unannotated* experimental uploads, including near-flat and nonmonotone curves.
4. Whole-posterior model-curve testing and probabilities of meeting joint design specifications.
5. Browser-level E2E tests and offline-vs-Pyodide reproducibility on public GitHub Pages, including versions and source hashes.
6. Final repository license, tagged release and archived citation/DOI before manuscript submission.

The benchmark used original historical FdeR calibration results; it did NOT use the screened-dose VBMC posterior to rewrite the published baseline.
