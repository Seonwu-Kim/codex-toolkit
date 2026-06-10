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
done

printf 'Restart Codex to refresh the skill list.\n'
