"""Unit tests for the pure request-building helpers in appconnect.triggers."""

from __future__ import annotations

from appconnect.triggers import (
    build_list_deliveries_params,
    build_list_trigger_definitions_params,
    build_subscribe_trigger_body,
    build_update_trigger_instance_body,
)


def test_list_trigger_definitions_params_omitted_when_service_is_none() -> None:
    assert build_list_trigger_definitions_params(None) is None


def test_list_trigger_definitions_params_includes_service() -> None:
    assert build_list_trigger_definitions_params("github-oauth") == {"service": "github-oauth"}


def test_subscribe_trigger_body_always_includes_all_fields() -> None:
    body = build_subscribe_trigger_body(
        service="github-oauth",
        trigger="new_commit",
        config={"owner": "octocat", "repo": "hello-world"},
        callback_url="https://partner.example.com/hooks/appconnect",
    )
    assert body == {
        "service": "github-oauth",
        "trigger": "new_commit",
        "config": {"owner": "octocat", "repo": "hello-world"},
        "callback_url": "https://partner.example.com/hooks/appconnect",
    }


def test_subscribe_trigger_body_includes_empty_config_dict() -> None:
    # An explicitly empty config must still be sent as `{}`, not omitted.
    body = build_subscribe_trigger_body(
        service="shopify", trigger="order_created", config={}, callback_url="https://x.example/"
    )
    assert body["config"] == {}


def test_update_trigger_instance_body_omits_all_unset_fields() -> None:
    """Regression-style test mirroring `_create_link_token_body`'s fix:
    unset optional args must not appear in the body at all (not even as
    JSON null), since the server's zod schema treats them as
    optional-absent, not nullable.
    """
    assert build_update_trigger_instance_body(None, None, None) == {}


def test_update_trigger_instance_body_includes_only_supplied_fields() -> None:
    assert build_update_trigger_instance_body("paused", None, None) == {"status": "paused"}
    assert build_update_trigger_instance_body(None, "https://new.example/hook", None) == {
        "callback_url": "https://new.example/hook"
    }
    assert build_update_trigger_instance_body(None, None, {"owner": "octocat"}) == {
        "config": {"owner": "octocat"}
    }


def test_update_trigger_instance_body_includes_all_fields_when_all_supplied() -> None:
    body = build_update_trigger_instance_body(
        "active", "https://new.example/hook", {"owner": "octocat", "repo": "hello-world"}
    )
    assert body == {
        "status": "active",
        "callback_url": "https://new.example/hook",
        "config": {"owner": "octocat", "repo": "hello-world"},
    }


def test_list_deliveries_params_none_when_all_unset() -> None:
    assert build_list_deliveries_params(None, None, None) is None


def test_list_deliveries_params_includes_only_supplied_filters() -> None:
    assert build_list_deliveries_params("failed", None, None) == {"status": "failed"}
    assert build_list_deliveries_params(None, 10, None) == {"limit": "10"}
    assert build_list_deliveries_params(None, None, "2026-01-01T00:00:00Z") == {
        "cursor": "2026-01-01T00:00:00Z"
    }


def test_list_deliveries_params_includes_all_when_all_supplied() -> None:
    params = build_list_deliveries_params("dead_letter", 5, "2026-01-01T00:00:00Z")
    assert params == {"status": "dead_letter", "limit": "5", "cursor": "2026-01-01T00:00:00Z"}
