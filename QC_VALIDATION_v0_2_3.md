# BioSensor Feature Studio v0.2.3 — quality-control release note

## Verified browser case (v0.2.2)

User-supplied screenshots and exported files from the public Pages application
showed `B0030_High_SYNTHETIC` classified as `NONRESPONSIVE_HIGH` with Spearman
rho -0.070, primary operational EC50 suppressed and the design-specification
probability withheld (`null`). The raw numeric estimates were retained in
exports for audit.

## v0.2.3 correction

The exported v0.2.2 summary incorrectly marked secondary Hill EC50 and Hill
shape parameters as interpretable when the response was nonresponsive.

For any response with quality other than `USABLE`, v0.2.3 marks these as
`Interpretable=false`:

- `EC50_operational`
- `EC50_Hill_FdeR`
- `Hill_n`
- `Hill_K`
- `Smax_Hill`

The browser displays *Not interpretable* for these features. Both CSV and
JSON exports now include the same `Interpretable` field. Numerical estimates
remain in exports only for methodological audit.

Basal, maximum-minus-minimum range, positive excursion, Hill fit R2 and the
bound-diagnostic indicator remain numerically visible as descriptive or
quality-control values; they are not evidence of a valid inducible response.

The only Python-engine modification adds interpretation metadata after the
feature values and bootstrap intervals have been calculated. The estimators,
calibration, posterior and uncertainty algorithms are unchanged.

## Additional synthetic posterior-curve test

Upload `synthetic_posterior_joint_test.csv` to the web application, select
`pLux`, `POSTERIOR_JOINT_TEST_SYNTHETIC`, source `model`, and set the optional
specifications:

- `EC50 <= 120 nM`
- `Dynamic range >= 170 MEFL/cell`
- `Basal <= 25 MEFL/cell`

The three complete model draws have basal 10/20/30, positive DR 90/180/270,
and EC50 75 nM each. Exactly one complete draw meets all three conditions,
so the expected result is **33.3% of 3 posterior curves**.

No experimental or unpublished data are included in this release.

## Remaining validation scope

This hotfix has passed offline synthetic tests and JavaScript syntax checks.
Its full Pyodide execution on the deployed public site still requires a browser
smoke test. The complete software validation for the JBE manuscript must also
cover regression across multiple seeds, all secondary Hill estimators and
browser-vs-engine concordance under real data inputs.
