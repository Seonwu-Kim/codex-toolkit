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

from render_document import render_template, render_toc


class RenderTemplateTest(unittest.TestCase):

    def test_template_prioritizes_platform_korean_fonts(self):
        template_path = (
            Path(__file__).resolve().parents[1]
            / "skills"
            / "generate-professional-pdf"
            / "assets"
            / "professional-document.html"
        )
        template = template_path.read_text(encoding="utf-8")
        font_stack = (
            '"Apple SD Gothic Neo", "Noto Sans CJK KR", "Noto Sans KR", '
            '"NanumGothic", "Malgun Gothic", sans-serif'
        )

        self.assertEqual(3, template.count(font_stack))

    def test_template_uses_korean_monospace_font_for_code(self):
        template_path = (
            Path(__file__).resolve().parents[1]
            / "skills"
            / "generate-professional-pdf"
            / "assets"
            / "professional-document.html"
        )
        template = template_path.read_text(encoding="utf-8")

        self.assertIn(
            'font-family: "D2Coding", "Noto Sans Mono CJK KR", '
            '"NanumGothicCoding", "Menlo", "Monaco", "Courier New", '
            "monospace;",
            template,
        )
        self.assertIn("font-variant-ligatures: none;", template)

    def test_renders_h2_table_of_contents_by_default(self):
        html_body = (
            '<h2 id="overview">1. 개요</h2>'
            '<p>본문</p>'
            '<h3 id="scope">1.1 범위</h3>'
            '<h2 id="result">2. 결과 &amp; 검증</h2>'
        )

        rendered = render_toc(html_body, {})

        self.assertIn('<section class="toc-page">', rendered)
        self.assertIn('href="#overview"', rendered)
        self.assertIn("1. 개요", rendered)
        self.assertIn('href="#result"', rendered)
        self.assertIn("2. 결과 &amp; 검증", rendered)
        self.assertNotIn('href="#scope"', rendered)

    def test_can_include_h3_table_of_contents_entries(self):
        html_body = (
            '<h2 id="overview">1. 개요</h2>'
            '<h3 id="scope">1.1 <code>API</code> 범위</h3>'
        )

        rendered = render_toc(html_body, {"toc_depth": 3})

        self.assertIn('class="toc-level-3"', rendered)
        self.assertIn('href="#scope"', rendered)
        self.assertIn("1.1 API 범위", rendered)

    def test_can_include_h1_chapters_above_restarted_h2_numbering(self):
        html_body = (
            '<h1 id="operator">Part I. 운영자 API</h1>'
            '<h2 id="competition">1. 대회</h2>'
            '<h1 id="worker">Part II. Worker API</h1>'
            '<h2 id="callback">1. Callback</h2>'
        )

        rendered = render_toc(
            html_body,
            {"toc_start_level": 1, "toc_depth": 2},
        )

        self.assertIn('class="toc toc-start-level-1"', rendered)
        self.assertIn('class="toc-level-1"', rendered)
        self.assertIn('href="#operator"', rendered)
        self.assertIn('href="#worker"', rendered)
        self.assertIn('href="#competition"', rendered)
        self.assertIn('href="#callback"', rendered)

    def test_omits_h1_chapters_by_default_for_backward_compatibility(self):
        html_body = (
            '<h1 id="document-title">문서 제목</h1>'
            '<h2 id="overview">1. 개요</h2>'
        )

        rendered = render_toc(html_body, {})

        self.assertNotIn('href="#document-title"', rendered)
        self.assertIn('href="#overview"', rendered)

    def test_can_disable_table_of_contents(self):
        rendered = render_toc(
            '<h2 id="overview">1. 개요</h2>',
            {"toc_enabled": False},
        )

        self.assertEqual("", rendered)

    def test_uses_existing_layout_defaults(self):
        template = (
            "{{body_font_size}}|{{body_line_height}}|"
            "{{table_font_size}}|{{table_page_break}}|"
            "{{cover_min_height}}|{{cover_padding_top}}|"
            "{{cover_title_size}}|{{cover_page_break}}|"
            "{{toc_page_break_before}}|{{content}}"
        )

        rendered = render_template(template, "<p>body</p>", {})

        self.assertEqual(
            "9.5pt|1.55|9pt|avoid|260mm|30mm|26pt|always|"
            "always|<p>body</p>",
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
