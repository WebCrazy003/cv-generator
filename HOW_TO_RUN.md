# How to Run — CV Generator

A step-by-step guide to running the app locally and generating a CV.

---

## 1. Prerequisites

| Requirement | Why | Check |
|---|---|---|
| **Python 3.9+** | runs the server | `python3 --version` |
| **python-docx** | builds the DOCX | `python3 -c "import docx; print(docx.__version__)"` |
| **LibreOffice** | converts DOCX → styled PDF | `soffice --version` |

All three are already installed on this machine (Python 3.9.6, python-docx 1.2.0,
LibreOffice 26.2.5).

> LibreOffice is **optional**: without it the app still generates the DOCX and a plain-text
> PDF fallback (with a warning). For a styled PDF that matches the DOCX, keep it installed:
> `brew install --cask libreoffice`.

---

## 2. One-time setup

From the project folder (`cv-generator`):

```bash
pip install -r requirements.txt
```

Make sure **`cv_template.docx`** sits next to `app.py` — this is the fixed template whose
title, heading, text and bullet styles are reused. It's included in the repo.

---

## 3. Start the app

```bash
python3 app.py
```

You should see:

```
Server running on http://127.0.0.1:8000
```

Open **http://127.0.0.1:8000** in your browser.

To stop the server: press **Ctrl+C** in the terminal.

---

## 4. Generate a CV

1. **Paste JSON** CV data into the text area (a sample is pre-filled — see the shape below).
2. **Set the output base folder** — e.g. `/Users/minimac/Documents/CVs`. This is remembered
   for next time.
3. Click **Generate CV (DOCX + PDF)**.
4. The status line shows the exact paths of the created files.

### Where files go

```
<output base folder>/<yy_mm_dd>/<personNameOnCV>_<companyNameApplyJob>.pdf
<output base folder>/<yy_mm_dd>/<personNameOnCV>_<companyNameApplyJob>.docx
```

Example: base `/Users/minimac/Documents/CVs`, run on 2026-08-06, for Jane Doe applying to
Acme Corp →
`/Users/minimac/Documents/CVs/26_08_06/Jane Doe_Acme Corp.pdf`

---

## 5. JSON input shape

```json
{
  "personNameOnCV": "Jane Doe",
  "personLocation": "Berlin, Germany",
  "personEmail": "jane.doe@example.com",
  "personUniversity": "TU Berlin",
  "personDegree": "BSc Computer Science",
  "companyNameApplyJob": "Acme Corp",
  "summary": "One-paragraph professional summary.",
  "experience": [
    {
      "companyName": "SoftXPro",
      "jobTitle": "Senior ML Engineer",
      "startDate": "11/2023",
      "endDate": "07/2026",
      "content": ["First achievement bullet", "Second achievement bullet"]
    }
  ],
  "skills": [
    { "categoryName": "Programming Languages", "skillItems": ["Python", "SQL"] }
  ]
}
```

Notes:
- `personNameOnCV` becomes the CV title **and** part of the filename.
- `personLocation` + `personEmail` render on the contact line as `Location • Email`.
- `personUniversity` + `personDegree` render in the Education section as `University | Degree`.
- `companyNameApplyJob` is used only in the filename.
- `experience` and `skills` accept **any number** of entries; empty sections are skipped.

---

## 6. Run the tests (optional)

```bash
python3 -m pytest -q
```

Expected: `7 passed`.

---

## 7. Troubleshooting

| Symptom | Cause / Fix |
|---|---|
| `Address already in use` on start | An old server is still running. Free the port: `lsof -ti tcp:8000 \| xargs kill` then start again. |
| `Please provide an output base folder.` | The output-folder field is empty — fill it in before generating. |
| PDF looks plain / warning about "low-fidelity fallback" | LibreOffice isn't found. Install it: `brew install --cask libreoffice`. |
| `Template not found: cv_template.docx` | `cv_template.docx` must be in the project root next to `app.py`. |
| `Invalid request JSON` / `Invalid settings JSON` | The pasted JSON is malformed — check commas/quotes. |
