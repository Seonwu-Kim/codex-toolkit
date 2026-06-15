#!/usr/bin/env python3

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET


RENDERERS = {
    "mermaid": {
        "binary": "mmdc",
        "env": "MMDC",
        "install": "npm install --prefix <skill-dir> @mermaid-js/mermaid-cli",
    },
    "graphviz": {
        "binary": "dot",
        "env": "DOT",
        "install": "brew install graphviz  # or: sudo apt-get install graphviz",
    },
    "vega-lite": {
        "binary": "vl2svg",
        "env": "VL2SVG",
        "install": "npm install --prefix <skill-dir> vega vega-lite vega-cli",
    },
}


def find_renderer(visual_type):
    config = RENDERERS[visual_type]
    override = os.environ.get(config["env"])
    if override:
        path = Path(override).expanduser()
        if path.is_file():
            return str(path)

    executable = shutil.which(config["binary"])
    if executable:
        return executable

    local = Path(__file__).resolve().parents[1] / "node_modules" / ".bin"
    candidate = local / config["binary"]
    if candidate.is_file():
        return str(candidate)

    raise RuntimeError(
        f"{config['binary']} was not found. Install it with: {config['install']}"
    )


def build_command(visual_type, executable, source, output, args):
    if visual_type == "mermaid":
        config = (
            Path(__file__).resolve().parents[1]
            / "assets"
            / "visualization"
            / "mermaid-config.json"
        )
        return [
            executable,
            "-i",
            str(source),
            "-o",
            str(output),
            "-b",
            args.background,
            "-t",
            args.theme,
            "-s",
            str(args.scale),
            "-c",
            str(config),
        ]
    if visual_type == "graphviz":
        return [executable, "-Tsvg", str(source), "-o", str(output)]
    return [
        executable,
        str(source),
        str(output),
        "-s",
        str(args.scale),
    ]


def validate_svg(output):
    try:
        root = ET.parse(output).getroot()
    except (ET.ParseError, OSError) as error:
        output.unlink(missing_ok=True)
        raise RuntimeError("Renderer did not create a valid SVG file.") from error

    if root.tag.split("}")[-1] != "svg":
        output.unlink(missing_ok=True)
        raise RuntimeError("Renderer did not create a valid SVG file.")

    if not root.get("viewBox") and not (root.get("width") and root.get("height")):
        output.unlink(missing_ok=True)
        raise RuntimeError("SVG must define viewBox or width and height.")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Render Mermaid, Graphviz, or Vega-Lite source to SVG."
    )
    parser.add_argument(
        "--type",
        choices=sorted(RENDERERS),
        required=True,
        dest="visual_type",
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--theme", default="neutral")
    parser.add_argument("--background", default="white")
    parser.add_argument("--scale", default=2.0, type=float)
    return parser.parse_args()


def main():
    args = parse_args()
    source = args.input.expanduser().resolve()
    output = args.output.expanduser().resolve()

    if not source.is_file():
        raise RuntimeError(f"Input file does not exist: {source}")
    if output.suffix.lower() != ".svg":
        raise RuntimeError("Output path must use the .svg extension.")

    output.parent.mkdir(parents=True, exist_ok=True)
    executable = find_renderer(args.visual_type)
    command = build_command(
        args.visual_type,
        executable,
        source,
        output,
        args,
    )
    subprocess.run(command, check=True)
    validate_svg(output)
    print(output)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
