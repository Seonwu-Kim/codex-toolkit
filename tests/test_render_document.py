import sys
import unittest
from pathlib import Path


SCRIPT_DIR = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "generate-professional-pdf"
    / "scripts"
)
sys.path.insert(0, str(SCRIPT_DIR))

from render_document import render_template


class RenderTemplateTest(unittest.TestCase):

    def test_uses_existing_layout_defaults(self):
        template = (
            "{{body_font_size}}|{{body_line_height}}|"
            "{{table_font_size}}|{{table_page_break}}|"
            "{{cover_min_height}}|{{cover_padding_top}}|"
            "{{cover_title_size}}|{{cover_page_break}}|{{content}}"
        )

        rendered = render_template(template, "<p>body</p>", {})

        self.assertEqual(
            "9.5pt|1.55|9pt|avoid|260mm|30mm|26pt|always|<p>body</p>",
            rendered,
        )

    def test_applies_dense_and_compact_layout_metadata(self):
        template = (
            "{{body_font_size}}|{{body_line_height}}|"
            "{{table_font_size}}|{{table_page_break}}|"
            "{{cover_min_height}}|{{cover_padding_top}}|"
            "{{cover_title_size}}|{{cover_page_break}}"
        )
        metadata = {
            "body_font_size": "8.8pt",
            "body_line_height": "1.42",
            "table_font_size": "8pt",
            "table_page_break": "auto",
            "cover_min_height": "95mm",
            "cover_padding_top": "10mm",
            "cover_title_size": "22pt",
            "cover_page_break": "auto",
        }

        rendered = render_template(template, "", metadata)

        self.assertEqual(
            "8.8pt|1.42|8pt|auto|95mm|10mm|22pt|auto",
            rendered,
        )


if __name__ == "__main__":
    unittest.main()
