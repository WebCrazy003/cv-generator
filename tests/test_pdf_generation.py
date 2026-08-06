import tempfile
import unittest
from pathlib import Path

import app


class PdfGenerationTests(unittest.TestCase):
    def test_build_simple_pdf_creates_a_pdf_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "sample.pdf"
            lines = ["Acme Corp", "Summary with parentheses (test)"]

            app.build_simple_pdf(output_path, lines)

            self.assertTrue(output_path.exists())
            self.assertGreater(output_path.stat().st_size, 0)
            self.assertIn(b"%PDF", output_path.read_bytes())


if __name__ == "__main__":
    unittest.main()
