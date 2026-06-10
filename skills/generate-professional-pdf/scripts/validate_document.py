#!/usr/bin/env python3
import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path


def validate_text(text, profile):
    errors = []
    for value in profile.get("required_text", []):
        if value not in text:
            errors.append(f"required text not found: {value}")

    lowered = text.lower()
    for value in profile.get("forbidden_terms", []):
        if value.lower() in lowered:
            errors.append(f"forbidden term found: {value}")

    for pattern in profile.get("forbidden_patterns", []):
        if re.search(pattern, text, re.MULTILINE):
            errors.append(f"forbidden pattern found: {pattern}")

    for token, expected in profile.get("expected_occurrences", {}).items():
        actual = text.count(token)
        if actual != expected:
            errors.append(
                f"expected {expected} occurrences of '{token}' but found {actual}"
            )

    for group in profile.get("equal_occurrence_groups", []):
        counts = {token: text.count(token) for token in group}
        if len(set(counts.values())) > 1:
            errors.append(f"occurrence counts differ: {counts}")

    return errors


def locate_review_terms(page_texts, terms):
    return {
        term: [
            index + 1
            for index, page_text in enumerate(page_texts)
            if term in page_text
        ]
        for term in terms
    }


def extract_pdf(pdf_path):
    try:
        from pypdf import PdfReader
    except ImportError as error:
        raise RuntimeError("Missing dependency: pypdf") from error
    reader = PdfReader(str(pdf_path))
    page_texts = [page.extract_text() or "" for page in reader.pages]
    return page_texts


def render_and_scan(pdf_path, render_dir, pdftoppm=None):
    try:
        from PIL import Image
    except ImportError as error:
        raise RuntimeError("Missing dependency: Pillow") from error

    executable = pdftoppm or shutil.which("pdftoppm")
    if not executable:
        raise RuntimeError("pdftoppm was not found.")

    render_dir = Path(render_dir)
    render_dir.mkdir(parents=True, exist_ok=True)
    for existing_page in render_dir.glob("page-*.png"):
        existing_page.unlink()
    prefix = render_dir / "page"
    subprocess.run(
        [str(executable), "-png", "-r", "110", str(pdf_path), str(prefix)],
        check=True,
        capture_output=True,
        text=True,
    )

    pages = sorted(render_dir.glob("page-*.png"))
    blank_like = []
    edge_dense = []
    for page in pages:
        image = Image.open(page).convert("RGB")
        small = image.resize(
            (max(1, image.width // 20), max(1, image.height // 20))
        )
        pixels = list(small.getdata())
        nonwhite_ratio = (
            sum(1 for red, green, blue in pixels if min(red, green, blue) < 245)
            / len(pixels)
        )
        border = (
            list(small.crop((0, 0, small.width, 3)).getdata())
            + list(
                small.crop(
                    (0, small.height - 3, small.width, small.height)
                ).getdata()
            )
            + list(small.crop((0, 0, 3, small.height)).getdata())
            + list(
                small.crop(
                    (small.width - 3, 0, small.width, small.height)
                ).getdata()
            )
        )
        edge_ratio = (
            sum(1 for red, green, blue in border if min(red, green, blue) < 220)
            / len(border)
        )
        if nonwhite_ratio < 0.01:
            blank_like.append(page.name)
        if edge_ratio > 0.15:
            edge_dense.append(page.name)
    return {
        "rendered_pages": len(pages),
        "blank_like_pages": blank_like,
        "edge_dense_pages": edge_dense,
    }


def validate_pdf(pdf_path, profile_path, render_dir, pdftoppm=None):
    profile = json.loads(Path(profile_path).read_text(encoding="utf-8"))
    page_texts = extract_pdf(pdf_path)
    text = "\n".join(page_texts)
    errors = validate_text(text, profile)

    page_count = len(page_texts)
    minimum = profile.get("minimum_page_count")
    maximum = profile.get("maximum_page_count")
    if minimum is not None and page_count < minimum:
        errors.append(f"expected at least {minimum} pages but found {page_count}")
    if maximum is not None and page_count > maximum:
        errors.append(f"expected at most {maximum} pages but found {page_count}")

    render_result = render_and_scan(
        pdf_path,
        render_dir,
        pdftoppm,
    )
    if render_result["blank_like_pages"]:
        errors.append(
            "blank-like pages: "
            + ", ".join(render_result["blank_like_pages"])
        )
    if render_result["edge_dense_pages"]:
        errors.append(
            "possible clipped pages: "
            + ", ".join(render_result["edge_dense_pages"])
        )

    occurrences = {
        token: text.count(token)
        for token in profile.get("report_occurrences", [])
    }
    sparse_text_pages = [
        index + 1
        for index, page_text in enumerate(page_texts)
        if len("".join(page_text.split())) < 20
    ]
    return {
        "page_count": page_count,
        **render_result,
        "sparse_text_pages": sparse_text_pages,
        "occurrences": occurrences,
        "review_pages": locate_review_terms(
            page_texts,
            profile.get("review_terms", []),
        ),
        "errors": errors,
    }


def parse_args():
    parser = argparse.ArgumentParser(
        description="Validate professional PDF text and rendered pages."
    )
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--render-dir", required=True, type=Path)
    parser.add_argument("--pdftoppm", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = validate_pdf(
        args.pdf,
        args.profile,
        args.render_dir,
        args.pdftoppm,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result["errors"]:
        raise SystemExit(1)
