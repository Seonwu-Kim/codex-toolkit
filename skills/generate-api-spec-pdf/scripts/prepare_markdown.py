#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


HTTP_METHOD_PATTERN = re.compile(r"\b(GET|POST|PUT|PATCH|DELETE)\b")
REQUIRED_ITEMS = (
    "Method / Path",
    "설명",
    "Path Parameter",
    "Query Parameter",
    "Request Body",
    "Response Body",
    "Status Code",
)


def common_section(document, marker=None):
    if marker is None:
        return document.rstrip()
    if marker not in document:
        raise ValueError(f"Main document does not contain '{marker}'.")
    return document.split(marker, 1)[0].rstrip()


def detail_sections(document, path):
    match = re.search(r"^## \d+\. ", document, flags=re.MULTILINE)
    if match is None:
        raise ValueError(f"{path} does not contain a numbered detail section.")
    return document[match.start() :].strip()


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Invalid JSON example: duplicate key '{key}'")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"Invalid JSON example: unsupported constant {value}")


def prettify_json(value):
    try:
        parsed = json.loads(
            value,
            object_pairs_hook=reject_duplicate_keys,
            parse_constant=reject_constant,
        )
    except json.JSONDecodeError as error:
        raise ValueError(
            "Invalid JSON example at "
            f"line {error.lineno}, column {error.colno}: {error.msg}"
        ) from error
    return json.dumps(
        parsed,
        indent=2,
        ensure_ascii=False,
        allow_nan=False,
    )


def extract_table(section_text):
    lines = section_text.splitlines()
    header_index = next(
        (
            index
            for index, line in enumerate(lines)
            if line.strip() == "| 항목 | 내용 |"
        ),
        None,
    )
    if header_index is None or header_index + 1 >= len(lines):
        return {}, section_text

    table_end = header_index + 2
    while table_end < len(lines) and lines[table_end].lstrip().startswith("|"):
        table_end += 1

    details = {}
    for row in lines[header_index + 2 : table_end]:
        columns = [column.strip() for column in row.strip().strip("|").split("|", 1)]
        if len(columns) == 2:
            details[columns[0]] = columns[1]
    remaining = lines[:header_index] + lines[table_end:]
    return details, "\n".join(remaining).strip()


def extract_examples(section_text):
    examples = {"요청 예시": None, "응답 예시": None}
    labeled_pattern = re.compile(
        r"#### (요청 예시|응답 예시)\s*\n+"
        r"```(json|http|text)\n(.*?)\n```",
        re.DOTALL,
    )

    def replace_labeled(match):
        title, language, code = match.groups()
        if language == "json":
            code = prettify_json(code)
        examples[title] = f"#### {title}\n\n```{language}\n{code}\n```"
        return ""

    remaining = labeled_pattern.sub(replace_labeled, section_text).strip()
    unlabeled_pattern = re.compile(
        r"```(json|http|text)\n(.*?)\n```",
        re.DOTALL,
    )
    matches = list(unlabeled_pattern.finditer(remaining))
    missing_titles = [title for title, value in examples.items() if value is None]
    for title, match in zip(missing_titles, matches):
        language, code = match.groups()
        if language == "json":
            code = prettify_json(code)
        examples[title] = f"#### {title}\n\n```{language}\n{code}\n```"

    remaining = unlabeled_pattern.sub("", remaining).strip()
    for title, value in examples.items():
        if value is None:
            examples[title] = f"#### {title}\n\n없음"
    return examples, remaining


def validate_single_api(section_header, method_path):
    methods = HTTP_METHOD_PATTERN.findall(method_path)
    if len(methods) != 1 or "..." in method_path:
        raise ValueError(
            f"{section_header}: multiple or abbreviated APIs found in "
            f"'{method_path}'. Split the source Markdown into one section per API "
            "and provide separate parameters, bodies, status codes, and examples."
        )
    match = re.fullmatch(
        r"\s*(GET|POST|PUT|PATCH|DELETE)\s+(\S+)\s*",
        method_path.replace("`", ""),
    )
    if not match:
        raise ValueError(
            f"{section_header}: invalid Method / Path value '{method_path}'."
        )
    return match.groups()


def normalize_api_section(section_header, section_content):
    details, remaining = extract_table(section_content)
    method_path = details.get("Method / Path")
    if method_path is None:
        return f"{section_header}\n\n{section_content.strip()}"

    method, path = validate_single_api(section_header, method_path)
    examples, remaining = extract_examples(remaining)
    table_lines = ["| 항목 | 내용 |", "|---|---|"]
    for item in REQUIRED_ITEMS:
        value = details.get(item, "없음")
        if item == "Method / Path":
            value = f"`{method} {path}`"
        table_lines.append(f"| {item} | {value} |")

    parts = [section_header, "\n".join(table_lines)]
    if remaining:
        parts.append(remaining)
    parts.extend((examples["요청 예시"], examples["응답 예시"]))
    return "\n\n".join(parts)


def normalize_markdown(content):
    section_pattern = re.compile(r"(^### \d+\.\d+ .*$)", re.MULTILINE)
    matches = list(section_pattern.finditer(content))
    if not matches:
        return content.rstrip() + "\n"

    output_parts = [content[: matches[0].start()].rstrip()]
    for index, match in enumerate(matches):
        section_end = (
            matches[index + 1].start()
            if index + 1 < len(matches)
            else len(content)
        )
        section_header = match.group(1).strip()
        section_content = content[match.end() : section_end].strip()
        major_heading = re.search(r"^## .*$", section_content, re.MULTILINE)
        if major_heading:
            api_content = section_content[: major_heading.start()].strip()
            trailing_content = section_content[major_heading.start() :].strip()
        else:
            api_content = section_content
            trailing_content = ""

        output_parts.append(normalize_api_section(section_header, api_content))
        if trailing_content:
            output_parts.append(trailing_content)
    return "\n\n".join(output_parts).strip() + "\n"


def prepare_markdown(
    main_path,
    detail_paths,
    output_path,
    common_end_marker=None,
):
    main_path = Path(main_path)
    output_path = Path(output_path)
    parts = [
        common_section(
            main_path.read_text(encoding="utf-8"),
            common_end_marker,
        )
    ]
    for detail_path in detail_paths:
        detail_path = Path(detail_path)
        parts.append(
            detail_sections(
                detail_path.read_text(encoding="utf-8"),
                detail_path,
            )
        )

    normalized = normalize_markdown("\n\n---\n\n".join(parts))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(normalized, encoding="utf-8")
    return output_path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Combine and normalize API specification Markdown files."
    )
    parser.add_argument("--main", required=True, type=Path)
    parser.add_argument("--detail", action="append", default=[], type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--common-end-marker")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = prepare_markdown(
        args.main,
        args.detail,
        args.output,
        args.common_end_marker,
    )
    print(f"Prepared Markdown: {result}")
