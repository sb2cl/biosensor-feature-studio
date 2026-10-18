# BioSensor Feature Studio v1.0.0 - local release-candidate verification

**Prepared:** 2026-10-19. **Not a published GitHub release or a Zenodo DOI.**

## Results run on this build

- Automated tests: **39 passed** (`python -m pytest -q tests`).
- JavaScript syntax: **passed** (`node --check docs/app.js`).
- Python compilation: feature files syntactically valid.
- `CITATION.cff` parsed as valid YAML with first creator Yadira Boada and second creator Alejandro Vignoni; semantic CFF schema validation in Zenodo remains pending.
- Both browser `docs/py/features.py` and offline `biosensor_studio/features.py` are **byte-identical** with SHA-256 `aabde7ff6a23c7826e76ec23971d9457b086e53695b047cd1bbaca17651e42a5` (same as v0.2.5).
- Synthetic function tests: FdeR and pLux extraction, interpretability flags, complete model posterior curves and **1/3 = 33.3%** joint feasibility, fixed-seed exact repeatability, three distinct FdeR seeds, weak flat/nonmonotonic QC, import templates, URL version parity, and absence of private MAT/HDF5 in package.
- Browser Pyodide runtime is pinned to v0.28.3; local tests are **not** a remote browser rerun of GitHub Pages v1.0.0.

## Tested offline Python environment

- Python 3.13.5
- NumPy 2.3.5; pandas 2.2.3; SciPy 1.17.0
- h5py 3.15.1; pytest 9.0.2
- JavaScript syntax checked by Node.js installed in this environment.

## Validation boundaries

- This is a release-candidate software QA check and uses **synthetic data only**.
- Earlier research-team browser screenshots/exports validate deployed v0.2.5 behavior, not the yet-to-be-deployed v1.0.0 branding/version label.
- A private 65-feature MATLAB-Python benchmark is documented separately. The historical pre-correction CSV has one R4R3 Exp1 Smax upper endpoint outlier (35.6% difference). A corrected numerical audit reports 319.89 Python vs 319.15 MATLAB, but its underlying private MATLAB inputs are not present here for an independent rerun. Do **not** call the present local suite proof of 65/65 verified MATLAB parity.
- Scientific method and PPC claims must continue to refer to the frozen external MATLAB FdeR/pLux analyses.

## Archival scope

The v1.0.0 release snapshot should contain only the public web app, offline helpers, synthetic demos, templates, tests, metadata, and documentation. Real experimental MAT/CSV, private posterior draws, and frozen PPC data are not contained in this archive.
