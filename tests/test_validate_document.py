import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT_DIR = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "generate-professional-pdf"
    / "scripts"
)
sys.path.insert(0, str(SCRIPT_DIR))

from validate_document import validate_pdf


class ValidateDocumentTest(unittest.TestCase):

    def test_uses_source_markdown_for_occurrence_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profile = root / "profile.json"
            source = root / "source.md"
            profile.write_text(
                json.dumps(
                    {
                        "expected_occurrences": {"결론": 1},
                        "report_occurrences": ["결론"],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            source.write_text("## 결론\n본문\n", encoding="utf-8")

            with (
                patch(
                    "validate_document.extract_pdf",
                    return_value=["목차 결론 2", "결론 본문"],
                ),
                patch(
                    "validate_document.render_and_scan",
                    return_value={
                        "rendered_pages": 2,
                        "blank_like_pages": [],
                        "edge_dense_pages": [],
                    },
                ),
            ):
                result = validate_pdf(
                    root / "document.pdf",
                    profile,
                    root / "rendered",
                    source_path=source,
                )

        self.assertEqual([], result["errors"])
        self.assertEqual({"결론": 1}, result["occurrences"])


if __name__ == "__main__":
    unittest.main()
