# BioSensor Feature Studio v1.0.0 - validation status

Validation is a **software functionality statement**, not an assertion of
numerical identity with MATLAB, prospective successful strain engineering,
or transferability of the biosensor digital twin.

## Evidence prior to release

- Public v0.2.5 browser run: synthetic FdeR curve, pLux B0030 High QC,
  and complete three-draw model-curve specifications were exercised by the
  research team. The posterior synthetic joint result was 1 of 3 = 33.3%.
- The v0.2.5 base was assembled from the previously tested v0.2.3 engine,
  v0.2.4 CSV templates, and v0.2.5 branding. v1.0.0 changes metadata,
  documentation and version labels, **not the scientific feature engine**.
- Offline automated synthetic suite and final bundle security/privacy
  audit results: see the separate pre-release validation log generated
  with this candidate.
- A **private, single-seed** MATLAB/Python comparison covers 5 FdeR and
  10 pLux series, 65 summary comparisons. The corrected audit document
  reports 65 medians and both sets of 65 CI endpoints within provisional
  3% limits or the FdeR EC50 absolute tolerance.

## Provenance caveat requiring explicit disclosure

One older exported comparison CSV available during packaging retains a
**pre-correction** R4R3 Exp1 Smax upper-CI discrepancy of about 35.6%.
An accompanying later v0.2.1 validation record documents an analytical
Hill derivative correction and a corrected upper endpoint 319.89 vs
MATLAB 319.15 (0.23% deviation). The private MATLAB reference inputs
needed to rerun the entire fixed regression are not part of this release
environment. Therefore, the 65/65 corrected CI claim is **documented
historically**, not independently reconfirmed by these public tests.

## Explicit release limitations

- No cross-language multiple-seed study is included in the public archive.
- Secondary pLux Hill estimates have not been fully matched to their
  separate 3,000-bootstrap historical protocol; treat as diagnostics.
- Automated QC on new, unannotated flat/nonmonotonic user curves is a
  screening heuristic; users must inspect experimental provenance.
- Public browser uses Pyodide v0.28.3 and the Plotly CDN, while the
  offline Python tests run under a different environment. Real remote
  Pyodide-vs-offline numerical identity is not certified by a static test.
- The software DOI archives software and synthetic examples, not
  unpublished FdeR/pLux MATLAB data, fitted models or research posterior.

## Conditions for JBE manuscript wording

It is accurate to call BioSensor Feature Studio a tested, publicly
accessible tool for uncertainty-aware analysis of processed curves, with
method-specific estimation, quality flags and exploratory constraint
checking. It is **not** accurate to call it an independently verified
full MATLAB-equivalent inference pipeline or a prospectively validated
strain-design predictor.
