import json
import mimetypes
import os
import re
import shutil
import tempfile
import zipfile
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from xml.sax.saxutils import escape

ROOT_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT_DIR / "frontend"
SETTINGS_FILE = ROOT_DIR / "settings.json"
OUTPUT_ROOT = ROOT_DIR / "output"


def load_settings():
    if SETTINGS_FILE.exists():
        try:
            return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"templates": [], "activeTemplate": "", "outputDirectory": str(OUTPUT_ROOT)}
    return {"templates": [], "activeTemplate": "", "outputDirectory": str(OUTPUT_ROOT)}


def save_settings(settings):
    SETTINGS_FILE.write_text(json.dumps(settings, indent=2), encoding="utf-8")
    return settings


def sanitize_name(value):
    value = re.sub(r"[^A-Za-z0-9._ -]+", "_", str(value).strip())
    value = re.sub(r"\s+", " ", value).strip()
    return value or "cv"


def build_experience_text(experience_items):
    if not experience_items:
        return "No experience information provided."

    blocks = []
    for item in experience_items:
        company = item.get("companyName", "")
        title = item.get("jobTitle", "")
        start_date = item.get("startDate", "")
        end_date = item.get("endDate", "")
        content = item.get("content") or []
        header = f"{company} | {title} | {start_date} - {end_date}".strip()
        blocks.append(header)
        for bullet in content:
            blocks.append(f"- {bullet}")
        blocks.append("")
    return "\n".join(blocks).strip()


def build_skills_text(skills):
    if not skills:
        return "No skills information provided."

    blocks = []
    for item in skills:
        category = item.get("categoryName", "")
        entries = item.get("skillItems") or []
        if category and entries:
            blocks.append(f"{category}: {', '.join(entries)}")
        elif category:
            blocks.append(category)
    return "\n".join(blocks).strip()


def build_replacement_map(payload):
    data = payload.get("data", {})
    company_name = data.get("companyNameApplyJob") or "cv"
    summary = data.get("summary") or ""
    experience_items = data.get("experience") or []
    skills_items = data.get("skills") or []
    experience_text = build_experience_text(experience_items)
    skills_text = build_skills_text(skills_items)

    replacements = {
        "{{companyNameApplyJob}}": company_name,
        "[[companyNameApplyJob]]": company_name,
        "{{CompanyNameApplyJob}}": company_name,
        "{{summary}}": summary,
        "[[summary]]": summary,
        "{{Summary}}": summary,
        "{{experience}}": experience_text,
        "[[experience]]": experience_text,
        "{{Experience}}": experience_text,
        "{{skills}}": skills_text,
        "[[skills]]": skills_text,
        "{{Skills}}": skills_text,
    }

    for index, item in enumerate(experience_items, start=1):
        company_name_value = item.get("companyName", "")
        job_title_value = item.get("jobTitle", "")
        content_value = "\n".join(item.get("content") or [])
        replacements[f"{{{{company{index}}}}}"] = company_name_value
        replacements[f"{{{{company{index}Name}}}}"] = company_name_value
        replacements[f"{{{{jobTitle{index}}}}}"] = job_title_value
        replacements[f"{{{{content{index}}}}}"] = content_value
        replacements[f"{{{{company{index}Details}}}}"] = f"{company_name_value} - {job_title_value}".strip(" -")
        replacements[f"{{{{Company{index}}}}}"] = company_name_value
        replacements[f"{{{{Company{index}Name}}}}"] = company_name_value
        replacements[f"{{{{JobTitle{index}}}}}"] = job_title_value
        replacements[f"{{{{Content{index}}}}}"] = content_value

    return replacements


def replace_placeholders(xml_text, replacements):
    updated_text = xml_text
    for token, value in replacements.items():
        updated_text = updated_text.replace(token, escape(str(value)))
    return updated_text


def generate_docx(template_path, payload, output_path):
    replacements = build_replacement_map(payload)
    template_path = Path(template_path).expanduser()
    output_path = Path(output_path).expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not template_path.exists():
        raise FileNotFoundError(f"Template path does not exist: {template_path}")

    with zipfile.ZipFile(template_path, "r") as source_zip:
        temp_dir = Path(tempfile.mkdtemp(prefix="cv-template-", dir=str(ROOT_DIR / "tmp")))
        try:
            for item in source_zip.infolist():
                target_path = temp_dir / item.filename
                if item.is_dir():
                    target_path.mkdir(parents=True, exist_ok=True)
                    continue

                try:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                except FileExistsError:
                    pass

                data = source_zip.read(item.filename)
                if item.filename.endswith(".xml") and item.filename.startswith("word/"):
                    text = data.decode("utf-8", errors="ignore")
                    updated = replace_placeholders(text, replacements)
                    target_path.write_text(updated, encoding="utf-8")
                else:
                    target_path.write_bytes(data)
            with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as out_zip:
                for file_path in temp_dir.rglob("*"):
                    if file_path.is_file():
                        out_zip.write(file_path, file_path.relative_to(temp_dir).as_posix())
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


def build_simple_pdf(path, lines):
    text = "\n".join(lines) if lines else ""
    escaped_text = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    content_stream = "BT\n/F1 11 Tf\n72 760 Td\n"
    for line in lines:
        escaped_line = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        content_stream += "(" + escaped_line + ") Tj\n0 -14 Td\n"
    content_stream += "ET"

    content_bytes = content_stream.encode("latin-1", "replace")
    font_obj = b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
    content_obj = b"4 0 obj\n<< /Length " + str(len(content_bytes)).encode("ascii") + b" >>\nstream\n" + content_bytes + b"\nendstream\nendobj\n"
    page_obj = b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
    pages_obj = b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
    catalog_obj = b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    objects = [catalog_obj, pages_obj, page_obj, content_obj, font_obj]

    pdf_bytes = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf_bytes))
        pdf_bytes.extend(obj)
    xref_offset = len(pdf_bytes)
    pdf_bytes.extend(f"xref\n0 {len(objects)+1}\n".encode("ascii"))
    pdf_bytes.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf_bytes.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf_bytes.extend(f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii"))
    Path(path).write_bytes(pdf_bytes)


class CvGeneratorHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            self._send_json({"status": "ok"})
            return
        if parsed.path == "/api/settings":
            self._send_json(load_settings())
            return

        target_path = FRONTEND_DIR / parsed.path.lstrip("/")
        if parsed.path in {"/", "/index.html"}:
            target_path = FRONTEND_DIR / "index.html"
        if target_path.exists() and target_path.is_file():
            self.send_response(200)
            self.send_header("Content-Type", mimetypes.guess_type(str(target_path))[0] or "application/octet-stream")
            self.send_header("Content-Length", str(target_path.stat().st_size))
            self.end_headers()
            self.wfile.write(target_path.read_bytes())
            return
        self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length).decode("utf-8") if content_length else ""

        if parsed.path == "/api/settings":
            try:
                settings = json.loads(body or "{}")
            except json.JSONDecodeError as exc:
                self._send_json({"error": f"Invalid settings JSON: {exc}"}, 400)
                return
            save_settings(settings)
            self._send_json({"status": "saved", "settings": settings})
            return

        if parsed.path == "/api/generate-cv":
            try:
                payload = json.loads(body or "{}")
            except json.JSONDecodeError as exc:
                self._send_json({"error": f"Invalid request JSON: {exc}"}, 400)
                return

            try:
                json_content = payload.get("jsonContent")
                if not json_content:
                    raise ValueError("The JSON content is empty.")
                data = json.loads(json_content)
                template_path = payload.get("templatePath")
                output_directory = payload.get("outputDirectory") or str(OUTPUT_ROOT)
                if not template_path:
                    raise ValueError("Please select an active DOCX template path.")
                template_path = Path(template_path).expanduser()
                if not template_path.exists():
                    raise ValueError(f"Template path does not exist: {template_path}")
                if not template_path.suffix.lower() == ".docx":
                    raise ValueError("The selected template must be a .docx file.")

                output_directory_path = Path(output_directory).expanduser()
                output_directory_path.mkdir(parents=True, exist_ok=True)
                today = datetime.now()
                output_folder = output_directory_path / f"26_{today:%m}_{today:%d}"
                output_folder.mkdir(parents=True, exist_ok=True)

                company_name = sanitize_name(data.get("companyNameApplyJob") or "cv")
                person_name = sanitize_name(template_path.stem)
                pdf_path = output_folder / f"{person_name}_{company_name}.pdf"
                docx_path = output_folder / f"{person_name}_{company_name}.docx"

                generate_docx(template_path, {"data": data}, docx_path)

                pdf_lines = [
                    f"Company: {data.get('companyNameApplyJob') or 'N/A'}",
                    "",
                    f"Summary: {data.get('summary') or 'N/A'}",
                    "",
                    "Experience:",
                ]
                for item in data.get("experience") or []:
                    pdf_lines.append(f"- {item.get('companyName') or 'N/A'} | {item.get('jobTitle') or 'N/A'}")
                    for bullet in item.get("content") or []:
                        pdf_lines.append(f"  • {bullet}")
                pdf_lines.append("")
                pdf_lines.append("Skills:")
                for item in data.get("skills") or []:
                    pdf_lines.append(f"- {item.get('categoryName') or 'N/A'}: {', '.join(item.get('skillItems') or [])}")

                build_simple_pdf(pdf_path, pdf_lines)
                self._send_json({"status": "success", "pdfPath": str(pdf_path), "docxPath": str(docx_path)})
            except Exception as exc:  # pragma: no cover - surfaced to UI
                self._send_json({"error": str(exc)}, 500)
                return

        self._send_json({"error": "Not found"}, 404)


def main():
    os.makedirs(ROOT_DIR / "tmp", exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 8000), CvGeneratorHandler)
    print("Server running on http://127.0.0.1:8000")
    server.serve_forever()


if __name__ == "__main__":
    main()
