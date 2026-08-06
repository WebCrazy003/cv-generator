# CV Generator — Implementation Status

## Status: ✅ Complete
The core generation engine has been rebuilt and the blocking template-compatibility
issue is resolved. Output DOCX matches the template's styling with no leftover
placeholder tokens and no sample content. All tests pass (`7 passed`). Committed on
`main` as `2ebb23a`.

One optional environment step remains (LibreOffice) for full-fidelity PDF — see below.

## What changed (this iteration)
The previous string-replace / zip-surgery engine was fundamentally broken for the
provided template (see [DISCOVERY_REPORT.md](DISCOVERY_REPORT.md) for the diagnosis):
tokens sat *before* hardcoded sample content and several were split across Word XML
runs, so replacement silently no-op'd and duplicated content.

It was replaced with a **`python-docx` prototype-clone builder** that reuses the
template as a *style carrier*:
- harvests one prototype paragraph per element type (name, contact, summary, section
  header, job date, job title, bullet, skill line, education line),
- wipes the document body,
- rebuilds from the JSON data by cloning those prototypes — preserving exact fonts,
  colors, list numbering and paragraph styles.

## Files
- [app.py](app.py) — `build_docx()` (prototype-clone engine), `convert_to_pdf()`
  (LibreOffice + text fallback), path-traversal guard, dated output folder.
- [frontend/app.js](frontend/app.js) — sample JSON with `name`/`contact`/`education`,
  PDF fallback warning surfaced, DOCX+PDF copy.
- [frontend/index.html](frontend/index.html) — UI shell (unchanged).
- [tests/test_docx_generation.py](tests/test_docx_generation.py) — asserts token-free
  output, injected content present, sample content dropped, styles preserved, single-entry handling.
- [tests/test_pdf_generation.py](tests/test_pdf_generation.py) — fallback PDF + `convert_to_pdf` coverage.
- [requirements.txt](requirements.txt) — `python-docx>=1.2`.
- [README.md](README.md) — setup, JSON shape, run/test instructions.
- [DISCOVERY_REPORT.md](DISCOVERY_REPORT.md) — codebase discovery + defect resolution log.

## Resolved from the previous "Known Remaining Work"
- ✅ Full template token coverage — tokens are no longer replaced individually; the
  document is rebuilt from prototypes, so `{{summary}}`, `{{Experience}}`, `{{Skills}}`,
  `{{Education}}`, `{{company1..N}}` are all handled regardless of run-splitting or count.
- ✅ Run-split tokens (`{{Experience}}`/`{{Skills}}`/`{{Education}}`) — no longer relevant.
- ✅ `{{Education}}` data path — `education` added to the JSON schema and rendered.
- ✅ Company slots no longer input-count-driven — any number of experience entries works.
- ✅ Layout fidelity — output preserves the template's styles/fonts/colors/bullets.
- ✅ Failing test removed/replaced with a passing suite.
- ✅ Hygiene: path-traversal guard, dated folder from `%y_%m_%d`, dead code removed,
  `.claude/settings.local.json` untracked.

## Remaining optional work
- **LibreOffice (environment):** not installed on this machine, so PDF currently uses
  the low-fidelity text fallback (a warning is surfaced in the UI). For a styled PDF
  matching the DOCX: `brew install --cask libreoffice`.
- **Nice-to-haves:** support for multiple template designs (only the `_Brazil` style
  structure is targeted); richer per-bullet formatting.

## How to run
```bash
pip install -r requirements.txt
python3 app.py
# open http://127.0.0.1:8000
```
Outputs land in `output/<yy_mm_dd>/<name>_<company>.docx` and `.pdf`.

## How to test
```bash
python3 -m pytest -q
```
