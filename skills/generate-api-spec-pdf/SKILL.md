---
name: generate-api-spec-pdf
description: Use when API specification Markdown files need endpoint-by-endpoint normalization before becoming a professional PDF, especially when each API requires a fixed contract table, separate request and response examples, exact endpoint counts, and project-specific terminology checks.
---

# Generate API Specification PDF

Normalize API contracts, then delegate PDF rendering and page inspection to
the `generate-professional-pdf` skill. Do not duplicate its renderer,
template, or generic visual validator here.

## Inputs

Collect:

- One main Markdown file containing common rules.
- Zero or more detail Markdown files.
- Metadata JSON based on `references/metadata.example.json`.
- API validation JSON based on
  `references/validation-profile.example.json`.
- The heading that ends the common section when the main document also
  contains an API index.

Each endpoint must have its own `### N.N` section and contract table:

```markdown
| 항목 | 내용 |
|---|---|
| Method / Path | `GET games` |
| 설명 | 경기 목록을 조회합니다. |
| Path Parameter | 없음 |
| Query Parameter | `page`, `size` |
| Request Body | 없음 |
| Response Body | `content`, `page` |
| Status Code | `200` |
```

Place request and response code blocks after the table. The preparer adds
their headings and formats strict JSON with two-space indentation and aligned
object/array closing brackets. Invalid JSON, trailing commas, non-standard
constants, smart-quote delimiters, and duplicate keys must fail the build
instead of passing through unformatted.

ASCII `"` characters remain JSON delimiters. Escaped quotes inside values
remain `\"`; typographic quotes such as `“` and `”` are preserved only when
they are intentional string content.

Keep `toc_depth` at `3` so the generated table of contents lists both major
API groups and individual endpoint sections with their final page numbers.
If API group numbering restarts across larger domains, add an H1 chapter for
each domain and set `toc_start_level` to `1`; the chapter must be visible in
the table of contents.

## Build

```bash
python scripts/build_api_spec_pdf.py \
  --main MAIN.md \
  --detail DETAIL_1.md \
  --detail DETAIL_2.md \
  --common-end-marker "## 2. API Index" \
  --metadata metadata.json \
  --profile validation-profile.json \
  --output API_Specification.pdf \
  --work-dir /tmp/api-spec-review
```

The wrapper automatically finds the sibling `generate-professional-pdf`
skill. Pass `--engine` only when testing an alternate installation.

The build must fail when:

- One section contains multiple or abbreviated APIs.
- Endpoint and example counts differ.
- Required API text is absent.
- Forbidden project terminology or combined methods appear.
- The generic PDF engine detects blank-like or suspiciously clipped pages.

Use the generic skill's `review_pages` output for visual inspection. Inspect
the cover, section boundaries, a long response example, and the final page.
