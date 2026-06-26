"""
Shared pytest fixtures for the nhung-huou-chatbot test suite.
"""

import os
import pytest

# Set a dummy API key before any module that imports Anthropic is loaded.
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")
os.environ.setdefault("PAGE_ACCESS_TOKEN", "test-page-token")
os.environ.setdefault("VERIFY_TOKEN", "test-verify-token")


@pytest.fixture(autouse=True)
def isolate_store(tmp_path, monkeypatch):
    """Redirect store.FILE_DATA to a temp file so tests never touch the real data file."""
    import store
    monkeypatch.setattr(store, "FILE_DATA", tmp_path / "khach_data.json")
    yield


@pytest.fixture()
def flask_client(monkeypatch):
    """Flask test client with Claude API and Facebook HTTP calls mocked out."""
    # Prevent Anthropic client from making real calls
    import claude_bot
    monkeypatch.setattr(claude_bot, "_goi_claude", lambda system, messages, max_tokens=350: "mocked reply")

    # Prevent requests.post (Facebook Send API) from making real calls
    import requests
    monkeypatch.setattr(requests, "post", lambda *a, **kw: _MockResponse(200))

    import app as flask_app
    flask_app.app.config["TESTING"] = True
    with flask_app.app.test_client() as client:
        yield client


class _MockResponse:
    def __init__(self, status_code: int, text: str = "ok"):
        self.status_code = status_code
        self.text = text
