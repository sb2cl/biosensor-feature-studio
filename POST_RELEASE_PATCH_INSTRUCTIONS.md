# After publication: metadata-only update to GitHub main

The user-provided Zenodo DOI is https://doi.org/10.5281/zenodo.23461067.
The archived GitHub release/tag v1.0.0 must remain unchanged.

This optional metadata-only patch contains:
- `README.md`: public citation, fixed-version DOI badge and stable-release label.
- `CITATION.cff`: explicit version 1.0.0 Zenodo DOI.
- `tests/test_release_v1.py`: replaces the pre-DOI negative assertion with a check of the published DOI.

The patch DOES NOT include or modify `docs/app.js`, `docs/index.html`,
`docs/py/features.py` or `biosensor_studio/features.py`.

For Windows GitHub Desktop:
1. Confirm GitHub release v1.0.0 exists and is not a draft; confirm the
   Zenodo record metadata for the supplied DOI.
2. Unzip `BFS_v1_0_0_POST_RELEASE_METADATA_PATCH.zip`.
3. GitHub Desktop > Repository > Show in Explorer, and copy the 3 files
   over the existing repo, preserving `tests/` folder structure.
4. Commit to main: `Add Zenodo DOI to v1.0.0 citation metadata`.
5. Push origin, then confirm GitHub Actions is green and the README DOI badge
   points to the intended Zenodo record.

Do not edit, delete, move or re-create tag `v1.0.0`, and do not try to
change the already archived Zenodo snapshot to insert its own DOI.

Local check (post-patch): 39 pytest tests passed and JavaScript syntax
checked. The version DOI is user-provided; independent Zenodo landing-page
and remote release metadata verification could not be completed from here.
