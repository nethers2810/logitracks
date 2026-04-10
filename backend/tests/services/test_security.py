from app.core.security import create_access_token, decode_token, hash_password, verify_password


def test_password_hash_roundtrip():
    hashed = hash_password("secret123")
    assert hashed != "secret123"
    assert verify_password("secret123", hashed)


def test_token_contains_subject_and_role():
    token = create_access_token(subject="planner@logitracks.local", role="planner", expires_minutes=30)
    payload = decode_token(token)
    assert payload["sub"] == "planner@logitracks.local"
    assert payload["role"] == "planner"
