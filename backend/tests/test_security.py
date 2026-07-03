from finflow.security import create_access_token, decode_token, hash_password, verify_password


def test_password_hash_roundtrip():
    hashed = hash_password("ChangeMe12345!")
    assert hashed != "ChangeMe12345!"
    assert verify_password("ChangeMe12345!", hashed)


def test_jwt_roundtrip(monkeypatch):
    token = create_access_token("u1", "ops@example.com", ["Admin"], "acme")
    principal = decode_token(token)
    assert principal.sub == "u1"
    assert principal.organization_id == "acme"
    assert principal.roles == ["Admin"]

