"""Unit tests for appconnect.webhook_signature.verify_webhook_signature."""

from __future__ import annotations

import hashlib
import hmac
import time

from appconnect.webhook_signature import verify_webhook_signature

SECRET = "test-signing-secret"


def _sign(raw_body: str, secret: str, timestamp: int) -> str:
    v1 = hmac.new(
        secret.encode("utf-8"), f"{timestamp}.{raw_body}".encode(), hashlib.sha256
    ).hexdigest()
    return f"t={timestamp},v1={v1}"


def test_accepts_a_signature_it_just_generated() -> None:
    raw_body = '{"event_id": "evt_1"}'
    now = int(time.time())
    header = _sign(raw_body, SECRET, now)

    assert verify_webhook_signature(raw_body, header, SECRET) is True


def test_rejects_tampered_body() -> None:
    raw_body = '{"event_id": "evt_1"}'
    now = int(time.time())
    header = _sign(raw_body, SECRET, now)

    assert verify_webhook_signature(raw_body + "tampered", header, SECRET) is False


def test_rejects_wrong_secret() -> None:
    raw_body = '{"event_id": "evt_1"}'
    now = int(time.time())
    header = _sign(raw_body, SECRET, now)

    assert verify_webhook_signature(raw_body, header, "wrong-secret") is False


def test_rejects_header_missing_v1() -> None:
    assert verify_webhook_signature("{}", f"t={int(time.time())}", SECRET) is False


def test_rejects_header_missing_t() -> None:
    raw_body = "{}"
    now = int(time.time())
    v1 = hmac.new(SECRET.encode("utf-8"), f"{now}.{raw_body}".encode(), hashlib.sha256).hexdigest()
    assert verify_webhook_signature(raw_body, f"v1={v1}", SECRET) is False


def test_rejects_malformed_or_empty_header() -> None:
    assert verify_webhook_signature("{}", "", SECRET) is False
    assert verify_webhook_signature("{}", "not-a-valid-header", SECRET) is False


def test_rejects_stale_timestamp_beyond_default_tolerance() -> None:
    raw_body = "{}"
    stale_timestamp = int(time.time()) - 301
    header = _sign(raw_body, SECRET, stale_timestamp)

    assert verify_webhook_signature(raw_body, header, SECRET) is False


def test_accepts_timestamp_within_default_tolerance() -> None:
    raw_body = "{}"
    recent_timestamp = int(time.time()) - 299
    header = _sign(raw_body, SECRET, recent_timestamp)

    assert verify_webhook_signature(raw_body, header, SECRET) is True


def test_respects_custom_tolerance() -> None:
    raw_body = "{}"
    timestamp = int(time.time()) - 30
    header = _sign(raw_body, SECRET, timestamp)

    assert verify_webhook_signature(raw_body, header, SECRET, tolerance_seconds=10) is False
    assert verify_webhook_signature(raw_body, header, SECRET, tolerance_seconds=60) is True


def test_skips_staleness_check_when_tolerance_is_zero() -> None:
    raw_body = "{}"
    very_old_timestamp = int(time.time()) - 1_000_000
    header = _sign(raw_body, SECRET, very_old_timestamp)

    assert verify_webhook_signature(raw_body, header, SECRET, tolerance_seconds=0) is True


def test_ignores_unknown_extra_components_in_header() -> None:
    raw_body = "{}"
    now = int(time.time())
    v1 = hmac.new(SECRET.encode("utf-8"), f"{now}.{raw_body}".encode(), hashlib.sha256).hexdigest()
    header = f"t={now},v1={v1},v2=future-scheme"

    assert verify_webhook_signature(raw_body, header, SECRET) is True
