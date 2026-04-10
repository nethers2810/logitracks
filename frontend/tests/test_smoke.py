from pathlib import Path


def test_frontend_contains_login_and_logout_controls():
    html = Path("frontend/index.html").read_text()
    assert 'id="login-form"' in html
    assert 'id="logout-btn"' in html
    assert "Current user:" in html
