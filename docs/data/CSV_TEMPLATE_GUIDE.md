# CSV import templates for BioSensor Feature Studio

These two CSVs are **fictional examples**, not experimental observations or calibrated model results. Download either CSV using the links in **01 / DATA**, replace all demonstration rows with your own data and upload the modified CSV back through **Upload normalized CSV**.

## Required columns

| Column | Meaning |
| --- | --- |
| `system` | Exactly `FdeR` or `pLux` (case sensitive). |
| `series` | Your construct / experiment identifier. |
| `source` | `experiment` for per-well measurements or `model` for posterior curves. |
| `dose` | Inducer concentration as a finite, nonnegative number. |
| `replicate` | Experimental well / replicate ID, or full posterior-draw ID for `model`. |
| `signal` | **Already calibrated and preprocessed** fluorescence in MEFL/cell. |

Optional metadata: `dose_unit` (uM for FdeR, nM for pLux), `signal_unit`, `window`, `qc_annotation`, `origin`. For `qc_annotation`, leave empty unless you have independently established a QC label; do not use it to force an unwanted result.

Every construct must have an explicit 0-dose level and at least four dose levels. Keep concentration units consistent within a construct. Numeric `signal` values must be finite and nonnegative. The web interface **does not** transform instrument units, choose raw time windows, calibrate MEFL/cell or execute ODE models.

## Experimental CSV

Each row is one dose and one measured well / biological replicate after all preprocessing, such as a time-window mean. You can use repeated `replicate` labels across doses, but the current bootstrap independently resamples wells **within each dose**. The example contains fictional FdeR and pLux curves: remove irrelevant rows and replace all others.

## Posterior CSV

Each row is one dose within one **complete** posterior draw. **Preserve the same `replicate` identifier across all doses of each draw.** All posterior draws for a given series must have the same complete dose grid. The web computes feature distributions from these complete curves; it does not perform another bootstrap over doses or add observation noise.

The pLux example `POSTERIOR_JOINT_TEST_SYNTHETIC` contains three draws. With EC50 <= 120 nM, positive DR >= 170 MEFL/cell and basal <= 25 MEFL/cell, exactly **1/3 = 33.3%** of draws should satisfy all conditions jointly. This is a software test only, not a biological claim.

**Confidentiality:** Uploaded CSV files are read by the browser client. Only synthetic template content belongs in the public GitHub repository. Never commit unpublished measurements or fitted posterior samples to this public repo.
