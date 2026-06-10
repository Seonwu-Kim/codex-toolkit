#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from prepare_markdown import prepare_markdown


SKILLS_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENGINE = (
    SKILLS_ROOT
    / "generate-professional-pdf"
    / "scripts"
    / "build_document_pdf.py"
)


def build(
    main,
    details,
    metadata,
    profile,
    output,
    common_end_marker=None,
    work_dir=None,
    pdftoppm=None,
    engine=DEFAULT_ENGINE,
    template=None,
):
    if work_dir:
        work_path = Path(work_dir)
        work_path.mkdir(parents=True, exist_ok=True)
        temporary = None
    else:
        temporary = tempfile.TemporaryDirectory(prefix="api-spec-pdf-")
        work_path = Path(temporary.name)

    prepared = work_path / "prepared-api-spec.md"
    prepare_markdown(main, details, prepared, common_end_marker)

    command = [
        sys.executable,
        str(engine),
        "--input",
        str(prepared),
        "--metadata",
        str(metadata),
        "--profile",
        str(profile),
        "--output",
        str(output),
        "--work-dir",
        str(work_path / "professional-pdf"),
    ]
    if pdftoppm:
        command.extend(["--pdftoppm", str(pdftoppm)])
    if template:
        command.extend(["--template", str(template)])

    completed = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
    )
    if temporary:
        temporary.cleanup()
    return json.loads(completed.stdout)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Normalize an API specification and build it with the "
        "generate-professional-pdf engine."
    )
    parser.add_argument("--main", required=True, type=Path)
    parser.add_argument("--detail", action="append", default=[], type=Path)
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--common-end-marker")
    parser.add_argument("--work-dir", type=Path)
    parser.add_argument("--pdftoppm", type=Path)
    parser.add_argument("--engine", type=Path, default=DEFAULT_ENGINE)
    parser.add_argument("--template", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = build(
        main=args.main,
        details=args.detail,
        metadata=args.metadata,
        profile=args.profile,
        output=args.output,
        common_end_marker=args.common_end_marker,
        work_dir=args.work_dir,
        pdftoppm=args.pdftoppm,
        engine=args.engine,
        template=args.template,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
