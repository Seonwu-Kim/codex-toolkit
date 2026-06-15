---
name: generate-technical-spec-pdf
description: Use when requirements, ERD, data models, architecture, interfaces, or technical decisions must become a dense professional PDF with chapter-level page separation, structured tables, code, and diagrams. Use generate-api-spec-pdf instead when endpoint contracts are the primary content.
---

# Generate Technical Specification PDF

Shape technical source material before delegating rendering and visual
inspection to the sibling `generate-professional-pdf` skill.

## Scope

Include requirements, domain/data models, ERD, architecture, interfaces,
constraints, and technical decisions. Do not reproduce endpoint-by-endpoint
API normalization here. When API contracts dominate the document, use
`generate-api-spec-pdf`; when APIs are supporting context, summarize them as
interfaces and link or append the dedicated API specification.

## Structure

Start from `references/outline.md`. Keep one responsibility per H2 and set
`section_page_break` to `always`. Prefer:

- requirement and constraint matrices over long prose;
- Mermaid-exported images or other rendered diagrams with captions;
- code blocks only for contracts, schemas, configuration, or critical logic;
- explicit IDs for requirements, components, entities, and decisions;
- traceability from requirements to components and verification.

Use `references/metadata.example.json` for dense typography and tables that
may continue across pages. Customize
`references/validation-profile.example.json` to the actual headings and
required terminology.

## Build

Run the sibling engine:

```bash
python ../generate-professional-pdf/scripts/build_document_pdf.py \
  --input TECHNICAL_SPEC.md \
  --metadata references/metadata.example.json \
  --profile references/validation-profile.example.json \
  --output Technical_Specification.pdf \
  --work-dir /tmp/technical-spec-review
```

Inspect the cover, every chapter start, all diagrams, the widest table, the
longest code block, and the final page. Confirm cross-references and diagram
labels remain legible.
