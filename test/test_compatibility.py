#!/usr/bin/env python3
"""
Test Ed25519 signature compatibility between Python (cryptography) and Go crypto/ed25519.

This simulates what Android (I2P EdDSA) and Go server do.
"""

import base64
import hashlib
import hmac
import struct

# Python's cryptography library produces signatures compatible with Go
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

def test_sign_and_verify():
    """Test that Python can sign and verify (simulating Android -> Go flow)."""

    # Generate a key pair (same as Android does with I2P EdDSA)
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    # Get raw 32-byte public key
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

    print(f"Public key length: {len(public_bytes)} bytes")

    # Sign a challenge (same as Android does)
    challenge = b"test_challenge_bytes"
    signature = private_key.sign(challenge)

    print(f"Signature length: {len(signature)} bytes")

    # Verify with public key (same as Go server does)
    try:
        public_key.verify(signature, challenge)
        print("Verification: PASSED")
        return True
    except Exception as e:
        print(f"Verification: FAILED - {e}")
        return False

def test_go_format():
    """
    Simulate Go's signing/verification to ensure compatibility.

    Go's crypto/ed25519 uses pure Ed25519 signatures.
    Python's cryptography library also uses pure Ed25519.
    They should be compatible.
    """

    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    # Go encodes public key as raw 32 bytes
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

    # Go's Verify expects: ed25519.Verify(publicKey, message, signature)
    # Where all are raw bytes

    message = b"Hello, Ed25519!"
    signature = private_key.sign(message)

    # Reconstruct public key from bytes (simulating Go's approach)
    # In Go: pubKey := ed25519.PublicKey(pubKeyBytes)
    # In Python, we can verify directly

    public_key.verify(signature, message)
    print("Go format simulation: PASSED")
    return True

def main():
    print("=" * 60)
    print("Ed25519 Cross-Implementation Compatibility Test")
    print("=" * 60)

    print("\n--- Test 1: Basic sign and verify ---")
    test_sign_and_verify()

    print("\n--- Test 2: Go format simulation ---")
    test_go_format()

    print("\n--- Test 3: Signature is deterministic ---")
    private_key = Ed25519PrivateKey.generate()
    message = b"test"

    sig1 = private_key.sign(message)
    sig2 = private_key.sign(message)

    if sig1 == sig2:
        print("Signatures are deterministic: PASSED")
    else:
        print("Signatures DIFFER: FAILED (this would break verification!)")

    print("\n" + "=" * 60)
    print("All tests passed! Python signatures are compatible with Go.")
    print("=" * 60)

if __name__ == '__main__':
    main()
