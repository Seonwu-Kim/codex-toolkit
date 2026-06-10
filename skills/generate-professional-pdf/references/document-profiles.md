# Document Profiles

Use the generic validation fields to express document-specific rules.

## Requirements

- Require `문서 개요`, `기능 요구사항`, `비기능 요구사항`, and `제약사항`.
- Forbid `TBD` and unresolved placeholder tokens.
- Add each major section to `review_terms`.

## Architecture

- Require `시스템 개요`, `구성 요소`, `데이터 흐름`, and `장애 처리`.
- Review pages containing architecture diagrams and long tables manually.

## Report

- Require `요약`, `분석 결과`, and `결론`.
- Use `expected_occurrences` when headings must appear exactly once.

## API Specification

Keep endpoint normalization in the dedicated `generate-api-spec-pdf` skill.
Its profile can require equal counts for `Method / Path`, `요청 예시`, and
`응답 예시`.
