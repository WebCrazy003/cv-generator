import tempfile
from pathlib import Path

from docx import Document

import app

TEMPLATE = Path(__file__).resolve().parent.parent / "Robson Oliveira_Brazil.docx"

SAMPLE_DATA = {
    "companyNameApplyJob": "Acme Corp",
    "name": "Jane Doe",
    "contact": "Berlin, Germany • jane.doe@example.com",
    "summary": "Senior engineer with a focus on ML platforms.",
    "experience": [
        {
            "companyName": "SoftXPro",
            "jobTitle": "Senior ML Engineer",
            "startDate": "11/2023",
            "endDate": "07/2026",
            "content": ["Built LLM applications", "Shipped inference services"],
        },
        {
            "companyName": "STS Software",
            "jobTitle": "Backend Engineer",
            "startDate": "01/2020",
            "endDate": "10/2023",
            "content": ["Distributed backend services"],
        },
    ],
    "skills": [
        {"categoryName": "Programming Languages", "skillItems": ["Python", "SQL"]},
        {"categoryName": "MLOps", "skillItems": ["Docker", "Kubernetes"]},
    ],
    "education": [
        {"institution": "TU Berlin", "degree": "BSc Computer Science"},
    ],
}


def _generate():
    tmp_dir = tempfile.mkdtemp()
    output = Path(tmp_dir) / "out.docx"
    app.build_docx(TEMPLATE, SAMPLE_DATA, output)
    text = "\n".join(p.text for p in Document(str(output)).paragraphs)
    return output, text


def test_output_has_no_leftover_tokens():
    _, text = _generate()
    assert "{{" not in text and "}}" not in text


def test_output_contains_injected_content():
    _, text = _generate()
    for expected in ["Jane Doe", "SoftXPro", "Backend Engineer", "TU Berlin",
                     "Programming Languages: Python, SQL"]:
        assert expected in text, expected


def test_output_drops_original_sample_content():
    _, text = _generate()
    for sample in ["Robson", "SDLC Corp", "Pitágoras"]:
        assert sample not in text, sample


def test_section_styles_preserved():
    output, _ = _generate()
    from docx.oxml.ns import qn

    header_styles = []
    for paragraph in Document(str(output)).paragraphs:
        ppr = paragraph._p.find(qn("w:pPr"))
        if ppr is None:
            continue
        pstyle = ppr.find(qn("w:pStyle"))
        if pstyle is not None and pstyle.get(qn("w:val")) == "2":
            header_styles.append(paragraph.text)
    assert header_styles == ["Experience", "Skills", "Education"]


def test_handles_single_experience_entry():
    data = dict(SAMPLE_DATA)
    data["experience"] = [SAMPLE_DATA["experience"][0]]
    tmp_dir = tempfile.mkdtemp()
    output = Path(tmp_dir) / "single.docx"
    app.build_docx(TEMPLATE, data, output)
    text = "\n".join(p.text for p in Document(str(output)).paragraphs)
    assert "STS Software" not in text
    assert "SoftXPro" in text
