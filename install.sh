#!/usr/bin/env sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
skills_dir="${CODEX_HOME:-$HOME/.codex}/skills"

mkdir -p "$skills_dir"

for source_dir in "$repo_dir"/skills/*; do
    skill_name=$(basename "$source_dir")
    target_dir="$skills_dir/$skill_name"

    rm -rf "$target_dir"
    cp -R "$source_dir" "$target_dir"
    printf 'Installed %s\n' "$skill_name"

    if [ "${INSTALL_VISUALIZATION_DEPS:-0}" = "1" ] &&
       [ "$skill_name" = "generate-professional-pdf" ]; then
        if ! command -v npm >/dev/null 2>&1; then
            printf 'npm is required for visualization dependencies.\n' >&2
            exit 1
        fi
        npm install --prefix "$target_dir" \
            @mermaid-js/mermaid-cli vega vega-lite vega-cli
    fi
done

printf 'Restart Codex to refresh the skill list.\n'
