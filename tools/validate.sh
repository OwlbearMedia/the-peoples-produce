#!/usr/bin/env bash
# Validates every ESPHome node config with throwaway secrets, so it runs anywhere
# without the real secrets.yaml or any hardware.
#
#   tools/validate.sh            schema and config validation
#   tools/validate.sh --compile  also build the firmware (checks C++ lambdas)
#
# Requires uv (https://docs.astral.sh/uv/). ESPHOME_VERSION overrides the pinned version.
set -euo pipefail

ESPHOME_VERSION="${ESPHOME_VERSION:-2026.9.1}"
command="config"
[[ "${1:-}" == "--compile" ]] && command="compile"

root="$(cd "$(dirname "$0")/.." && pwd)"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

# Copy only tracked config, never the real secrets or old build output.
cp -R "$root/esphome/packages" "$work/"
cp "$root"/esphome/*.yaml "$work/"
rm -f "$work/secrets.yaml"
cat > "$work/secrets.yaml" <<EOF
wifi_ssid: "validate"
wifi_password: "validate-password"
fallback_ap_password: "validate-password"
api_encryption_key: "$(openssl rand -base64 32)"
EOF

status=0
for node in "$work"/*.yaml; do
  name="$(basename "$node")"
  [[ "$name" == "secrets.yaml" ]] && continue
  echo "==> esphome $command $name"
  if ! uvx --from "esphome==$ESPHOME_VERSION" esphome "$command" "$node" > "$work/$name.log" 2>&1; then
    cat "$work/$name.log"
    echo "FAILED: $name"
    status=1
  else
    grep -E "^(WARNING|ERROR)" "$work/$name.log" || true
    echo "ok: $name"
  fi
done
exit $status
