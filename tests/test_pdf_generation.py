import tempfile
import unittest
from pathlib import Path

import app

TEMPLATE = Path(__file__).resolve().parent.parent / "cv_template.docx"


class PdfGenerationTests(unittest.TestCase):
    def test_build_simple_pdf_creates_a_pdf_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "sample.pdf"
            lines = ["Acme Corp", "Summary with parentheses (test)"]

            app.build_simple_pdf(output_path, lines)

            self.assertTrue(output_path.exists())
            self.assertGreater(output_path.stat().st_size, 0)
            self.assertIn(b"%PDF", output_path.read_bytes())

    def test_convert_to_pdf_produces_pdf(self):
        """convert_to_pdf yields a %PDF file via LibreOffice or the fallback."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            docx_path = Path(tmp_dir) / "cv.docx"
            pdf_path = Path(tmp_dir) / "cv.pdf"
            data = {
                "personNameOnCV": "Jane Doe",
                "summary": "Engineer",
                "experience": [{"companyName": "SoftXPro", "jobTitle": "Eng",
                                "startDate": "2023", "endDate": "2026", "content": ["Did work"]}],
                "skills": [{"categoryName": "Lang", "skillItems": ["Python"]}],
                "education": [{"institution": "Uni", "degree": "BSc"}],
            }
            app.build_docx(TEMPLATE, data, docx_path)

            warning = app.convert_to_pdf(docx_path, pdf_path)

            self.assertTrue(pdf_path.exists())
            self.assertIn(b"%PDF", pdf_path.read_bytes())
            # When LibreOffice is unavailable a warning is returned; otherwise None.
            if app.find_soffice() is None:
                self.assertIsNotNone(warning)


if __name__ == "__main__":
    unittest.main()
