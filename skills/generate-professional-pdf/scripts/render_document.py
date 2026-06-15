#!/usr/bin/env python3
import argparse
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path


def escaped(value):
    return html.escape(str(value), quote=True)


class HeadingParser(HTMLParser):

    def __init__(self, min_level, max_level):
        super().__init__()
        self.min_level = min_level
        self.max_level = max_level
        self.headings = []
        self.active_heading = None

    def handle_starttag(self, tag, attrs):
        if tag not in {"h1", "h2", "h3"}:
            return
        level = int(tag[1])
        if level < self.min_level or level > self.max_level:
            return
        attributes = dict(attrs)
        heading_id = attributes.get("id")
        if heading_id:
            self.active_heading = {
                "level": level,
                "id": heading_id,
                "text": [],
            }

    def handle_data(self, data):
        if self.active_heading:
            self.active_heading["text"].append(data)

    def handle_endtag(self, tag):
        if not self.active_heading:
            return
        if tag != f"h{self.active_heading['level']}":
            return
        heading = self.active_heading
        heading["text"] = "".join(heading["text"]).strip()
        self.headings.append(heading)
        self.active_heading = None


def render_toc(html_body, metadata):
    if not metadata.get("toc_enabled", True):
        return ""

    start_level = max(1, min(int(metadata.get("toc_start_level", 2)), 3))
    depth = max(start_level, min(int(metadata.get("toc_depth", 2)), 3))
    parser = HeadingParser(start_level, depth)
    parser.feed(html_body)
    if not parser.headings:
        return ""

    items = "\n".join(
        '<li class="toc-level-{level}">'
        '<a href="#{heading_id}">{title}</a>'
        "</li>".format(
            level=heading["level"],
            heading_id=escaped(heading["id"]),
            title=escaped(heading["text"]),
        )
        for heading in parser.headings
    )
    return """
<section class="toc-page">
  <h1>{title}</h1>
  <nav class="toc toc-start-level-{start_level}">
    <ol>
      {items}
    </ol>
  </nav>
</section>
""".strip().format(
        title=escaped(metadata.get("toc_title", "목차")),
        items=items,
        start_level=start_level,
    )


def render_lines(lines):
    rendered = []
    for item in lines:
        if isinstance(item, dict):
            label = item.get("label")
            value = item.get("value", "")
            if label:
                rendered.append(f"{escaped(label)}: {escaped(value)}")
            else:
                rendered.append(escaped(value))
        else:
            rendered.append(escaped(item))
    return "<br>\n".join(rendered)


def render_cover_field(field):
    if "lines" in field:
        value = render_lines(field["lines"])
    else:
        value = escaped(field.get("value", ""))
    return (
        "<tr>"
        f"<td>{escaped(field.get('label', ''))}</td>"
        f"<td>{value}</td>"
        "</tr>"
    )


def render_cover_content(metadata):
    cover_rows = "\n".join(
        render_cover_field(field)
        for field in metadata.get("cover_fields", [])
    )
    revisions = metadata.get("revisions", [])
    revision_rows = "\n".join(
        "<tr>"
        f"<td>{escaped(item.get('version', ''))}</td>"
        f"<td>{escaped(item.get('date', ''))}</td>"
        f"<td>{escaped(item.get('author', ''))}</td>"
        f"<td>{escaped(item.get('description', ''))}</td>"
        "</tr>"
        for item in revisions
    )
    revision_content = ""
    if revisions:
        revision_content = f"""
<div class="revision-history">
  <h3>{escaped(metadata.get("revision_title", "문서 변경 이력"))}</h3>
  <table class="revision-table">
    <thead>
      <tr><th>버전</th><th>일자</th><th>작성자</th><th>변경 내용</th></tr>
    </thead>
    <tbody>{revision_rows}</tbody>
  </table>
</div>
""".strip()
    return f"""
<table class="cover-table">
  {cover_rows}
</table>
{revision_content}
""".strip()


def render_template(template, html_body, metadata):
    replacements = {
        "content": html_body,
        "brand": escaped(metadata.get("brand", "")),
        "title": escaped(metadata.get("title", "")),
        "version": escaped(metadata.get("version", "")),
        "subtitle": escaped(metadata.get("subtitle", "")),
        "header": escaped(metadata.get("header", "")),
        "cover_content": render_cover_content(metadata),
        "toc_content": metadata.get("toc_content", ""),
        "primary_color": escaped(metadata.get("primary_color", "#223f73")),
        "accent_color": escaped(metadata.get("accent_color", "#0b7f90")),
        "body_font_size": escaped(metadata.get("body_font_size", "9.5pt")),
        "body_line_height": escaped(metadata.get("body_line_height", "1.55")),
        "table_font_size": escaped(metadata.get("table_font_size", "9pt")),
        "table_page_break": escaped(
            metadata.get("table_page_break", "avoid")
        ),
        "cover_min_height": escaped(
            metadata.get("cover_min_height", "260mm")
        ),
        "cover_padding_top": escaped(
            metadata.get("cover_padding_top", "30mm")
        ),
        "cover_title_size": escaped(
            metadata.get("cover_title_size", "26pt")
        ),
        "cover_page_break": escaped(
            metadata.get("cover_page_break", "always")
        ),
        "toc_page_break_before": escaped(
            metadata.get("toc_page_break_before", "always")
        ),
        "toc_page_break_after": escaped(
            metadata.get("toc_page_break_after", "always")
        ),
        "section_page_break": escaped(
            metadata.get("section_page_break", "auto")
        ),
        "first_column_width": escaped(
            metadata.get("first_column_width", "auto")
        ),
        "first_column_background": escaped(
            metadata.get("first_column_background", "transparent")
        ),
        "first_column_font_weight": escaped(
            metadata.get("first_column_font_weight", "normal")
        ),
        "first_column_white_space": escaped(
            metadata.get("first_column_white_space", "normal")
        ),
    }
    rendered = template
    for key, value in replacements.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    unresolved = re.findall(r"\{\{[a-z_][a-z0-9_]*\}\}", rendered)
    if unresolved:
        raise ValueError(
            "HTML template contains unresolved placeholders: "
            + ", ".join(sorted(set(unresolved)))
        )
    return rendered


def render_pdf(markdown_path, template_path, metadata_path, output_path):
    try:
        import markdown
        from weasyprint import HTML
    except ImportError as error:
        raise RuntimeError(
            "Missing dependencies. Install markdown and weasyprint."
        ) from error

    markdown_path = Path(markdown_path)
    template_path = Path(template_path)
    metadata_path = Path(metadata_path)
    output_path = Path(output_path)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    html_body = markdown.markdown(
        markdown_path.read_text(encoding="utf-8"),
        extensions=["tables", "fenced_code", "toc", "sane_lists"],
    )
    metadata["toc_content"] = render_toc(html_body, metadata)
    rendered = render_template(
        template_path.read_text(encoding="utf-8"),
        html_body,
        metadata,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=rendered, base_url=str(template_path.parent)).write_pdf(output_path)
    return output_path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Render a styled professional PDF from Markdown."
    )
    parser.add_argument("--markdown", required=True, type=Path)
    parser.add_argument("--template", required=True, type=Path)
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = render_pdf(
        args.markdown,
        args.template,
        args.metadata,
        args.output,
    )
    print(f"Generated PDF: {result}")
