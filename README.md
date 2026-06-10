# codex-toolkit

Personal Codex skills and reusable workflows.

## Skills

- `generate-professional-pdf`: Markdown 문서를 전문적인 PDF로 생성하고
  텍스트 및 전체 페이지 렌더링을 검증합니다.
- `generate-api-spec-pdf`: API 명세를 endpoint 단위로 정규화한 뒤
  `generate-professional-pdf`를 사용해 PDF로 생성합니다.

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
