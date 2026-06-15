# codex-toolkit

Personal Codex skills and reusable workflows.

## Skills

- `generate-professional-pdf`: Markdown 문서를 전문적인 PDF로 생성하고
  텍스트 및 전체 페이지 렌더링을 검증합니다. Mermaid, Graphviz,
  Vega-Lite 기반 다이어그램·간트차트·데이터 차트 생성도 지원합니다.
- `generate-api-spec-pdf`: API 명세를 endpoint 단위로 정규화한 뒤
  `generate-professional-pdf`를 사용해 PDF로 생성합니다.
- `generate-technical-spec-pdf`: 요구사항, ERD, 데이터 모델, 아키텍처를
  촘촘한 표와 장별 페이지 구성의 기술 명세 PDF로 생성합니다. API
  endpoint 계약이 중심이면 `generate-api-spec-pdf`를 사용합니다.
- `generate-project-report-pdf`: 구현 계획, 진행 상황, 테스트 결과를
  요약 지표, 마일스톤, 결과, 다음 작업 중심의 PDF로 생성합니다.
- `generate-incident-report-pdf`: 장애 증거를 영향도, 타임라인, 원인,
  조치, 담당자 중심의 PDF로 생성합니다.
- `generate-meeting-notes-pdf`: 회의 내용을 결정 사항과 담당자·기한이
  있는 액션 아이템 중심의 짧고 밀도 높은 PDF로 생성합니다.

## Install

```bash
git clone https://github.com/Seonwu-Kim/codex-toolkit.git
cd codex-toolkit
./install.sh
```

기본 설치 경로는 `${CODEX_HOME:-$HOME/.codex}/skills`입니다. 설치 후
Codex를 다시 시작하면 스킬이 검색됩니다.

## Dependencies

```bash
python3 -m pip install markdown weasyprint pypdf Pillow PyYAML
```

PDF 페이지 렌더링 검증에는 Poppler의 `pdftoppm`이 필요합니다.

```bash
# macOS
brew install poppler

# Ubuntu / Debian
sudo apt-get install poppler-utils
```

WeasyPrint는 운영체제에 따라 추가 네이티브 라이브러리가 필요할 수
있습니다.

### Visualization dependencies

Mermaid와 Vega-Lite 도구를 스킬 설치와 함께 로컬 설치하려면:

```bash
INSTALL_VISUALIZATION_DEPS=1 ./install.sh
```

수동 설치도 가능합니다.

```bash
npm install --prefix ~/.codex/skills/generate-professional-pdf \
  @mermaid-js/mermaid-cli vega vega-lite vega-cli

# macOS
brew install graphviz

# Ubuntu / Debian
sudo apt-get install graphviz
```
