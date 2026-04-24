#!/usr/bin/env python3
"""
Android Pairing Simulator — tests the complete pairing flow with the IINA Remote server.

This script replicates the Android app's Ed25519 key generation and pairing logic,
allowing testing without a physical Android device.

Usage:
    python3 test_android_pairing.py [--host HOST] [--port PORT]

Requirements:
    pip install cryptography requests
"""

import argparse
import base64
import json
import os
import sys
import uuid
from pathlib import Path

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
except ImportError:
    print("Error: cryptography package not installed")
    print("Run: pip install cryptography requests")
    sys.exit(1)

import requests


class Ed25519KeyPair:
    """Replicates KeyStoreManager's key handling using I2P EdDSA compatible format."""

    def __init__(self, private_bytes: bytes, public_bytes: bytes):
        self.private_bytes = private_bytes  # 32-byte seed
        self.public_bytes = public_bytes    # 32-byte public key

    @classmethod
    def generate(cls) -> "Ed25519KeyPair":
        """Generate a new Ed25519 key pair (same format as I2P EdDSA)."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        # Get raw 32-byte seeds (same as I2P EdDSA's getSeed() and getAbyte())
        private_bytes = private_key.private_bytes_raw()
        public_bytes = public_key.public_bytes_raw()

        return cls(private_bytes, public_bytes)

    def public_key_base64(self) -> str:
        """Returns base64-encoded public key (NO_WRAP, matching Android's Base64.NO_WRAP)."""
        return base64.b64encode(self.public_bytes).decode('ascii')

    def sign(self, data: bytes) -> bytes:
        """Sign data with Ed25519 (raw signature, same as I2P EdDSA)."""
        # Reconstruct the private key from raw bytes for signing
        # Using cryptography's Ed25519PrivateKey directly
        private_key = Ed25519PrivateKey.from_private_bytes(self.private_bytes)
        return private_key.sign(data)


class AndroidPairingSimulator:
    """
    Simulates the Android app's pairing flow with the IINA Remote server.

    Replicates:
    - KeyStoreManager: Ed25519 key generation and signing
    - PairingViewModel: Complete pairing and reconnect flow
    - ConnectionStore: Device ID persistence
    """

    def __init__(self, host: str = "localhost", port: int = 8765, pair_port: int = 8766):
        self.host = host
        self.port = port
        self.pair_port = pair_port
        self.base_url = f"http://{host}:{port}/api/v1"
        self.device_id = str(uuid.uuid4())
        self.key_pair: Ed25519KeyPair | None = None
        self.auth_token: str | None = None
        self.server_name: str | None = None
        self.paired_servers: list[dict] = []

    def _get_pair_code(self) -> str:
        """Get the current 6-character pair code from the server (from Mac screen)."""
        resp = requests.get(f"http://localhost:{self.pair_port}/api/v1/pair/code", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return data["code"]

    def _ensure_key_pair(self):
        """Ensure we have an Ed25519 key pair (same logic as KeyStoreManager.hasKeyPair)."""
        if self.key_pair is None:
            self.key_pair = Ed25519KeyPair.generate()

    def pair_with_code(self, pair_code: str, device_name: str = "Android Simulator") -> dict:
        """
        Complete initial pairing flow.

        Steps:
        1. Ensure Ed25519 key pair exists
        2. POST /api/v1/pair with code + device_id + device_name + public_key
        3. Save token and server_name

        Returns the PairResponse dict.
        """
        self._ensure_key_pair()

        payload = {
            "code": pair_code,
            "device_id": self.device_id,
            "device_name": device_name,
            "public_key": self.key_pair.public_key_base64()
        }

        resp = requests.post(f"{self.base_url}/pair", json=payload, timeout=10)
        resp.raise_for_status()

        data = resp.json()
        self.auth_token = data.get("token")
        self.server_name = data.get("server_name")

        # Save to paired servers (same as ConnectionStore.addPairedServer)
        paired_info = {
            "device_id": self.device_id,
            "server_name": self.server_name,
            "host": self.host,
            "port": self.port
        }

        # Update or add
        for i, s in enumerate(self.paired_servers):
            if s["host"] == self.host and s["port"] == self.port:
                self.paired_servers[i] = paired_info
                break
        else:
            self.paired_servers.append(paired_info)

        return data

    def auto_pair(self, device_name: str = "Android Simulator") -> dict:
        """
        Automatic pairing: fetch pair code and submit in one step.
        """
        pair_code = self._get_pair_code()
        print(f"  Got pair code: {pair_code}")
        return self.pair_with_code(pair_code, device_name)

    def reconnect(self) -> dict:
        """
        Reconnect flow (challenge-response).

        Steps:
        1. POST /api/v1/pair/challenge/generate with device_id
        2. Decode challenge from base64
        3. Sign the raw challenge bytes with Ed25519 private key
        4. POST /api/v1/pair/reconnect with device_id + challenge + signature
        5. Save new token

        Returns the ReconnectResponse dict.
        """
        if self.key_pair is None:
            raise RuntimeError("No key pair available. Must pair first.")

        # Step 1: Get challenge
        resp = requests.post(
            f"{self.base_url}/pair/challenge/generate",
            json={"device_id": self.device_id},
            timeout=10
        )
        resp.raise_for_status()
        challenge = resp.json()["challenge"]

        # Step 2: Decode challenge from base64 (same as Android's Base64.decode)
        challenge_bytes = base64.b64decode(challenge)

        # Step 3: Sign the raw challenge bytes
        signature = self.key_pair.sign(challenge_bytes)
        signature_b64 = base64.b64encode(signature).decode('ascii')

        # Step 4: Reconnect
        resp = requests.post(
            f"{self.base_url}/pair/reconnect",
            json={
                "device_id": self.device_id,
                "challenge": challenge,
                "signature": signature_b64,
                "device_name": self.server_name or "Android Simulator"
            },
            timeout=10
        )
        resp.raise_for_status()

        data = resp.json()
        if data.get("token"):
            self.auth_token = data["token"]
        if data.get("server_name"):
            self.server_name = data["server_name"]

        return data

    def get_status(self) -> dict:
        """Get IINA playback status (requires auth token)."""
        if not self.auth_token:
            raise RuntimeError("Not authenticated. Must pair first.")

        resp = requests.get(
            f"{self.base_url}/status",
            headers={"Authorization": f"Bearer {self.auth_token}"},
            timeout=10
        )
        resp.raise_for_status()
        return resp.json()

    def revoke(self) -> None:
        """Revoke this device (requires auth token)."""
        if not self.auth_token:
            raise RuntimeError("Not authenticated. Must pair first.")

        resp = requests.delete(
            f"{self.base_url}/devices/{self.auth_token}",
            headers={"Authorization": f"Bearer {self.auth_token}"},
            timeout=10
        )
        # 204 No Content is expected
        if resp.status_code != 204:
            print(f"  Warning: revoke returned {resp.status_code}: {resp.text}")


def main():
    parser = argparse.ArgumentParser(description="Android Pairing Simulator")
    parser.add_argument("--host", default="localhost", help="Server host (default: localhost)")
    parser.add_argument("--port", type=int, default=8765, help="Server port (default: 8765)")
    parser.add_argument("--pair-port", type=int, default=8766, help="Pair code port (default: 8766)")
    parser.add_argument("--name", default="Android Simulator", help="Device name")
    parser.add_argument("--reconnect-only", action="store_true", help="Skip pairing, try reconnect with existing keys")
    parser.add_argument("--revoke", action="store_true", help="Revoke this device after pairing")
    args = parser.parse_args()

    sim = AndroidPairingSimulator(host=args.host, port=args.port, pair_port=args.pair_port)

    print("=" * 60)
    print("Android Pairing Simulator")
    print("=" * 60)
    print(f"  Host: {args.host}:{args.port}")
    print(f"  Device ID: {sim.device_id}")
    print()

    if args.reconnect_only:
        print("[1] Testing reconnection (skipping pair)...")
        try:
            result = sim.reconnect()
            print(f"  Reconnect SUCCESS: server_name={result.get('server_name')}")
            print(f"  Token: {result.get('token', 'none')[:30]}...")
        except Exception as e:
            print(f"  Reconnect FAILED: {e}")
            sys.exit(1)
        return

    print("[1] Generating Ed25519 key pair...")
    sim._ensure_key_pair()
    print(f"  Public key: {sim.key_pair.public_key_base64()[:30]}... (32 bytes)")

    print("[2] Fetching pair code from server...")
    try:
        pair_code = sim._get_pair_code()
        print(f"  Pair code: {pair_code}")
    except Exception as e:
        print(f"  Failed to get pair code: {e}")
        print("  (Is the server running? Is the pair port correct?)")
        sys.exit(1)

    print("[3] Submitting pair request...")
    try:
        result = sim.pair_with_code(pair_code, args.name)
        print(f"  Pair SUCCESS!")
        print(f"  Server name: {result.get('server_name')}")
        print(f"  Token: {result.get('token', 'none')[:30]}...")
        print(f"  Expires in: {result.get('expires_in')} seconds")
    except Exception as e:
        print(f"  Pair FAILED: {e}")
        sys.exit(1)

    print("[4] Testing reconnection...")
    try:
        result = sim.reconnect()
        print(f"  Reconnect SUCCESS: server_name={result.get('server_name')}")
    except Exception as e:
        print(f"  Reconnect FAILED: {e}")
        sys.exit(1)

    print()
    print("=" * 60)
    print("All tests passed!")
    print("=" * 60)

    if args.revoke:
        print(f"\n[5] Revoking device...")
        sim.revoke()
        print("  Revoked successfully.")


if __name__ == "__main__":
    main()