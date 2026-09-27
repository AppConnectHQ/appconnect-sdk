"""Unit tests for the trigger/webhook methods on AppConnectClient and
SyncAppConnectClient, using respx
to mock the HTTP transport. Split out of `test_client.py` once it grew past
a convenient size; shares the `async_client`/`sync_client` fixtures and
`_success`/`BASE_URL` helpers from `conftest.py`.
"""

from __future__ import annotations

import json

import httpx
import respx
from conftest import BASE_URL, _success

from appconnect.client import AppConnectClient, SyncAppConnectClient

# --- async client -------------------------------------------------------------


@respx.mock
async def test_list_trigger_definitions_without_service_filter(
    async_client: AppConnectClient,
) -> None:
    route = respx.get(f"{BASE_URL}/api/trigger-definitions").mock(
        return_value=_success({"trigger_definitions": []})
    )

    result = await async_client.list_trigger_definitions("apphq_token")

    assert result == []
    assert route.called
    assert route.calls.last.request.url.params == httpx.QueryParams()


@respx.mock
async def test_list_trigger_definitions_with_service_filter(
    async_client: AppConnectClient,
) -> None:
    route = respx.get(f"{BASE_URL}/api/trigger-definitions").mock(
        return_value=_success(
            {
                "trigger_definitions": [
                    {
                        "id": "def_1",
                        "service": "github-oauth",
                        "serviceName": "GitHub",
                        "slug": "new_commit",
                        "displayName": "New Commit",
                        "description": None,
                        "mode": "webhook",
                        "configSchema": {"type": "object"},
                        "payloadSchema": {"type": "object"},
                    }
                ]
            }
        )
    )

    result = await async_client.list_trigger_definitions("apphq_token", service="github-oauth")

    assert len(result) == 1
    assert result[0].slug == "new_commit"
    assert route.calls.last.request.url.params["service"] == "github-oauth"


@respx.mock
async def test_subscribe_trigger_sends_snake_case_callback_url(
    async_client: AppConnectClient,
) -> None:
    respx.post(f"{BASE_URL}/api/triggers").mock(
        return_value=_success(
            {
                "trigger": {
                    "id": "trg_1",
                    "service": "github-oauth",
                    "trigger": "new_commit",
                    "config": {"owner": "octocat", "repo": "hello-world"},
                    "callbackUrl": "https://partner.example.com/hooks/appconnect",
                    "status": "active",
                    "lastEventAt": None,
                    "lastPolledAt": None,
                    "errorMessage": None,
                    "createdAt": "2026-01-01T00:00:00Z",
                    "updatedAt": "2026-01-01T00:00:00Z",
                },
                "signing_secret": "whsec_abc123",
            }
        )
    )

    result = await async_client.subscribe_trigger(
        "apphq_token",
        service="github-oauth",
        trigger="new_commit",
        config={"owner": "octocat", "repo": "hello-world"},
        callback_url="https://partner.example.com/hooks/appconnect",
    )

    assert result.signing_secret == "whsec_abc123"
    assert result.trigger.id == "trg_1"
    sent_json = json.loads(respx.calls.last.request.content)
    assert sent_json["callback_url"] == "https://partner.example.com/hooks/appconnect"


@respx.mock
async def test_list_trigger_instances(async_client: AppConnectClient) -> None:
    respx.get(f"{BASE_URL}/api/triggers").mock(return_value=_success({"triggers": []}))

    result = await async_client.list_trigger_instances("apphq_token")

    assert result == []


@respx.mock
async def test_get_trigger_instance(async_client: AppConnectClient) -> None:
    respx.get(f"{BASE_URL}/api/triggers/trg_1").mock(
        return_value=_success(
            {
                "trigger": {
                    "id": "trg_1",
                    "service": "github-oauth",
                    "trigger": "new_commit",
                    "config": {},
                    "callbackUrl": "https://partner.example.com/hook",
                    "status": "active",
                    "lastEventAt": None,
                    "lastPolledAt": None,
                    "errorMessage": None,
                    "createdAt": "2026-01-01T00:00:00Z",
                    "updatedAt": "2026-01-01T00:00:00Z",
                }
            }
        )
    )

    result = await async_client.get_trigger_instance("apphq_token", "trg_1")

    assert result.id == "trg_1"


@respx.mock
async def test_update_trigger_instance_omits_unset_fields_in_body(
    async_client: AppConnectClient,
) -> None:
    route = respx.patch(f"{BASE_URL}/api/triggers/trg_1").mock(
        return_value=_success(
            {
                "trigger": {
                    "id": "trg_1",
                    "service": "github-oauth",
                    "trigger": "new_commit",
                    "config": {},
                    "callbackUrl": "https://partner.example.com/hook",
                    "status": "paused",
                    "lastEventAt": None,
                    "lastPolledAt": None,
                    "errorMessage": None,
                    "createdAt": "2026-01-01T00:00:00Z",
                    "updatedAt": "2026-01-01T00:00:00Z",
                }
            }
        )
    )

    result = await async_client.update_trigger_instance("apphq_token", "trg_1", status="paused")

    assert result.status == "paused"
    sent_json = json.loads(route.calls.last.request.content)
    assert sent_json == {"status": "paused"}


@respx.mock
async def test_unsubscribe_trigger(async_client: AppConnectClient) -> None:
    respx.delete(f"{BASE_URL}/api/triggers/trg_1").mock(return_value=_success({"revoked": True}))

    result = await async_client.unsubscribe_trigger("apphq_token", "trg_1")

    assert result is True


@respx.mock
async def test_list_deliveries_encodes_filters_into_querystring(
    async_client: AppConnectClient,
) -> None:
    route = respx.get(f"{BASE_URL}/api/triggers/trg_1/deliveries").mock(
        return_value=_success({"deliveries": [], "nextCursor": None})
    )

    result = await async_client.list_deliveries(
        "apphq_token", "trg_1", status="failed", limit=10, cursor="2026-01-01T00:00:00Z"
    )

    assert result.deliveries == []
    assert result.nextCursor is None
    sent_params = route.calls.last.request.url.params
    assert sent_params["status"] == "failed"
    assert sent_params["limit"] == "10"
    assert sent_params["cursor"] == "2026-01-01T00:00:00Z"


# --- sync client ----------------------------------------------------------


@respx.mock
def test_sync_subscribe_trigger_sends_snake_case_callback_url(
    sync_client: SyncAppConnectClient,
) -> None:
    respx.post(f"{BASE_URL}/api/triggers").mock(
        return_value=_success(
            {
                "trigger": {
                    "id": "trg_1",
                    "service": "shopify",
                    "trigger": "order_created",
                    "config": {},
                    "callbackUrl": "https://partner.example.com/hooks/appconnect",
                    "status": "active",
                    "lastEventAt": None,
                    "lastPolledAt": None,
                    "errorMessage": None,
                    "createdAt": "2026-01-01T00:00:00Z",
                    "updatedAt": "2026-01-01T00:00:00Z",
                },
                "signing_secret": "whsec_def456",
            }
        )
    )

    result = sync_client.subscribe_trigger(
        "apphq_token",
        service="shopify",
        trigger="order_created",
        config={},
        callback_url="https://partner.example.com/hooks/appconnect",
    )

    assert result.signing_secret == "whsec_def456"
    sent_json = json.loads(respx.calls.last.request.content)
    assert sent_json["callback_url"] == "https://partner.example.com/hooks/appconnect"


@respx.mock
def test_sync_list_trigger_instances(sync_client: SyncAppConnectClient) -> None:
    respx.get(f"{BASE_URL}/api/triggers").mock(return_value=_success({"triggers": []}))

    result = sync_client.list_trigger_instances("apphq_token")

    assert result == []


@respx.mock
def test_sync_update_trigger_instance_omits_unset_fields_in_body(
    sync_client: SyncAppConnectClient,
) -> None:
    route = respx.patch(f"{BASE_URL}/api/triggers/trg_1").mock(
        return_value=_success(
            {
                "trigger": {
                    "id": "trg_1",
                    "service": "github-oauth",
                    "trigger": "new_commit",
                    "config": {},
                    "callbackUrl": "https://new.example.com/hook",
                    "status": "active",
                    "lastEventAt": None,
                    "lastPolledAt": None,
                    "errorMessage": None,
                    "createdAt": "2026-01-01T00:00:00Z",
                    "updatedAt": "2026-01-01T00:00:00Z",
                }
            }
        )
    )

    result = sync_client.update_trigger_instance(
        "apphq_token", "trg_1", callback_url="https://new.example.com/hook"
    )

    assert result.callbackUrl == "https://new.example.com/hook"
    sent_json = json.loads(route.calls.last.request.content)
    assert sent_json == {"callback_url": "https://new.example.com/hook"}


@respx.mock
def test_sync_unsubscribe_trigger(sync_client: SyncAppConnectClient) -> None:
    respx.delete(f"{BASE_URL}/api/triggers/trg_1").mock(return_value=_success({"revoked": True}))

    result = sync_client.unsubscribe_trigger("apphq_token", "trg_1")

    assert result is True


@respx.mock
def test_sync_list_deliveries_no_querystring_when_opts_unset(
    sync_client: SyncAppConnectClient,
) -> None:
    route = respx.get(f"{BASE_URL}/api/triggers/trg_1/deliveries").mock(
        return_value=_success({"deliveries": [], "nextCursor": None})
    )

    result = sync_client.list_deliveries("apphq_token", "trg_1")

    assert result.deliveries == []
    assert route.calls.last.request.url.params == httpx.QueryParams()
