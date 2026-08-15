#!/usr/bin/env bash
# Launch Nuxt so the QR / Network URL works on a phone against the real API.
# Usage (from frontend/ or repo root via this path):
#   ./scripts/dev-mobile.sh
#   ./scripts/dev-mobile.sh 10.0.0.156

set -euo pipefail
cd "$(dirname "$0")/.."

# Prefer primary LAN IP (same machine Nuxt prints as Network URL)
if [[ "${1:-}" != "" ]]; then
  LAN_IP="$1"
else
  LAN_IP="$(ip -4 route get 1.1.1.1 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i=="src"){print $(i+1); exit}}')"
fi

if [[ -z "${LAN_IP:-}" ]]; then
  echo "Could not detect LAN IP. Pass it: ./scripts/dev-mobile.sh 10.0.0.156" >&2
  exit 1
fi

export NUXT_PUBLIC_API_MODE=http
# Phone cannot use localhost — that would point at the phone itself
export NUXT_PUBLIC_API_BASE_URL="http://${LAN_IP}:8000"

echo "LAN IP:              ${LAN_IP}"
echo "API (phone + PC):    ${NUXT_PUBLIC_API_BASE_URL}"
echo "Open on phone via Nuxt Network / QR URL (same Wi‑Fi as this machine)."
echo "Ensure backend CORS includes http://${LAN_IP}:3000–3003 (Nuxt may use 3002 if lower ports are busy)"
echo

exec npm run dev -- --host 0.0.0.0 --port 3000
