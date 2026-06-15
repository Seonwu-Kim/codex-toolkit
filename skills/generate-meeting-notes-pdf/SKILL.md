---
name: generate-meeting-notes-pdf
description: Use when meeting minutes, decision records, workshop notes, review outcomes, or committee notes must become a short, dense PDF centered on decisions, action items, owners, due dates, and unresolved questions.
---

# Generate Meeting Notes PDF

Condense meeting material into decisions and accountable follow-up, then use
the sibling `generate-professional-pdf` engine for rendering and inspection.

## Structure

Start from `references/outline.md`. Keep the document short:

- use a compact cover without a dedicated cover page when practical;
- summarize discussion only when it explains a decision or action;
- number decisions and action items;
- assign each action one owner, due date, and completion criterion;
- distinguish unresolved questions from deferred decisions;
- omit transcript-like dialogue and repeated context.

Use `references/metadata.example.json` for the compact cover and
`references/validation-profile.example.json` for accountability checks.

## Build

```bash
python ../generate-professional-pdf/scripts/build_document_pdf.py \
  --input MEETING_NOTES.md \
  --metadata references/metadata.example.json \
  --profile references/validation-profile.example.json \
  --output Meeting_Notes.pdf \
  --work-dir /tmp/meeting-notes-review
```

Inspect the compact cover transition, decision table, action-item table, and
final page. Confirm every action has an owner and due date, and that no
important decision exists only in prose.
