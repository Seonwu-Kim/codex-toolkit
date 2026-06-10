---
name: generate-incident-report-pdf
description: Use when an outage, degradation, security event, data issue, failed deployment, or operational incident needs an evidence-led PDF covering timeline, impact, detection, root cause, contributing factors, remediation, owners, and due dates.
---

# Generate Incident Report PDF

Build a blameless, evidence-led incident narrative before delegating PDF
rendering and visual inspection to `generate-professional-pdf`.

## Structure

Start from `references/outline.md`. Use absolute timestamps with timezone and
distinguish fact, inference, and unknown:

- quantify user, service, data, financial, and duration impact;
- keep the timeline chronological and source each important event;
- separate trigger, root cause, and contributing factors;
- explain why detection and safeguards did or did not work;
- give every corrective action an owner, priority, due date, and verification;
- avoid naming individuals as causes.

Use `references/metadata.example.json` and customize the validation profile.
Redact secrets, personal data, tokens, and exploitable operational details.

## Build

```bash
python ../generate-professional-pdf/scripts/build_document_pdf.py \
  --input INCIDENT_REPORT.md \
  --metadata references/metadata.example.json \
  --profile references/validation-profile.example.json \
  --output Incident_Report.pdf \
  --work-dir /tmp/incident-report-review
```

Inspect the impact summary, full timeline, root-cause diagram, action table,
and final page. Verify timestamps, durations, owners, and due dates against
the source evidence.
