"""
Tests for Flask routes in app.py.
Uses the `flask_client` fixture from conftest.py, which mocks out the
Anthropic API, Facebook HTTP calls, and store persistence.
"""

import json
import pytest


class TestHome:
    def test_get_home_returns_200(self, flask_client):
        resp = flask_client.get("/")
        assert resp.status_code == 200

    def test_get_home_body_mentions_chatbot(self, flask_client):
        resp = flask_client.get("/")
        assert b"dang chay" in resp.data or b"Chatbot" in resp.data


class TestWebhookVerification:
    def test_valid_token_returns_challenge(self, flask_client):
        resp = flask_client.get(
            "/webhook",
            query_string={
                "hub.mode": "subscribe",
                "hub.verify_token": "test-verify-token",
                "hub.challenge": "CHALLENGE_STRING",
            },
        )
        assert resp.status_code == 200
        assert b"CHALLENGE_STRING" in resp.data

    def test_wrong_token_returns_403(self, flask_client):
        resp = flask_client.get(
            "/webhook",
            query_string={
                "hub.mode": "subscribe",
                "hub.verify_token": "wrong-token",
                "hub.challenge": "CHALLENGE_STRING",
            },
        )
        assert resp.status_code == 403

    def test_wrong_mode_returns_403(self, flask_client):
        resp = flask_client.get(
            "/webhook",
            query_string={
                "hub.mode": "unsubscribe",
                "hub.verify_token": "test-verify-token",
                "hub.challenge": "CHALLENGE_STRING",
            },
        )
        assert resp.status_code == 403


class TestWebhookPost:
    def _post(self, flask_client, payload: dict):
        return flask_client.post(
            "/webhook",
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_non_page_object_returns_ok(self, flask_client):
        resp = self._post(flask_client, {"object": "user", "entry": []})
        assert resp.status_code == 200
        assert resp.data == b"ok"

    def test_page_object_with_no_entries_returns_ok(self, flask_client):
        resp = self._post(flask_client, {"object": "page", "entry": []})
        assert resp.status_code == 200

    def test_messenger_event_handled(self, flask_client, mocker):
        mock_xu_ly = mocker.patch("app.xu_ly_messenger")
        payload = {
            "object": "page",
            "entry": [{
                "id": "page123",
                "messaging": [{
                    "sender": {"id": "user123"},
                    "message": {"text": "xin chào"},
                }],
                "changes": [],
            }],
        }
        resp = self._post(flask_client, payload)
        assert resp.status_code == 200
        mock_xu_ly.assert_called_once()

    def test_feed_change_event_handled(self, flask_client, mocker):
        mock_xu_ly = mocker.patch("app.xu_ly_comment")
        payload = {
            "object": "page",
            "entry": [{
                "id": "page123",
                "messaging": [],
                "changes": [{
                    "field": "feed",
                    "value": {"item": "comment", "verb": "add",
                               "message": "hỏi giá", "comment_id": "c1",
                               "from": {"id": "user999", "name": "Khách"}, "post_id": "p1"},
                }],
            }],
        }
        resp = self._post(flask_client, payload)
        assert resp.status_code == 200
        mock_xu_ly.assert_called_once()


class TestRunTheoDuoi:
    def test_wrong_key_returns_403(self, flask_client):
        resp = flask_client.get("/run-theo-duoi?key=wrong")
        assert resp.status_code == 403

    def test_correct_key_returns_200(self, flask_client, mocker):
        mocker.patch("theo_duoi.chay")
        resp = flask_client.get("/run-theo-duoi?key=test-verify-token")
        assert resp.status_code == 200
