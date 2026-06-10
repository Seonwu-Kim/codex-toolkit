#!/usr/bin/env python3
import argparse
import json
import tempfile
from pathlib import Path

from render_document import render_pdf
from validate_document import validate_pdf


SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TEMPLATE = SKILL_ROOT / "assets" / "professional-document.html"


def combine_markdown(input_paths, output_path):
    parts = [
        Path(path).read_text(encoding="utf-8").strip()
        for path in input_paths
    ]
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "\n\n---\n\n".join(parts).strip() + "\n",
        encoding="utf-8",
    )
    return output_path


def build(
    inputs,
    metadata,
    profile,
    output,
    template=DEFAULT_TEMPLATE,
    work_dir=None,
    pdftoppm=None,
):
    if work_dir:
        work_path = Path(work_dir)
        work_path.mkdir(parents=True, exist_ok=True)
        temporary = None
    else:
        temporary = tempfile.TemporaryDirectory(prefix="professional-pdf-")
        work_path = Path(temporary.name)

    combined = combine_markdown(inputs, work_path / "combined.md")
    render_dir = work_path / "rendered"
    render_pdf(combined, template, metadata, output)
    result = validate_pdf(output, profile, render_dir, pdftoppm)
    if temporary:
        temporary.cleanup()
    if result["errors"]:
        raise RuntimeError("; ".join(result["errors"]))
    return result


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build and validate a polished professional PDF."
    )
    parser.add_argument("--input", action="append", required=True, type=Path)
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--work-dir", type=Path)
    parser.add_argument("--pdftoppm", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = build(
        inputs=args.input,
        metadata=args.metadata,
        profile=args.profile,
        output=args.output,
        template=args.template,
        work_dir=args.work_dir,
        pdftoppm=args.pdftoppm,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
