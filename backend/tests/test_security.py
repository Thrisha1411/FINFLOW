from backend.app.core.security import create_access_token, decode_token, get_password_hash, verify_password


def test_password_hash_roundtrip():
    hashed = get_password_hash("ChangeMe12345!")
    assert hashed != "ChangeMe12345!"
    assert verify_password("ChangeMe12345!", hashed)
    assert not verify_password("WrongPassword!", hashed)


def test_jwt_roundtrip():
    token = create_access_token(
        subject="u1",
        claims={"email": "ops@example.com", "organization_id": "acme", "roles": ["Admin"]}
    )
    principal = decode_token(token)
    assert principal is not None
    assert principal["sub"] == "u1"
    assert principal["organization_id"] == "acme"
    assert principal["roles"] == ["Admin"]
