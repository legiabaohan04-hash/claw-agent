#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

source_file="${1:-$HOME/.codex/tableau-mcp.env}"
if [[ ! -f "${source_file}" ]]; then
  echo "Tableau MCP env not found: ${source_file}"
  exit 1
fi

tmp_file="$(mktemp)"
trap 'rm -f "${tmp_file}"' EXIT

grep -E '^(SERVER|SITE_NAME|PAT_NAME|PAT_VALUE|REST_API_VERSION)=' "${source_file}" > "${tmp_file}"

if [[ ! -s "${tmp_file}" ]]; then
  echo "No Tableau env keys found in ${source_file}"
  exit 1
fi

touch .env
chmod 600 .env

while IFS='=' read -r key value; do
  value="${value%\"}"
  value="${value#\"}"
  value="${value%\'}"
  value="${value#\'}"
  if grep -q "^${key}=" .env 2>/dev/null; then
    grep -v "^${key}=" .env > .env.tmp && mv .env.tmp .env
  fi
  echo "${key}=${value}" >> .env
done < "${tmp_file}"

for pair in \
  "TABLEAU_AUTO_REFRESH=true" \
  "TABLEAU_HTTP_TIMEOUT_SECONDS=30" \
  "TABLEAU_VIEW_INSURANCE_PERFORMANCE_ID=d3bc93f4-3036-449c-84f8-0a4875cbfc5b" \
  "TABLEAU_VIEW_INSURANCE_TRAFFIC_ID=d580ce59-6cc4-4e74-93e0-79b75b2f9154" \
  "TABLEAU_VIEW_PROMOTION_SUMMARY_ID=5f8e8ee3-2a76-417b-91ab-e2f4e680e286" \
  "TABLEAU_APPID_FILTER_FIELDS=Sku,App ID" \
  "TABLEAU_PERFORMANCE_APPID_FILTER_FIELDS=Sku,App ID" \
  "TABLEAU_PRODUCT_APPID_FILTER_FIELDS=App ID,Sku,SKU Name" \
  "TABLEAU_TRAFFIC_APPID_FILTER_FIELDS=SKU NAME,APP NAME,App ID" \
  "TABLEAU_PROMOTION_APPID_FILTER_FIELDS=*App ID,App ID,Campaign Code,Campaign ID"; do
  key="${pair%%=*}"
  if grep -q "^${key}=" .env 2>/dev/null; then
    grep -v "^${key}=" .env > .env.tmp && mv .env.tmp .env
  fi
  echo "${pair}" >> .env
done

for ignored in .env .greennode.json; do
  if [[ -f .gitignore ]] && ! grep -qxF "${ignored}" .gitignore; then
    echo "${ignored}" >> .gitignore
  fi
  if [[ -f .dockerignore ]] && ! grep -qxF "${ignored}" .dockerignore; then
    echo "${ignored}" >> .dockerignore
  fi
done

echo "Imported Tableau config into local .env without printing secrets."
echo "Note: AppID-level answers need TABLEAU_VIEW_PRODUCT_PERFORMANCE_ID if the default dashboard view only exports aggregate rows."
