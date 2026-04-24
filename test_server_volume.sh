#!/bin/bash
#
# Test: Volume flashback bug - simplified without jq
#

SERVER="${1:-http://localhost:8765}"
echo "Testing against: $SERVER"
echo "================================"

# Function to extract volume from JSON (without jq)
extract_volume() {
    echo "$1" | grep -o '"volume":[0-9]*' | grep -o '[0-9]*'
}

# 1. Get initial volume
echo "Step 1: Get initial volume..."
INITIAL_RESP=$(curl -s "$SERVER/api/v1/status")
INITIAL=$(extract_volume "$INITIAL_RESP")
echo "  Response: $INITIAL_RESP"
echo "  Initial volume: $INITIAL"

# 2. Set volume to 50
echo ""
echo "Step 2: Set volume to 50..."
SET_RESP=$(curl -s -X POST "$SERVER/api/v1/playback/volume" \
  -H "Content-Type: application/json" \
  -d '{"volume": 0.5}')
echo "  Response: $SET_RESP"

# 3. IMMEDIATELY get status (within 100ms)
echo ""
echo "Step 3: Get status IMMEDIATELY after set..."
sleep 0.1
IMMEDIATE_RESP=$(curl -s "$SERVER/api/v1/status")
IMMEDIATE=$(extract_volume "$IMMEDIATE_RESP")
echo "  Response: $IMMEDIATE_RESP"
echo "  Volume immediately after set: $IMMEDIATE"

# 4. Wait 3 seconds for mpv to process
echo ""
echo "Step 4: Wait 3 seconds for mpv to process..."
sleep 3

# 5. Get status again
echo ""
echo "Step 5: Get status after mpv processing..."
AFTER_RESP=$(curl -s "$SERVER/api/v1/status")
AFTER=$(extract_volume "$AFTER_RESP")
echo "  Response: $AFTER_RESP"
echo "  Volume after wait: $AFTER"

echo ""
echo "================================"
echo "RESULTS:"
echo "  Initial:      $INITIAL"
echo "  Immediate:    $IMMEDIATE"
echo "  After wait:   $AFTER"
echo ""

# Check if there's a flashback (immediate shows old value)
if [ -n "$IMMEDIATE" ] && [ -n "$AFTER" ] && [ "$IMMEDIATE" != "$AFTER" ]; then
  echo "SERVER ISSUE DETECTED:"
  echo "  Server returned $IMMEDIATE immediately, but $AFTER after mpv processed"
  echo "  This indicates mpv has a delay before reporting new volume"
elif [ "$IMMEDIATE" = "$AFTER" ]; then
  echo "Server behaves consistently"
fi

# The real test: does immediate match what we set?
if [ "$IMMEDIATE" = "50" ]; then
  echo "PASS: Server returned new volume (50) immediately"
elif [ -n "$IMMEDIATE" ]; then
  echo "FAIL: Server returned $IMMEDIATE instead of 50 immediately"
  echo "  This explains why Android client sees flashback - server has stale volume"
else
  echo "Could not determine volume from response"
fi