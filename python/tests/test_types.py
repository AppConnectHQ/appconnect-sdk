"""Unit tests for appconnect.types."""

from __future__ import annotations

from appconnect.types import (
    EXCHANGE_LINK_TOKEN_ADAPTER,
    AppConnectError,
    ConnectedLinkExchangeResponse,
    PendingLinkExchangeResponse,
    Tool,
    ToolExecutionResponse,
)


def test_app_connect_error_defaults() -> None:
    err = AppConnectError("boom")
    assert err.message == "boom"
    assert err.status == 0
    assert err.code is None
    assert str(err) == "boom"


def test_app_connect_error_with_status_and_code() -> None:
    err = AppConnectError("invalid token", status=401, code="invalid_token")
    assert err.status == 401
    assert err.code == "invalid_token"
    assert "invalid token" in repr(err)
    assert "401" in repr(err)


def test_tool_accepts_null_description_and_input_schema() -> None:
    tool = Tool.model_validate(
        {
            "id": "aws_s3_list_buckets",
            "service": "aws",
            "serviceName": "AWS",
            "name": "s3_list_buckets",
            "displayName": "List S3 Buckets",
            "description": None,
            "method": "GET",
            "inputSchema": None,
        }
    )
    assert tool.description is None
    assert tool.inputSchema is None


def test_tool_input_schema_round_trip() -> None:
    tool = Tool.model_validate(
        {
            "id": "google_calendar_list_events",
            "service": "google-calendar",
            "serviceName": "Google Calendar",
            "name": "list_events",
            "displayName": "List Events",
            "description": "List calendar events",
            "method": "GET",
            "inputSchema": {
                "type": "object",
                "properties": {"calendarId": {"type": "string"}},
                "required": ["calendarId"],
            },
        }
    )
    assert tool.inputSchema is not None
    assert tool.inputSchema.required == ["calendarId"]
    assert tool.inputSchema.properties is not None
    assert tool.inputSchema.properties["calendarId"] == {"type": "string"}


def test_exchange_link_token_adapter_discriminates_pending() -> None:
    result = EXCHANGE_LINK_TOKEN_ADAPTER.validate_python(
        {"status": "pending", "user_id": "user_1", "state": None, "message": "waiting"}
    )
    assert isinstance(result, PendingLinkExchangeResponse)
    assert result.user_id == "user_1"


def test_exchange_link_token_adapter_discriminates_connected() -> None:
    result = EXCHANGE_LINK_TOKEN_ADAPTER.validate_python(
        {
            "status": "connected",
            "user_id": "user_1",
            "state": "xyz",
            "access_token": "apphq_abc",
            "refresh_token": "apphq_refresh_abc",
            "token_type": "Bearer",
            "expires_at": "2026-01-01T00:00:00Z",
            "connected_services": ["google-calendar"],
        }
    )
    assert isinstance(result, ConnectedLinkExchangeResponse)
    assert result.connected_services == ["google-calendar"]


def test_tool_execution_response_allows_arbitrary_data() -> None:
    resp = ToolExecutionResponse.model_validate(
        {"tool": "github_oauth_list_repos", "data": {"items": [1, 2, 3]}}
    )
    assert resp.tool == "github_oauth_list_repos"
    assert resp.data == {"items": [1, 2, 3]}
