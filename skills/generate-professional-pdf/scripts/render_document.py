#!/usr/bin/env python3
import argparse
import html
import json
import re
from pathlib import Path


def escaped(value):
    return html.escape(str(value), quote=True)


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
        "primary_color": escaped(metadata.get("primary_color", "#223f73")),
        "accent_color": escaped(metadata.get("accent_color", "#0b7f90")),
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
