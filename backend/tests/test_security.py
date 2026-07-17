from __future__ import annotations

import pytest

from app.security.hashing import hash_secret, verify_secret
from app.security.tokens import (
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
)


def test_hash_and_verify() -> None:
    h = hash_secret("s3cret-pass")
    assert h != "s3cret-pass"
    assert verify_secret("s3cret-pass", h)
    assert not verify_secret("wrong", h)
    assert not verify_secret("x", None)


def test_access_token_roundtrip() -> None:
    token = create_access_token("user-1", "parent")
    payload = decode_token(token, expected_type="access")
    assert payload["sub"] == "user-1"
    assert payload["role"] == "parent"
    assert payload["type"] == "access"


def test_refresh_token_has_jti_and_type() -> None:
    token, jti, ttl = create_refresh_token("user-1", "parent")
    assert ttl > 0
    payload = decode_token(token, expected_type="refresh")
    assert payload["jti"] == jti
    assert payload["type"] == "refresh"


def test_wrong_type_rejected() -> None:
    access = create_access_token("u", "parent")
    with pytest.raises(TokenError):
        decode_token(access, expected_type="refresh")


def test_tampered_token_rejected() -> None:
    with pytest.raises(TokenError):
        decode_token("not.a.jwt", expected_type="access")
