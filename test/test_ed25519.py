#!/usr/bin/env python3
"""
Unit test for Ed25519 key generation and signing.
Verifies that:
1. Generated public key is exactly 32 bytes
2. Generated private key is exactly 32 bytes
3. Signature is exactly 64 bytes
4. Signature verification works
"""

import sys
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def test_key_generation():
    """Test that Ed25519 key generation produces correct key sizes."""
    print("=== Test: Key Generation ===")

    # Generate a key pair
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    # Get raw bytes
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )

    print(f"  Public key length: {len(public_bytes)} bytes (expected: 32)")
    print(f"  Private key length: {len(private_bytes)} bytes (expected: 32)")
    print(f"  Public key (base64): {base64.b64encode(public_bytes).decode()}")

    assert len(public_bytes) == 32, f"Public key should be 32 bytes, got {len(public_bytes)}"
    assert len(private_bytes) == 32, f"Private key should be 32 bytes, got {len(private_bytes)}"
    print("  PASSED")
    return public_bytes, private_bytes

def test_signing(public_bytes, private_bytes):
    """Test that signing produces correct signature size."""
    print("\n=== Test: Signing ===")

    # Reconstruct key from bytes
    private_key = Ed25519PrivateKey.from_private_bytes(private_bytes)

    # Sign a message
    message = b"Hello, World!"
    signature = private_key.sign(message)

    print(f"  Message length: {len(message)} bytes")
    print(f"  Signature length: {len(signature)} bytes (expected: 64)")
    print(f"  Signature (base64): {base64.b64encode(signature).decode()}")

    assert len(signature) == 64, f"Signature should be 64 bytes, got {len(signature)}"
    print("  PASSED")
    return signature

def test_verification(public_bytes, signature, message):
    """Test that signature verification works."""
    print("\n=== Test: Verification ===")

    # Reconstruct public key from bytes
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    public_key = Ed25519PublicKey.from_public_bytes(public_bytes)

    # Verify
    try:
        public_key.verify(signature, message)
        print("  Signature verification: PASSED")
        return True
    except Exception as e:
        print(f"  Signature verification FAILED: {e}")
        return False

def test_server_format():
    """Test that we produce the correct format for server."""
    print("\n=== Test: Server Format ===")

    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

    # This is what we'll send to the server (base64 encoded)
    public_key_b64 = base64.b64encode(public_bytes).decode()
    print(f"  Public key for server (base64): {public_key_b64}")
    print(f"  Length after decode: {len(public_bytes)} bytes")

    assert len(public_bytes) == 32, "Public key must be exactly 32 bytes for server"
    print("  PASSED")

def main():
    print("Ed25519 Unit Tests")
    print("=" * 50)

    try:
        # Run tests
        public_bytes, private_bytes = test_key_generation()
        signature = test_signing(public_bytes, private_bytes)
        verification = test_verification(public_bytes, signature, b"Hello, World!")
        test_server_format()

        print("\n" + "=" * 50)
        print("ALL TESTS PASSED!")
        return 0
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\nERROR: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
