#!/usr/bin/env python3
"""
IINA Remote Pairing Test
Tests the complete pairing flow with Ed25519 keys.

Usage:
    python3 PairingTest.py -h <host> -p <port> -c <code> [-n <name>]
"""

import argparse
import base64
import json
import sys
import urllib.request
import urllib.error
import uuid

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False
    print("[ERROR] cryptography library required: pip install cryptography")
    sys.exit(1)

def log(msg):
    print(f"[LOG] {msg}")

def error(msg):
    print(f"[ERROR] {msg}")

def http_get(host, port, path):
    url = f"http://{host}:{port}{path}"
    log(f"GET {url}")
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            body = resp.read().decode('utf-8')
            log(f"  -> HTTP {resp.status}")
            return body
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8') if e.fp else ""
        log(f"  -> HTTP {e.code} {e.reason}")
        if body:
            log(f"     Body: {body[:200]}")
        return None
    except Exception as e:
        error(f"  -> {e}")
        return None

def http_post(host, port, path, data):
    url = f"http://{host}:{port}{path}"
    log(f"POST {url}")
    try:
        req = urllib.request.Request(url,
            data=data.encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST')
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode('utf-8')
            log(f"  -> HTTP {resp.status}")
            return body
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8') if e.fp else ""
        log(f"  -> HTTP {e.code} {e.reason}")
        if body:
            log(f"     Body: {body[:500]}")
        return None
    except Exception as e:
        error(f"  -> {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='IINA Remote Pairing Test')
    parser.add_argument('--host', '-H', default='localhost', help='Server host')
    parser.add_argument('--port', '-P', type=int, default=8765, help='Server port')
    parser.add_argument('--code', '-c', required=True, help='Pair code (6 digits)')
    parser.add_argument('--name', '-n', default='TestDevice', help='Device name')
    args = parser.parse_args()

    print("=" * 60)
    print("IINA Remote Pairing Test")
    print("=" * 60)
    log(f"Host: {args.host}:{args.port}")
    log(f"Code: {args.code}")
    log(f"Name: {args.name}")
    print()

    # Step 1: Generate Ed25519 key pair (32-byte raw public key)
    log("Step 1: Generate Ed25519 key pair")
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    # Get raw 32-byte public key (this is what we send to server)
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    public_key_b64 = base64.b64encode(public_bytes).decode()
    log(f"  Public key (32 bytes, base64): {public_key_b64}")
    log(f"  Public key length: {len(public_bytes)} bytes")
    assert len(public_bytes) == 32, f"Public key must be 32 bytes, got {len(public_bytes)}"
    print()

    # Step 2: Generate device ID
    log("Step 2: Generate device ID")
    device_id = str(uuid.uuid4())
    log(f"  Device ID: {device_id}")
    print()

    # Step 3: Get pair challenge
    log("Step 3: Get pair challenge")
    challenge_resp = http_get(args.host, args.port, '/api/v1/pair/challenge')
    if challenge_resp is None:
        error("Failed to get challenge!")
        sys.exit(1)
    log(f"  Response: {challenge_resp}")
    print()

    # Step 4: Submit pair request with public key
    log("Step 4: Submit pair request")

    pair_request = {
        "code": args.code,
        "device_id": device_id,
        "device_name": args.name,
        "public_key": public_key_b64
    }
    request_body = json.dumps(pair_request)
    log(f"  Request body: {request_body}")

    pair_response = http_post(args.host, args.port, '/api/v1/pair', request_body)
    if pair_response is None:
        error("No response from server!")
        sys.exit(1)

    print()
    print("=" * 60)
    print("Response:")
    print(pair_response)
    print("=" * 60)

    # Parse response
    try:
        resp_json = json.loads(pair_response)
        if "token" in resp_json:
            print()
            print("=== PAIRING SUCCESSFUL ===")
            print(f"  Token: {resp_json['token'][:30]}...")
            print(f"  Server Name: {resp_json.get('server_name', 'N/A')}")
            print(f"  Expires In: {resp_json.get('expires_in', 'N/A')} seconds")
        else:
            print()
            print("=== PAIRING FAILED ===")
            print(f"  Response: {pair_response}")
    except json.JSONDecodeError:
        print()
        print("=== PAIRING FAILED (invalid JSON) ===")
        print(f"  Response: {pair_response}")

if __name__ == '__main__':
    main()
