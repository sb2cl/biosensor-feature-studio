# Publish BioSensor Feature Studio v1.0.0 on GitHub + Zenodo

IMPORTANT: This file does not itself create a release or DOI.

## Before GitHub release

1. Confirm names/ORCIDs in `CITATION.cff`, UPV copyright in `LICENSE`,
   logo notice in `BRANDING_AND_ASSETS.md`, and no private datasets.
2. Copy the release candidate to the repository; commit/push via GitHub
   Desktop, and wait for the **Science and site checks** action to pass.
3. Open the public Pages app and verify the `Release v1.0.0` header, both
   downloadable CSV templates, and the FdeR/pLux demo calculations.
   Check the exported provenance string for version v1.0.0.
4. Connect your GitHub account to Zenodo, open
   https://zenodo.org/account/settings/github/, click **Sync now**, and
   enable `sb2cl/biosensor-feature-studio` **before** tagging the release.
   For an organization repo, Zenodo may need SB2CL OAuth app approval.

## Publish release

5. Go to GitHub repository > Releases > Draft a new release.
   Create tag **v1.0.0** at the tested commit, release title
   **BioSensor Feature Studio v1.0.0**. Paste the reviewed text from
   `RELEASE_NOTES_v1_0_0.md`. Do not mark it a prerelease if you intend a
   stable v1.0.0. Publish only once checks above have succeeded.
6. Open Zenodo's GitHub integration and confirm that it has created a
   published, publicly accessible software record for v1.0.0. Verify
   **both creators in correct order**, ORCID, license, archive version.
   Copy the **version-specific DOI**, not the concept DOI, to your JBE
   Code availability paragraph and Figure 1 source statement.
7. Do not edit the archived tag to insert the DOI: commit actual DOI badge
   or citation updates to a **new commit** on `main` (and to future
   releases as appropriate). Tag v1.0.0 remains the reproducible snapshot.

## Metadata precedence and DOI notes

This source includes `CITATION.cff` and deliberately no `.zenodo.json`.
If both files are present, Zenodo uses `.zenodo.json` and ignores the CFF.
GitHub integration cannot pre-reserve a DOI for a future GitHub release.

Official sources:
https://help.zenodo.org/docs/github/enable-repository/
https://help.zenodo.org/docs/github/describe-software/
https://help.zenodo.org/docs/github/archive-software/github-upload/
https://support.zenodo.org/help/en-gb/24-github-integration/73-can-i-pre-reserved-a-doi-before-a-github-release
