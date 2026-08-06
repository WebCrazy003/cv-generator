# CV Generator

A local web app that fills a styled DOCX CV template from JSON data and outputs a
matching DOCX and PDF.

## How it works

The bundled `cv_template.docx` is used as a **style carrier**. The generator harvests
one prototype paragraph per element type (name/title, contact, summary, section header,
job date, job title, bullet, skill line, education line), wipes the body, and rebuilds
the document from your JSON by cloning those prototypes — so the title, heading, text,
bullet-point styles and overall layout match the template exactly, with no leftover
placeholder tokens or sample content.

## Setup

```bash
pip install -r requirements.txt
```

### Optional: styled PDF output

PDF is produced by converting the generated DOCX with **LibreOffice**. If LibreOffice
is not installed, the app still works but falls back to a plain-text PDF and returns a
warning in the UI. For full-fidelity PDF:

```bash
brew install --cask libreoffice
```

(`docx2pdf` is not used — on macOS it requires Microsoft Word.)

## Run

```bash
python3 app.py
```

Then open http://127.0.0.1:8000 and:

1. Paste JSON CV data (see the default sample for the expected shape).
2. Set an **output base folder** (remembered across sessions).
3. Generate — outputs land in
   `<base>/<yy_mm_dd>/<personNameOnCV>_<companyNameApplyJob>.pdf` (and `.docx`).

The template is fixed (`cv_template.docx`, next to `app.py`); there is no template picker.

### JSON shape

```json
{
  "companyNameApplyJob": "Acme Corp",
  "personNameOnCV": "Jane Doe",
  "contact": "Berlin, Germany • jane.doe@example.com",
  "summary": "…",
  "experience": [
    {"companyName": "SoftXPro", "jobTitle": "Senior ML Engineer",
     "startDate": "11/2023", "endDate": "07/2026", "content": ["…"]}
  ],
  "skills": [{"categoryName": "Programming Languages", "skillItems": ["Python", "SQL"]}],
  "education": [{"institution": "TU Berlin", "degree": "BSc Computer Science"}]
}
```

## Tests

```bash
python3 -m pytest -q
```
