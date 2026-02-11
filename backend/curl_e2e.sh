#!/usr/bin/env bash
# End-to-end test for the iterative /chat endpoint.
# Requires: jq (brew install jq)
# Usage:   chmod +x curl_e2e.sh && ./curl_e2e.sh
# Expects: Flask server running on http://127.0.0.1:5000

set -euo pipefail

BASE_URL="http://127.0.0.1:5000"
BOLD='\033[1m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'
RESET='\033[0m'

log() { echo -e "\n${BOLD}${CYAN}=== $1 ===${RESET}\n"; }
pass() { echo -e "${GREEN}✓ $1${RESET}"; }

# ── Health check ──────────────────────────────────────────────────────
log "Health check"
curl -sf "${BASE_URL}/health" | jq .
pass "Server is up"

# ── Round 1: First message — no prior state ───────────────────────────
log "Round 1: Plan a trip to Tokyo (no prior state)"

R1=$(curl -sf -X POST "${BASE_URL}/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to plan a 3 day trip to Tokyo"
  }')

echo "$R1" | jq .

# Extract state for next round
R1_POIS=$(echo "$R1" | jq -c '.pois')
R1_REQS=$(echo "$R1" | jq -c '.requirements')
R1_PLAN=$(echo "$R1" | jq -c '.plan')

pass "Round 1 complete — pois: $(echo "$R1_POIS" | jq 'length'), requirements: $(echo "$R1_REQS" | jq 'length'), plan options: $(echo "$R1_PLAN" | jq 'length')"

# ── Round 2: Add requirement + add POI ────────────────────────────────
log "Round 2: Add budget requirement and add Kyoto (carries forward Round 1 state)"

R2=$(curl -sf -X POST "${BASE_URL}/chat" \
  -H "Content-Type: application/json" \
  -d "$(jq -n \
    --arg msg "I also want to visit Kyoto. Budget must be under \$3000." \
    --argjson pois "$R1_POIS" \
    --argjson reqs "$R1_REQS" \
    --argjson plan "$R1_PLAN" \
    '{message: $msg, pois: $pois, requirements: $reqs, plan: $plan}'
  )")

echo "$R2" | jq .

R2_POIS=$(echo "$R2" | jq -c '.pois')
R2_REQS=$(echo "$R2" | jq -c '.requirements')
R2_PLAN=$(echo "$R2" | jq -c '.plan')

pass "Round 2 complete — pois: $(echo "$R2_POIS" | jq 'length'), requirements: $(echo "$R2_REQS" | jq 'length'), plan options: $(echo "$R2_PLAN" | jq 'length')"

# ── Round 3: Remove a POI + add another requirement ──────────────────
log "Round 3: Remove Tokyo, add 'must include traditional food' requirement"

R3=$(curl -sf -X POST "${BASE_URL}/chat" \
  -H "Content-Type: application/json" \
  -d "$(jq -n \
    --arg msg "Remove Tokyo from the trip. I want to make sure we try traditional Japanese food." \
    --argjson pois "$R2_POIS" \
    --argjson reqs "$R2_REQS" \
    --argjson plan "$R2_PLAN" \
    '{message: $msg, pois: $pois, requirements: $reqs, plan: $plan}'
  )")

echo "$R3" | jq .

R3_POIS=$(echo "$R3" | jq -c '.pois')
R3_REQS=$(echo "$R3" | jq -c '.requirements')
R3_PLAN=$(echo "$R3" | jq -c '.plan')

pass "Round 3 complete — pois: $(echo "$R3_POIS" | jq 'length'), requirements: $(echo "$R3_REQS" | jq 'length'), plan options: $(echo "$R3_PLAN" | jq 'length')"

# ── Round 4: Non-actionable message — state should pass through unchanged
log "Round 4: General question (no POI/requirement changes — should skip Azure planner)"

R4=$(curl -sf -X POST "${BASE_URL}/chat" \
  -H "Content-Type: application/json" \
  -d "$(jq -n \
    --arg msg "What is the best time of year to visit Japan?" \
    --argjson pois "$R3_POIS" \
    --argjson reqs "$R3_REQS" \
    --argjson plan "$R3_PLAN" \
    '{message: $msg, pois: $pois, requirements: $reqs, plan: $plan}'
  )")

echo "$R4" | jq .

R4_POIS=$(echo "$R4" | jq -c '.pois')
R4_REQS=$(echo "$R4" | jq -c '.requirements')
R4_PLAN=$(echo "$R4" | jq -c '.plan')

# Verify state was returned unchanged
if [ "$R4_POIS" = "$R3_POIS" ] && [ "$R4_REQS" = "$R3_REQS" ] && [ "$R4_PLAN" = "$R3_PLAN" ]; then
  pass "Round 4 complete — state passed through unchanged (no actionable intents)"
else
  echo "⚠  Round 4: state changed unexpectedly for a non-actionable message"
fi

# ── Round 5: Remove a requirement ─────────────────────────────────────
log "Round 5: Remove the budget requirement"

R5=$(curl -sf -X POST "${BASE_URL}/chat" \
  -H "Content-Type: application/json" \
  -d "$(jq -n \
    --arg msg "Actually, remove the budget constraint." \
    --argjson pois "$R4_POIS" \
    --argjson reqs "$R4_REQS" \
    --argjson plan "$R4_PLAN" \
    '{message: $msg, pois: $pois, requirements: $reqs, plan: $plan}'
  )")

echo "$R5" | jq .

R5_REQS=$(echo "$R5" | jq -c '.requirements')

pass "Round 5 complete — requirements remaining: $(echo "$R5_REQS" | jq 'length')"

log "All rounds finished"
