"""Unit tests for appconnect.config."""

from __future__ import annotations

import pytest

from appconnect.config import resolve_config
from appconnect.types import AppConnectError


def test_constructor_args_take_priority(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPCONNECT_BASE_URL", "https://env.example.com")
    monkeypatch.setenv("APPCONNECT_CLIENT_ID", "env_client")
    monkeypatch.setenv("APPCONNECT_CLIENT_SECRET", "env_secret")

    config = resolve_config(
        base_url="https://ctor.example.com",
        client_id="ctor_client",
        client_secret="ctor_secret",
    )

    assert config.base_url == "https://ctor.example.com"
    assert config.client_id == "ctor_client"
    assert config.client_secret == "ctor_secret"


def test_falls_back_to_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPCONNECT_BASE_URL", "https://env.example.com")
    monkeypatch.setenv("APPCONNECT_CLIENT_ID", "env_client")
    monkeypatch.setenv("APPCONNECT_CLIENT_SECRET", "env_secret")

    config = resolve_config()

    assert config.base_url == "https://env.example.com"
    assert config.client_id == "env_client"
    assert config.client_secret == "env_secret"


def test_strips_trailing_slash_from_base_url() -> None:
    config = resolve_config(
        base_url="https://api.example.com/",
        client_id="client",
        client_secret="secret",
    )
    assert config.base_url == "https://api.example.com"


def test_raises_app_connect_error_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPCONNECT_BASE_URL", raising=False)
    monkeypatch.delenv("APPCONNECT_CLIENT_ID", raising=False)
    monkeypatch.delenv("APPCONNECT_CLIENT_SECRET", raising=False)

    with pytest.raises(AppConnectError) as exc_info:
        resolve_config()

    assert exc_info.value.status == 0
    assert exc_info.value.code == "config_error"
    assert "base_url" in exc_info.value.message
    assert "client_id" in exc_info.value.message
    assert "client_secret" in exc_info.value.message


def test_partial_env_reports_only_missing_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPCONNECT_BASE_URL", "https://env.example.com")
    monkeypatch.delenv("APPCONNECT_CLIENT_ID", raising=False)
    monkeypatch.delenv("APPCONNECT_CLIENT_SECRET", raising=False)

    with pytest.raises(AppConnectError) as exc_info:
        resolve_config(client_id="ctor_client")

    assert "client_secret" in exc_info.value.message
    assert "base_url" not in exc_info.value.message
    assert "client_id" not in exc_info.value.message
