#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

scripts_dir="${AGENTBASE_SKILL_SCRIPTS:-$HOME/.codex/skills/agentbase/scripts}"
default_base_url="https://maas-llm-aiplatform-hcm.api.vngcloud.vn/v1"
default_model="qwen/qwen3-5-27b"

if [[ ! -x "${scripts_dir}/save_iam_credentials.sh" && ! -f "${scripts_dir}/save_iam_credentials.sh" ]]; then
  echo "AgentBase helper scripts not found at: ${scripts_dir}"
  echo "Set AGENTBASE_SKILL_SCRIPTS to the folder containing save_iam_credentials.sh."
  exit 1
fi

echo "Set up local credentials for Bé Hadi Bảo hiểm"
echo "Secrets will be saved only to local files ignored by Git/Docker:"
echo "  - .greennode.json for IAM"
echo "  - .env for LLM config"
echo

read -r -p "GREENNODE_CLIENT_ID: " client_id
if [[ -z "${client_id}" ]]; then
  echo "GREENNODE_CLIENT_ID is required."
  exit 1
fi

read -r -s -p "GREENNODE_CLIENT_SECRET (hidden): " client_secret
echo
if [[ -z "${client_secret}" ]]; then
  echo "GREENNODE_CLIENT_SECRET is required."
  exit 1
fi

printf "%s" "${client_secret}" | bash "${scripts_dir}/save_iam_credentials.sh" \
  --client-id "${client_id}" \
  --secret-stdin

echo
echo "LLM setup"
echo "Use GreenNode AI Platform API key if available."
read -r -p "LLM_BASE_URL [${default_base_url}]: " base_url
base_url="${base_url:-$default_base_url}"

read -r -p "LLM_MODEL [${default_model}]: " model
model="${model:-$default_model}"

read -r -s -p "AI_PLATFORM_API_KEY / LLM_API_KEY (hidden): " llm_key
echo
if [[ -z "${llm_key}" ]]; then
  echo "LLM_API_KEY is required."
  exit 1
fi

printf "%s" "${llm_key}" | bash "${scripts_dir}/save_env_var.sh" \
  --key LLM_API_KEY \
  --value-stdin \
  --extra "LLM_BASE_URL=${base_url}" \
  --extra "LLM_MODEL=${model}" \
  --extra "LLM_TIMEOUT_SECONDS=90"

printf "%s" "${llm_key}" | bash "${scripts_dir}/save_env_var.sh" \
  --key AI_PLATFORM_API_KEY \
  --value-stdin

echo
bash "${scripts_dir}/check_credentials.sh" iam
bash "${scripts_dir}/check_credentials.sh" llm

echo
echo "Credentials are ready for local test/deploy."
