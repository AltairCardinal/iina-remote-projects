#!/bin/bash
#
# IINA Remote Pairing Test
# Usage: ./PairingTest.sh -h <host> -p <port> -c <code>
#

HOST="192.168.1.100"
PORT=8765
CODE="123456"
DEVICE_NAME="Test-Device"

while getopts "h:p:c:n:" opt; do
    case $opt in
        h) HOST="$OPTARG";;
        p) PORT="$OPTARG";;
        c) CODE="$OPTARG";;
        n) DEVICE_NAME="$OPTARG";;
        \?) echo "Usage: $0 -h <host> -p <port> -c <code> -n <name>"; exit 1;;
    esac
done

echo "=== IINA Remote Pairing Test ==="
echo "Host: $HOST:$PORT"
echo "Code: $CODE"
echo "Name: $DEVICE_NAME"
echo

# Generate random device ID
DEVICE_ID=$(uuidgen 2>/dev/null || cat /proc/sys/kernel/random/uuid 2>/dev/null || echo "device-$(date +%s)")
echo "[LOG] Device ID: $DEVICE_ID"

# Test if server is reachable
echo
echo "[LOG] Testing connection to server..."
if ! nc -z -w5 "$HOST" "$PORT" 2>/dev/null; then
    echo "[ERROR] Cannot connect to $HOST:$PORT"
    exit 1
fi
echo "[LOG] Server is reachable"

# Step 1: Get challenge
echo
echo "[LOG] Step 1: Getting pair challenge..."
CHALLENGE_RESP=$(curl -s -w "\n%{http_code}" "http://$HOST:$PORT/api/v1/pair/challenge")
CHALLENGE_BODY=$(echo "$CHALLENGE_RESP" | head -n -1)
CHALLENGE_CODE=$(echo "$CHALLENGE_RESP" | tail -n 1)
echo "[LOG] Challenge response code: $CHALLENGE_CODE"
echo "[LOG] Challenge body: $CHALLENGE_BODY"

# For now, just generate a dummy key pair for testing
# In real scenario, this would be Ed25519 from AndroidKeyStore
echo
echo "[LOG] Step 2: Would generate Ed25519 key pair (skipped for curl test)"

# Step 3: Submit pair request
echo
echo "[LOG] Step 3: Submitting pair request..."
echo "[LOG] Request body:"
cat <<EOF
{
    "code": "$CODE",
    "device_id": "$DEVICE_ID",
    "device_name": "$DEVICE_NAME",
    "public_key": "dummy-public-key-for-testing"
}
EOF

PAIR_RESP=$(curl -s -w "\n%{http_code}" -X POST "http://$HOST:$PORT/api/v1/pair" \
    -H "Content-Type: application/json" \
    -d "{\"code\": \"$CODE\", \"device_id\": \"$DEVICE_ID\", \"device_name\": \"$DEVICE_NAME\", \"public_key\": \"dummy\"}")
PAIR_BODY=$(echo "$PAIR_RESP" | head -n -1)
PAIR_CODE=$(echo "$PAIR_RESP" | tail -n 1)

echo "[LOG] Pair response code: $PAIR_CODE"
echo "[LOG] Pair response body: $PAIR_BODY"

if [ "$PAIR_CODE" = "200" ]; then
    echo
    echo "=== PAIRING RESPONSE ==="
    echo "$PAIR_BODY" | python3 -m json.tool 2>/dev/null || echo "$PAIR_BODY"
else
    echo
    echo "=== PAIRING FAILED ==="
fi
