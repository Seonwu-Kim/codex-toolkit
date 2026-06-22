import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "generate-professional-pdf"
    / "scripts"
)
sys.path.insert(0, str(SCRIPT_DIR))

from render_document import (
    prepare_markdown_for_render,
    render_pdf,
    render_template,
    render_toc,
)


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

        self.assertEqual(5, template.count(font_stack))

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

    def test_prepares_mermaid_and_dot_fences_as_rendered_figures(self):
        rendered = []

        def fake_renderer(visual_type, source, output):
            rendered.append((visual_type, source.read_text(encoding="utf-8")))
            output.write_text("<svg viewBox='0 0 1 1'></svg>", encoding="utf-8")

        markdown_text = """# 문서

```mermaid
flowchart LR
  A --> B
```

```dot
digraph G { A -> B }
```
"""

        with self.subTest("visual fences"):
            prepared = prepare_markdown_for_render(
                markdown_text,
                Path("/tmp/source.md"),
                Path("/tmp/render-work"),
                visual_renderer=fake_renderer,
            )

        self.assertEqual(
            [("mermaid", "flowchart LR\n  A --> B"), ("graphviz", "digraph G { A -> B }")],
            rendered,
        )
        self.assertIn('<figure class="diagram diagram-mermaid">', prepared)
        self.assertIn('<figure class="diagram diagram-graphviz">', prepared)
        self.assertNotIn("```mermaid", prepared)
        self.assertNotIn("```dot", prepared)

    def test_prepares_latex_math_as_svg_figures(self):
        rendered = []

        def fake_math_renderer(expression, output, display):
            rendered.append((expression, display))
            output.write_text("<svg viewBox='0 0 1 1'></svg>", encoding="utf-8")

        prepared = prepare_markdown_for_render(
            "Inline $a+b$ and block:\n\n$$\nx^2\n$$\n",
            Path("/tmp/source.md"),
            Path("/tmp/render-work"),
            math_renderer=fake_math_renderer,
        )

        self.assertEqual([("x^2", True), ("a+b", False)], rendered)
        self.assertIn('class="math math-display"', prepared)
        self.assertIn('<span class="math math-inline">', prepared)
        self.assertNotIn('<figure class="math math-inline">', prepared)

    def test_latex_math_does_not_modify_code_fences(self):
        rendered = []

        def fake_math_renderer(expression, output, display):
            rendered.append((expression, display))
            output.write_text("<svg viewBox='0 0 1 1'></svg>", encoding="utf-8")

        markdown_text = '''```js
const formula = "$a$";
```

Real math $b$.
'''

        prepared = prepare_markdown_for_render(
            markdown_text,
            Path("/tmp/source.md"),
            Path("/tmp/render-work"),
            math_renderer=fake_math_renderer,
        )

        self.assertEqual([("b", False)], rendered)
        self.assertIn('const formula = "$a$";', prepared)

    def test_can_leave_latex_math_unprocessed_for_compatibility(self):
        prepared = prepare_markdown_for_render(
            "Price is $10 and math is $a+b$.",
            Path("/tmp/source.md"),
            Path("/tmp/render-work"),
            math_enabled=False,
        )

        self.assertEqual("Price is $10 and math is $a+b$.", prepared)

    def test_template_uses_named_pages_for_cover_toc_and_body(self):
        template_path = (
            Path(__file__).resolve().parents[1]
            / "skills"
            / "generate-professional-pdf"
            / "assets"
            / "professional-document.html"
        )
        template = template_path.read_text(encoding="utf-8")

        self.assertIn("@page cover", template)
        self.assertIn("@page toc", template)
        self.assertIn("@page body", template)
        self.assertIn("content: none;", template)
        self.assertIn("counter-reset: bodyPage 0;", template)
        self.assertIn("counter(bodyPage)", template)
        self.assertIn(".math-inline img", template)

    def test_python_requirements_include_optional_rendering_dependencies(self):
        requirements_path = (
            Path(__file__).resolve().parents[1]
            / "skills"
            / "generate-professional-pdf"
            / "requirements.txt"
        )
        requirements = requirements_path.read_text(encoding="utf-8")

        for package in ["Pygments", "matplotlib", "weasyprint", "pypdf"]:
            self.assertIn(package, requirements)

    def test_body_page_counter_restarts_after_cover_and_toc(self):
        template_path = (
            Path(__file__).resolve().parents[1]
            / "skills"
            / "generate-professional-pdf"
            / "assets"
            / "professional-document.html"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            markdown_path = root / "document.md"
            metadata_path = root / "metadata.json"
            output_path = root / "document.pdf"
            markdown_path.write_text(
                "# 제목\n\n## A\n\n본문\n\n"
                '<div style="page-break-before: always"></div>\n\n'
                "## B\n\n본문2\n",
                encoding="utf-8",
            )
            metadata_path.write_text(
                json.dumps(
                    {
                        "brand": "Brand",
                        "title": "Title",
                        "version": "v1",
                        "subtitle": "Subtitle",
                        "header": "Header",
                        "cover_fields": [],
                        "toc_enabled": True,
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            render_pdf(markdown_path, template_path, metadata_path, output_path)

            from pypdf import PdfReader

            pages = [
                " | ".join((page.extract_text() or "").splitlines())
                for page in PdfReader(str(output_path)).pages
            ]

        self.assertIn("- 1 -", pages[2])
        self.assertIn("- 2 -", pages[3])


if __name__ == "__main__":
    unittest.main()
