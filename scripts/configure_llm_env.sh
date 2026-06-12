#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

default_base_url="https://maas-llm-aiplatform-hcm.api.vngcloud.vn/v1"
default_model="qwen/qwen3-5-27b"

echo "Configure Bé Hadi Bảo hiểm LLM environment"
echo "Base URL default: ${default_base_url}"
echo

read -r -p "LLM_BASE_URL [${default_base_url}]: " base_url
base_url="${base_url:-$default_base_url}"

read -r -p "LLM_MODEL [${default_model}]: " model
model="${model:-$default_model}"

read -r -s -p "LLM_API_KEY (hidden): " api_key
echo
if [[ -z "${api_key}" ]]; then
  echo "LLM_API_KEY is required."
  exit 1
fi

touch .env

set_env() {
  local key="$1"
  local value="$2"
  if grep -q "^${key}=" .env 2>/dev/null; then
    grep -v "^${key}=" .env > .env.tmp && mv .env.tmp .env
  fi
  printf '%s=%s\n' "$key" "$value" >> .env
}

set_env "LLM_API_KEY" "${api_key}"
set_env "AI_PLATFORM_API_KEY" "${api_key}"
set_env "LLM_BASE_URL" "${base_url}"
set_env "LLM_MODEL" "${model}"
set_env "LLM_TIMEOUT_SECONDS" "90"

chmod 600 .env

echo
echo ".env updated locally with restricted permissions."
echo "Do not commit .env. It is already ignored by .gitignore."
