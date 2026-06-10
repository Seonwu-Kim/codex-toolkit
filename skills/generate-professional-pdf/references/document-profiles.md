# Document Profiles

Use the generic validation fields to express document-specific rules.

## Requirements

- Require `문서 개요`, `기능 요구사항`, `비기능 요구사항`, and `제약사항`.
- Forbid `TBD` and unresolved placeholder tokens.
- Add each major section to `review_terms`.
- For requirements combined with ERD and architecture, use the dedicated
  `generate-technical-spec-pdf` skill.

## Architecture

- Require `시스템 개요`, `구성 요소`, `데이터 흐름`, and `장애 처리`.
- Review pages containing architecture diagrams and long tables manually.

## Report

- Require `요약`, `분석 결과`, and `결론`.
- Use `expected_occurrences` when headings must appear exactly once.
- Use `generate-project-report-pdf` for implementation progress, milestones,
  test results, release readiness, and next work.

## Incident Report

- Use `generate-incident-report-pdf`.
- Require impact, timeline, root cause, corrective actions, owners, and due
  dates.
- Use absolute timestamps with timezone and scan for exposed secrets.

## Meeting Notes

- Use `generate-meeting-notes-pdf`.
- Prefer a compact cover and require decisions plus action items.
- Keep owners, due dates, and completion criteria explicit.

## API Specification

Keep endpoint normalization in the dedicated `generate-api-spec-pdf` skill.
Its profile can require equal counts for `Method / Path`, `요청 예시`, and
`응답 예시`.
