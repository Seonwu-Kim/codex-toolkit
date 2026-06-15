---
name: generate-project-report-pdf
description: Use when implementation plans, progress reports, milestone reviews, test results, release readiness, or project closeout material must become a professional PDF centered on summary metrics, milestones, outcomes, risks, and next work.
---

# Generate Project Report PDF

Normalize project evidence, then delegate rendering and page inspection to
the sibling `generate-professional-pdf` skill.

## Structure

Start from `references/outline.md`. Lead with a one-page executive summary and
keep metrics reproducible:

- state the reporting period, baseline, target, actual, and data source;
- separate completed outcomes from activity descriptions;
- show milestone status with owner and variance;
- report test scope, command/environment, result, failures, and residual risk;
- turn next work into prioritized actions with owner and target date.

Use `references/metadata.example.json` and customize the validation profile.
Do not claim completion or readiness without cited evidence.

## Build

```bash
python ../generate-professional-pdf/scripts/build_document_pdf.py \
  --input PROJECT_REPORT.md \
  --metadata references/metadata.example.json \
  --profile references/validation-profile.example.json \
  --output Project_Report.pdf \
  --work-dir /tmp/project-report-review
```

Inspect the executive summary, metric tables, milestone table, test-result
pages, next-work page, and final page. Verify that status colors are not the
only carrier of meaning.
