"""Unit tests for appconnect.client, using respx to mock the HTTP transport.

Trigger/webhook method tests live in `test_client_triggers.py`; both files
share fixtures and helpers from `conftest.py`.
"""

from __future__ import annotations

import json

import httpx
import pytest
import respx
from conftest import BASE_URL, _error, _success

from appconnect.client import AppConnectClient, SyncAppConnectClient
from appconnect.types import (
    AppConnectError,
    ConnectedLinkExchangeResponse,
    PendingLinkExchangeResponse,
)

# --- async client -----------------------------------------------------------


@respx.mock
async def test_create_link_token(async_client: AppConnectClient) -> None:
    route = respx.post(f"{BASE_URL}/api/link-tokens").mock(
        return_value=_success(
            {
                "link_token": "lt_abc",
                "link_url": "https://example.invalid/link/lt_abc",
                "expires_at": "2026-01-01T00:00:00Z",
            }
        )
    )

    result = await async_client.create_link_token(
        user_id="user_1",
        redirect_uri="https://partner.example.com/callback",
        state="xyz",
        allowed_services=["google-calendar"],
        expires_in=3600,
    )

    assert result.link_token == "lt_abc"
    sent_body = respx.calls.last.request.content
    assert route.called
    assert b'"client_id":"client_123"' in sent_body
    assert b'"user_id":"user_1"' in sent_body


@respx.mock
async def test_create_link_token_omits_optional_fields_when_unset(
    async_client: AppConnectClient,
) -> None:
    """Regression test: omitted optional args must not be sent as JSON null.

    The server's zod schema treats state/allowed_services/expires_in as
    optional-with-defaults, not nullable, so httpx must drop the keys
    entirely rather than serialize the Python `None` default as `null`.
    """
    route = respx.post(f"{BASE_URL}/api/link-tokens").mock(
        return_value=_success(
            {
                "link_token": "lt_abc",
                "link_url": "https://example.invalid/link/lt_abc",
                "expires_at": "2026-01-01T00:00:00Z",
            }
        )
    )

    result = await async_client.create_link_token(
        user_id="user_1",
        redirect_uri="https://partner.example.com/callback",
    )

    assert result.link_token == "lt_abc"
    assert route.called
    sent_json = json.loads(respx.calls.last.request.content)
    assert "state" not in sent_json
    assert "allowed_services" not in sent_json
    assert "expires_in" not in sent_json
    assert sent_json["user_id"] == "user_1"


@respx.mock
def test_sync_create_link_token_omits_optional_fields_when_unset(
    sync_client: SyncAppConnectClient,
) -> None:
    route = respx.post(f"{BASE_URL}/api/link-tokens").mock(
        return_value=_success(
            {
                "link_token": "lt_abc",
                "link_url": "https://example.invalid/link/lt_abc",
                "expires_at": "2026-01-01T00:00:00Z",
            }
        )
    )

    result = sync_client.create_link_token(
        user_id="user_1",
        redirect_uri="https://partner.example.com/callback",
    )

    assert result.link_token == "lt_abc"
    assert route.called
    sent_json = json.loads(respx.calls.last.request.content)
    assert "state" not in sent_json
    assert "allowed_services" not in sent_json
    assert "expires_in" not in sent_json


@respx.mock
async def test_exchange_link_token_pending(async_client: AppConnectClient) -> None:
    respx.post(f"{BASE_URL}/api/link-tokens/exchange").mock(
        return_value=_success(
            {"status": "pending", "user_id": "user_1", "state": None, "message": "Waiting for user"}
        )
    )

    result = await async_client.exchange_link_token("lt_abc")

    assert isinstance(result, PendingLinkExchangeResponse)
    assert result.user_id == "user_1"


@respx.mock
async def test_exchange_link_token_connected(async_client: AppConnectClient) -> None:
    respx.post(f"{BASE_URL}/api/link-tokens/exchange").mock(
        return_value=_success(
            {
                "status": "connected",
                "user_id": "user_1",
                "state": None,
                "access_token": "apphq_abc",
                "refresh_token": "apphq_refresh_abc",
                "token_type": "Bearer",
                "expires_at": "2026-01-01T00:00:00Z",
                "connected_services": ["google-calendar", "notion"],
            }
        )
    )

    result = await async_client.exchange_link_token("lt_abc")

    assert isinstance(result, ConnectedLinkExchangeResponse)
    assert result.connected_services == ["google-calendar", "notion"]


@respx.mock
async def test_exchange_authorization_code(async_client: AppConnectClient) -> None:
    respx.post(f"{BASE_URL}/api/oauth/token").mock(
        return_value=_success(
            {
                "access_token": "apphq_new",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": "apphq_refresh_new",
                "connected_services": ["github-oauth"],
            }
        )
    )

    result = await async_client.exchange_authorization_code(
        "auth_code_1", "https://partner.example.com/callback"
    )

    assert result.access_token == "apphq_new"
    sent_body = respx.calls.last.request.content
    assert b'"grant_type":"authorization_code"' in sent_body


@respx.mock
async def test_refresh_token(async_client: AppConnectClient) -> None:
    respx.post(f"{BASE_URL}/api/oauth/token").mock(
        return_value=_success(
            {
                "access_token": "apphq_refreshed",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": "apphq_refresh_2",
                "connected_services": [],
            }
        )
    )

    result = await async_client.refresh_token("apphq_refresh_old")

    assert result.access_token == "apphq_refreshed"
    sent_body = respx.calls.last.request.content
    assert b'"grant_type":"refresh_token"' in sent_body


@respx.mock
async def test_list_tools(async_client: AppConnectClient) -> None:
    respx.get(f"{BASE_URL}/api/tools").mock(
        return_value=_success(
            {
                "tools": [
                    {
                        "id": "google_calendar_list_events",
                        "service": "google-calendar",
                        "serviceName": "Google Calendar",
                        "name": "list_events",
                        "displayName": "List Events",
                        "description": "List calendar events",
                        "method": "GET",
                        "inputSchema": {"type": "object", "properties": {}, "required": []},
                    }
                ]
            }
        )
    )

    tools = await async_client.list_tools("apphq_token")

    assert len(tools) == 1
    assert tools[0].id == "google_calendar_list_events"
    sent_headers = respx.calls.last.request.headers
    assert sent_headers["authorization"] == "Bearer apphq_token"


@respx.mock
async def test_search_tools_sends_query_and_limit(async_client: AppConnectClient) -> None:
    route = respx.get(f"{BASE_URL}/api/tools/search").mock(
        return_value=_success({"query": "calendar", "tools": []})
    )

    tools = await async_client.search_tools("apphq_token", "calendar", limit=5)

    assert tools == []
    sent_url = route.calls.last.request.url
    assert sent_url.params["q"] == "calendar"
    assert sent_url.params["limit"] == "5"


@respx.mock
async def test_execute_tool(async_client: AppConnectClient) -> None:
    respx.post(f"{BASE_URL}/api/tools/execute").mock(
        return_value=_success({"tool": "github_oauth_list_repos", "data": {"items": []}})
    )

    result = await async_client.execute_tool(
        "apphq_token", "github_oauth_list_repos", {"org": "appconnecthq"}
    )

    assert result.tool == "github_oauth_list_repos"
    assert result.data == {"items": []}
    sent_body = respx.calls.last.request.content
    assert b'"params":{"org":"appconnecthq"}' in sent_body


@respx.mock
async def test_execute_tool_defaults_params_to_empty_dict(async_client: AppConnectClient) -> None:
    respx.post(f"{BASE_URL}/api/tools/execute").mock(
        return_value=_success({"tool": "notion_list_pages", "data": []})
    )

    await async_client.execute_tool("apphq_token", "notion_list_pages")

    sent_body = respx.calls.last.request.content
    assert b'"params":{}' in sent_body


@respx.mock
async def test_proxy_strips_leading_slash(async_client: AppConnectClient) -> None:
    route = respx.get(f"{BASE_URL}/api/proxy/github-oauth/user/repos").mock(
        return_value=_success({"repos": []})
    )

    result = await async_client.proxy("apphq_token", "github-oauth", "/user/repos")

    assert result == {"repos": []}
    assert route.called


@respx.mock
async def test_proxy_forwards_method_and_body(async_client: AppConnectClient) -> None:
    respx.post(f"{BASE_URL}/api/proxy/notion/pages").mock(return_value=_success({"id": "page_1"}))

    result = await async_client.proxy(
        "apphq_token", "notion", "pages", method="POST", body={"title": "New page"}
    )

    assert result == {"id": "page_1"}
    sent_body = respx.calls.last.request.content
    assert b'"title":"New page"' in sent_body


@respx.mock
async def test_error_response_raises_app_connect_error(async_client: AppConnectClient) -> None:
    respx.get(f"{BASE_URL}/api/tools").mock(
        return_value=_error("invalid_token", "Access token expired", 401)
    )

    with pytest.raises(AppConnectError) as exc_info:
        await async_client.list_tools("apphq_expired")

    assert exc_info.value.status == 401
    assert exc_info.value.code == "invalid_token"
    assert exc_info.value.message == "Access token expired"


@respx.mock
async def test_http_error_without_json_body(async_client: AppConnectClient) -> None:
    respx.get(f"{BASE_URL}/api/tools").mock(return_value=httpx.Response(500, text="Internal error"))

    with pytest.raises(AppConnectError) as exc_info:
        await async_client.list_tools("apphq_token")

    assert exc_info.value.status == 500


@respx.mock
async def test_network_error_raises_app_connect_error(async_client: AppConnectClient) -> None:
    respx.get(f"{BASE_URL}/api/tools").mock(side_effect=httpx.ConnectError("connection refused"))

    with pytest.raises(AppConnectError) as exc_info:
        await async_client.list_tools("apphq_token")

    assert exc_info.value.status == 0
    assert exc_info.value.code == "network_error"


async def test_async_client_context_manager_closes_owned_http_client() -> None:
    async with AppConnectClient(
        base_url=BASE_URL, client_id="client_123", client_secret="secret_abc"
    ) as client:
        internal_client = client._get_http_client()
        assert not internal_client.is_closed

    assert internal_client.is_closed


# --- sync client --------------------------------------------------------------


@respx.mock
def test_sync_list_tools(sync_client: SyncAppConnectClient) -> None:
    respx.get(f"{BASE_URL}/api/tools").mock(return_value=_success({"tools": []}))

    tools = sync_client.list_tools("apphq_token")

    assert tools == []


@respx.mock
def test_sync_execute_tool(sync_client: SyncAppConnectClient) -> None:
    respx.post(f"{BASE_URL}/api/tools/execute").mock(
        return_value=_success({"tool": "openai_chat_completion", "data": {"ok": True}})
    )

    result = sync_client.execute_tool("apphq_token", "openai_chat_completion", {"prompt": "hi"})

    assert result.data == {"ok": True}


@respx.mock
def test_sync_error_response_raises_app_connect_error(sync_client: SyncAppConnectClient) -> None:
    respx.get(f"{BASE_URL}/api/tools").mock(
        return_value=_error("invalid_token", "Access token expired", 401)
    )

    with pytest.raises(AppConnectError) as exc_info:
        sync_client.list_tools("apphq_expired")

    assert exc_info.value.status == 401


def test_sync_client_context_manager_closes_owned_http_client() -> None:
    with SyncAppConnectClient(
        base_url=BASE_URL, client_id="client_123", client_secret="secret_abc"
    ) as client:
        internal_client = client._get_http_client()
        assert not internal_client.is_closed

    assert internal_client.is_closed
