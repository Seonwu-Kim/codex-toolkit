---
name: generate-professional-pdf
description: Use when one or more Markdown documents must become a polished professional PDF, including requirements, architecture, ERD, plans, reports, meeting records, proposals, or specifications where a cover, revision history, consistent styling, content checks, and rendered-page inspection matter.
---

# Generate Professional PDF

Use the bundled deterministic pipeline instead of constructing PDF layout
ad hoc.

## Inputs

Collect:

- One or more Markdown files in final document order.
- Metadata JSON based on `references/metadata.example.json`.
- Validation JSON based on `references/validation-profile.example.json`.
- An optional custom HTML template. Use the bundled template by default.

Metadata controls branding, title, colors, arbitrary cover fields, revision
history, and whether each H2 starts a new page through
`section_page_break` (`auto` or `always`). Validation profiles express
document-specific required text, forbidden terms, occurrence counts, and
review-page markers.

Use the optional typography and cover fields when a document profile needs a
dense technical layout or a compact meeting-notes cover:

- `body_font_size`, `body_line_height`, and `table_font_size`
- `table_page_break` (`avoid` or `auto`)
- `cover_min_height`, `cover_padding_top`, and `cover_title_size`
- `cover_page_break` (`always` or `auto`)

For structured forms or contract tables, customize the first column with
`first_column_width`, `first_column_background`,
`first_column_font_weight`, and `first_column_white_space`.

Read `references/document-profiles.md` when selecting rules for a requirements
document, architecture document, report, or API specification.

## Environment

Use a task-local virtual environment when dependencies are unavailable:

```bash
python -m pip install markdown weasyprint pypdf Pillow
```

Use `pdftoppm` from Poppler. Prefer an existing bundled binary before
installing system software.

## Build

```bash
python scripts/build_document_pdf.py \
  --input COVER_AND_COMMON.md \
  --input DETAILS.md \
  --metadata metadata.json \
  --profile validation-profile.json \
  --output document.pdf \
  --work-dir /tmp/document-pdf-review
```

Inputs are concatenated in the order provided. Pass `--template` only when the
document needs a different visual system.

## Validation

The build must fail when:

- Required text is absent.
- Forbidden terms or patterns remain.
- Expected occurrence counts are wrong.
- Terms configured as an equal-count group have different counts.
- Page-count constraints fail.
- Rendered pages are blank-like or content reaches page edges suspiciously.

The result includes page count, sparse-text page candidates, configured
occurrence counts, and page numbers for every `review_terms` entry.

## Visual Review

Automated checks are necessary but not sufficient. After a successful build:

1. Inspect the cover and revision history.
2. Inspect every page listed under `review_pages`.
3. Inspect every page listed under `sparse_text_pages` and decide whether the
   whitespace is intentional.
4. Inspect pages containing long tables, code blocks, diagrams, or images.
5. Inspect the final page.
6. Confirm there is no clipping, overlap, broken glyph, misplaced heading, or
   unexpected blank page.

Do not claim completion from text extraction alone.
