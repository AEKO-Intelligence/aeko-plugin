#!/bin/sh
# Usage: ./scripts/lint-release-contracts.sh

set -eu

script_dir=$(CDPATH= cd "$(dirname "$0")" && pwd)
repo_root=$(CDPATH= cd "$script_dir/.." && pwd)

site_severity="$repo_root/skills/aeko-site-audit/references/severity.md"
pdp_severity="$repo_root/skills/aeko-pdp-audit/references/severity.md"

if ! cmp -s "$site_severity" "$pdp_severity"; then
  printf '%s\n' "ERROR: audit severity references are not byte-identical:" >&2
  printf '  %s\n  %s\n' "$site_severity" "$pdp_severity" >&2
  exit 1
fi

fetcher_reference="$repo_root/skills/aeko-pdp-audit/scripts/fetch_evidence.py"
fetcher_copies='skills/aeko-site-audit/scripts/fetch_evidence.py
skills/aeko-pdp-build/scripts/fetch_evidence.py
skills/aeko-message-audit/scripts/fetch_evidence.py'

if [ ! -x "$fetcher_reference" ]; then
  printf 'ERROR: bundled fetcher is missing or not executable: %s\n' "$fetcher_reference" >&2
  exit 1
fi

for relative_path in $fetcher_copies; do
  fetcher_copy="$repo_root/$relative_path"
  if [ ! -x "$fetcher_copy" ]; then
    printf 'ERROR: bundled fetcher copy is missing or not executable: %s\n' "$fetcher_copy" >&2
    exit 1
  fi
  if ! cmp -s "$fetcher_reference" "$fetcher_copy"; then
    printf '%s\n' 'ERROR: bundled fetch_evidence.py copies are not byte-identical:' >&2
    printf '  %s\n  %s\n' "$fetcher_reference" "$fetcher_copy" >&2
    exit 1
  fi
done

versions=$(
  for relative_path in \
    .claude-plugin/marketplace.json \
    .claude-plugin/plugin.json \
    .codex-plugin/marketplace.json \
    .codex-plugin/plugin.json \
    gemini-extension.json
  do
    sed -n 's/^[[:space:]]*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)"[[:space:]]*,\{0,1\}[[:space:]]*$/\1/p' "$repo_root/$relative_path"
  done
)

version_count=$(printf '%s\n' "$versions" | sed '/^$/d' | wc -l | tr -d '[:space:]')
if [ "$version_count" -ne 5 ]; then
  printf '%s\n' "ERROR: expected exactly one version declaration in each of the five release manifests." >&2
  exit 1
fi

unique_version_count=$(printf '%s\n' "$versions" | sort -u | wc -l | tr -d '[:space:]')
if [ "$unique_version_count" -ne 1 ]; then
  printf '%s\n' "ERROR: release manifest versions disagree:" >&2
  grep -Hn '"version"' \
    "$repo_root/.claude-plugin/marketplace.json" \
    "$repo_root/.claude-plugin/plugin.json" \
    "$repo_root/.codex-plugin/marketplace.json" \
    "$repo_root/.codex-plugin/plugin.json" \
    "$repo_root/gemini-extension.json" >&2
  exit 1
fi

compatibility_router_hits=$(
  find "$repo_root/skills" -type f -name SKILL.md \
    ! -path "$repo_root/skills/*-workspace/*" \
    -exec grep -HniE 'compatibility[[:space:]-]+router|This host cannot delegate to another skill' {} + || true
)
if [ -n "$compatibility_router_hits" ]; then
  printf '%s\n' "$compatibility_router_hits" >&2
  printf '%s\n' 'ERROR: unreleased catalog contains a compatibility routing stub.' >&2
  exit 1
fi

# Shipped-surface check only. outputs/ is dated research evidence and skills/*-workspace/ contains
# gitignored evaluation artifacts; neither is release content, so both are deliberately excluded.
deleted_slug_pattern='aeo''-audit|aeko''-onboarding|aeko''-visibility-report|aeko''-prompt-deep-dive|aeko''-check-source|aeko''-brand-competitor-analysis|aeko''-product-competitor-analysis|aeko''-find-prompts-to-track|aeko''-manage-tracked-prompts|aeko''-setup-store|aeko''-inject-reviews|aeko''-optimize-budget|aeko''-refresh-jsonld|aeko''-ad-report|aeko''-ad-guardrails|aeko''-compose-ads'
deleted_slug_hits=$(
  {
    find \
      "$repo_root/skills" \
      "$repo_root/scripts" \
      "$repo_root/.claude-plugin" \
      "$repo_root/.codex-plugin" \
      -type f ! -path "$repo_root/skills/*-workspace/*" -print
    printf '%s\n' \
      "$repo_root/gemini-extension.json" \
      "$repo_root/README.md" \
      "$repo_root/CHANGELOG.md" \
      "$repo_root/CUSTOMIZATION.md"
  } | while IFS= read -r shipped_file; do
    grep -HnE "$deleted_slug_pattern" "$shipped_file" || true
  done
)
if [ -n "$deleted_slug_hits" ]; then
  printf '%s\n' "$deleted_slug_hits" >&2
  printf '%s\n' 'ERROR: shipped release content references a deleted pre-release slug.' >&2
  exit 1
fi

prohibited_hits=$(
  find "$repo_root/skills" -type f -name SKILL.md \
    ! -path "$repo_root/skills/*-workspace/*" \
    -exec grep -HniE 'forensics|포렌식' {} + || true
)
if [ -n "$prohibited_hits" ]; then
  printf '%s\n' "$prohibited_hits" >&2
  printf '%s\n' 'ERROR: shipped skill prose contains a prohibited source-analysis term.' >&2
  exit 1
fi

python3 "$repo_root/scripts/lint-brand-contracts.py"
python3 "$repo_root/scripts/build-trusted-upstream-catalog.py" --check

printf 'Release contracts pass (version %s).\n' "$(printf '%s\n' "$versions" | sed -n '1p')"
