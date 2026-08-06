import os
import zipfile
from pathlib import Path

from app import build_replacement_map


def test_placeholder_map_contains_expected_tokens():
    payload = {
        "data": {
            "companyNameApplyJob": "Janea Systems",
            "summary": "Senior engineer",
            "experience": [
                {"companyName": "SoftXPro", "jobTitle": "Senior ML Engineer", "startDate": "11/2023", "endDate": "07/2026", "content": ["Built AI systems"]}
            ],
            "skills": [{"categoryName": "Python", "skillItems": ["FastAPI", "pytest"]}],
        }
    }
    replacements = build_replacement_map(payload)
    assert "{{summary}}" in replacements
    assert "{{Experience}}" in replacements
    assert "{{Skills}}" in replacements
    assert "{{company1}}" in replacements
    assert "{{company2}}" in replacements
