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

The renderer creates a table of contents from Markdown headings and prints
each heading's final PDF page number. Configure it with:

- `toc_enabled` to include or omit the table of contents
- `toc_title`, `toc_start_level`, and `toc_depth`
  (`2`/`2` for H2, `2`/`3` for H2-H3, `1`/`3` for H1-H3)

When section numbering restarts, add an explicit H1 chapter for each numbering
scope and set `toc_start_level` to `1`. Never show repeated top-level numbers
without the chapter that explains the reset.
- `toc_page_break_before` and `toc_page_break_after`

The page number uses WeasyPrint's target counter after pagination, so do not
calculate or type page numbers manually. Keep `toc_page_break_before` as
`always` so the table of contents starts on its own page.

Use the optional typography and cover fields when a document profile needs a
dense technical layout or a compact meeting-notes cover:

- `body_font_size`, `body_line_height`, and `table_font_size`
- `table_page_break` (`avoid` or `auto`)
- `cover_min_height`, `cover_padding_top`, and `cover_title_size`
- `cover_page_break` (`always` or `auto`)

Code blocks use a Korean-capable monospace fallback stack. Keep JSON fences as
`json` and inspect delimiter quotes, escaped quotes, and nested closing
brackets during visual review.

For structured forms or contract tables, customize the first column with
`first_column_width`, `first_column_background`,
`first_column_font_weight`, and `first_column_white_space`.

Read `references/document-profiles.md` when selecting rules for a requirements
document, architecture document, report, or API specification.

## Visualizations

When the document needs architecture diagrams, flows, ERDs, Gantt charts, or
data charts, read `references/visualizations.md`. Start from a bundled template
under `assets/visualization/` and render it with
`scripts/render_visual.py`. Prefer generated SVG over hand-written SVG.

Do not place layout instructions, drawing notes, or agent-facing guidance in
the document. Captions and callouts must explain the business or technical
meaning of the visual.

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
2. Inspect the table of contents and verify several entries against their
   destination pages.
3. Inspect every page listed under `review_pages`.
4. Inspect every page listed under `sparse_text_pages` and decide whether the
   whitespace is intentional.
5. Inspect pages containing long tables, code blocks, diagrams, or images.
6. Inspect every diagram at normal size and at 200% zoom. Confirm arrow
   direction, node-boundary termination, label spacing, and legibility.
7. Inspect the final page.
8. Confirm there is no clipping, overlap, broken glyph, misplaced heading, or
   unexpected blank page.

Do not claim completion from text extraction alone.
