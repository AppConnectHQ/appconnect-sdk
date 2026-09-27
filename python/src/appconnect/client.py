"""AppConnect API clients: async `AppConnectClient` and its sync twin.

Both mirror `@appconnecthq/sdk`'s `AppConnectClient` (`typescript/src/index.ts`)
1:1 -- same endpoints, same request/response shapes. AppConnect's REST API
is simple enough (bearer-per-call, no session/connection lifecycle) that the
sync client is a plain twin built on `httpx.Client` rather than an
asyncio.run() wrapper around the async one; the two classes share the pure
request-building helpers below so the only real duplication is the I/O call
itself.
"""

from __future__ import annotations

from typing import Any

import httpx

from appconnect.config import resolve_config
from appconnect.triggers import (
    build_list_deliveries_params,
    build_list_trigger_definitions_params,
    build_subscribe_trigger_body,
    build_update_trigger_instance_body,
)
from appconnect.types import (
    EXCHANGE_LINK_TOKEN_ADAPTER,
    AppConnectError,
    ConnectedLinkExchangeResponse,
    CreateLinkTokenResponse,
    GetTriggerInstanceResponse,
    ListDeliveriesResponse,
    ListToolsResponse,
    ListTriggerDefinitionsResponse,
    ListTriggerInstancesResponse,
    PendingLinkExchangeResponse,
    SearchToolsResponse,
    SubscribeTriggerResponse,
    TokenResponse,
    Tool,
    ToolExecutionResponse,
    TriggerDefinition,
    TriggerInstance,
    UnsubscribeTriggerResponse,
    UpdateTriggerInstanceResponse,
)


def _build_headers(access_token: str | None) -> dict[str, str]:
    headers: dict[str, str] = {"Accept": "application/json"}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    return headers


def _parse_response(response: httpx.Response) -> Any:
    try:
        payload = response.json()
    except ValueError:
        payload = None

    is_error_payload = isinstance(payload, dict) and payload.get("success") is False
    if response.is_error or is_error_payload:
        error = payload.get("error") if isinstance(payload, dict) else None
        message = (error or {}).get("message") if error else None
        code = (error or {}).get("code") if error else None
        raise AppConnectError(
            message or response.reason_phrase or "Request failed", response.status_code, code
        )

    return payload.get("data") if isinstance(payload, dict) else None


def _create_link_token_body(
    client_id: str,
    client_secret: str,
    user_id: str,
    redirect_uri: str,
    state: str | None,
    allowed_services: list[str] | None,
    expires_in: int | None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "client_id": client_id,
        "client_secret": client_secret,
        "user_id": user_id,
        "redirect_uri": redirect_uri,
    }
    if state is not None:
        body["state"] = state
    if allowed_services is not None:
        body["allowed_services"] = allowed_services
    if expires_in is not None:
        body["expires_in"] = expires_in
    return body


def _exchange_link_token_body(
    client_id: str, client_secret: str, link_token: str
) -> dict[str, Any]:
    return {"client_id": client_id, "client_secret": client_secret, "link_token": link_token}


def _authorization_code_body(
    client_id: str, client_secret: str, code: str, redirect_uri: str
) -> dict[str, Any]:
    return {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
    }


def _refresh_token_body(client_id: str, client_secret: str, refresh_token: str) -> dict[str, Any]:
    return {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
    }


def _search_tools_params(query: str, limit: int | None) -> dict[str, str]:
    params = {"q": query}
    if limit is not None:
        params["limit"] = str(limit)
    return params


class AppConnectClient:
    """Async AppConnect API client."""

    def __init__(
        self,
        base_url: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        timeout: int = 30,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        config = resolve_config(base_url, client_id, client_secret)
        self._base_url = config.base_url
        self._client_id = config.client_id
        self._client_secret = config.client_secret
        self._timeout = timeout
        self._http_client = http_client
        self._owns_http_client = http_client is None

    async def __aenter__(self) -> AppConnectClient:
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        """Close the underlying HTTP client, if this instance created it."""
        if self._owns_http_client and self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None

    def _get_http_client(self) -> httpx.AsyncClient:
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=self._timeout)
        return self._http_client

    async def create_link_token(
        self,
        user_id: str,
        redirect_uri: str,
        state: str | None = None,
        allowed_services: list[str] | None = None,
        expires_in: int | None = None,
    ) -> CreateLinkTokenResponse:
        body = _create_link_token_body(
            self._client_id,
            self._client_secret,
            user_id,
            redirect_uri,
            state,
            allowed_services,
            expires_in,
        )
        payload = await self._request("POST", "/api/link-tokens", body=body)
        return CreateLinkTokenResponse.model_validate(payload)

    async def exchange_link_token(
        self, link_token: str
    ) -> PendingLinkExchangeResponse | ConnectedLinkExchangeResponse:
        body = _exchange_link_token_body(self._client_id, self._client_secret, link_token)
        payload = await self._request("POST", "/api/link-tokens/exchange", body=body)
        return EXCHANGE_LINK_TOKEN_ADAPTER.validate_python(payload)

    async def exchange_authorization_code(self, code: str, redirect_uri: str) -> TokenResponse:
        body = _authorization_code_body(self._client_id, self._client_secret, code, redirect_uri)
        payload = await self._request("POST", "/api/oauth/token", body=body)
        return TokenResponse.model_validate(payload)

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        body = _refresh_token_body(self._client_id, self._client_secret, refresh_token)
        payload = await self._request("POST", "/api/oauth/token", body=body)
        return TokenResponse.model_validate(payload)

    async def list_tools(self, access_token: str) -> list[Tool]:
        payload = await self._request("GET", "/api/tools", access_token=access_token)
        return ListToolsResponse.model_validate(payload).tools

    async def search_tools(
        self, access_token: str, query: str, limit: int | None = None
    ) -> list[Tool]:
        payload = await self._request(
            "GET",
            "/api/tools/search",
            access_token=access_token,
            query_params=_search_tools_params(query, limit),
        )
        return SearchToolsResponse.model_validate(payload).tools

    async def execute_tool(
        self, access_token: str, tool: str, params: dict[str, Any] | None = None
    ) -> ToolExecutionResponse:
        payload = await self._request(
            "POST",
            "/api/tools/execute",
            access_token=access_token,
            body={"tool": tool, "params": params or {}},
        )
        return ToolExecutionResponse.model_validate(payload)

    async def proxy(
        self,
        access_token: str,
        service: str,
        path: str,
        method: str = "GET",
        body: Any = None,
    ) -> Any:
        clean_path = path.lstrip("/")
        return await self._request(
            method, f"/api/proxy/{service}/{clean_path}", access_token=access_token, body=body
        )

    async def list_trigger_definitions(
        self, access_token: str, service: str | None = None
    ) -> list[TriggerDefinition]:
        payload = await self._request(
            "GET",
            "/api/trigger-definitions",
            access_token=access_token,
            query_params=build_list_trigger_definitions_params(service),
        )
        return ListTriggerDefinitionsResponse.model_validate(payload).trigger_definitions

    async def subscribe_trigger(
        self,
        access_token: str,
        service: str,
        trigger: str,
        config: dict[str, Any],
        callback_url: str,
    ) -> SubscribeTriggerResponse:
        body = build_subscribe_trigger_body(service, trigger, config, callback_url)
        payload = await self._request("POST", "/api/triggers", access_token=access_token, body=body)
        return SubscribeTriggerResponse.model_validate(payload)

    async def list_trigger_instances(self, access_token: str) -> list[TriggerInstance]:
        payload = await self._request("GET", "/api/triggers", access_token=access_token)
        return ListTriggerInstancesResponse.model_validate(payload).triggers

    async def get_trigger_instance(self, access_token: str, trigger_id: str) -> TriggerInstance:
        payload = await self._request(
            "GET", f"/api/triggers/{trigger_id}", access_token=access_token
        )
        return GetTriggerInstanceResponse.model_validate(payload).trigger

    async def update_trigger_instance(
        self,
        access_token: str,
        trigger_id: str,
        status: str | None = None,
        callback_url: str | None = None,
        config: dict[str, Any] | None = None,
    ) -> TriggerInstance:
        body = build_update_trigger_instance_body(status, callback_url, config)
        payload = await self._request(
            "PATCH", f"/api/triggers/{trigger_id}", access_token=access_token, body=body
        )
        return UpdateTriggerInstanceResponse.model_validate(payload).trigger

    async def unsubscribe_trigger(self, access_token: str, trigger_id: str) -> bool:
        payload = await self._request(
            "DELETE", f"/api/triggers/{trigger_id}", access_token=access_token
        )
        return UnsubscribeTriggerResponse.model_validate(payload).revoked

    async def list_deliveries(
        self,
        access_token: str,
        trigger_instance_id: str,
        status: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> ListDeliveriesResponse:
        payload = await self._request(
            "GET",
            f"/api/triggers/{trigger_instance_id}/deliveries",
            access_token=access_token,
            query_params=build_list_deliveries_params(status, limit, cursor),
        )
        return ListDeliveriesResponse.model_validate(payload)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        body: Any = None,
        access_token: str | None = None,
        query_params: dict[str, str] | None = None,
    ) -> Any:
        client = self._get_http_client()
        try:
            response = await client.request(
                method,
                f"{self._base_url}{path}",
                headers=_build_headers(access_token),
                params=query_params,
                json=body,
            )
        except httpx.HTTPError as exc:
            raise AppConnectError(f"Request failed: {exc}", status=0, code="network_error") from exc

        return _parse_response(response)


class SyncAppConnectClient:
    """Synchronous twin of `AppConnectClient`, built on `httpx.Client`."""

    def __init__(
        self,
        base_url: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        timeout: int = 30,
        http_client: httpx.Client | None = None,
    ) -> None:
        config = resolve_config(base_url, client_id, client_secret)
        self._base_url = config.base_url
        self._client_id = config.client_id
        self._client_secret = config.client_secret
        self._timeout = timeout
        self._http_client = http_client
        self._owns_http_client = http_client is None

    def __enter__(self) -> SyncAppConnectClient:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP client, if this instance created it."""
        if self._owns_http_client and self._http_client is not None:
            self._http_client.close()
            self._http_client = None

    def _get_http_client(self) -> httpx.Client:
        if self._http_client is None:
            self._http_client = httpx.Client(timeout=self._timeout)
        return self._http_client

    def create_link_token(
        self,
        user_id: str,
        redirect_uri: str,
        state: str | None = None,
        allowed_services: list[str] | None = None,
        expires_in: int | None = None,
    ) -> CreateLinkTokenResponse:
        body = _create_link_token_body(
            self._client_id,
            self._client_secret,
            user_id,
            redirect_uri,
            state,
            allowed_services,
            expires_in,
        )
        payload = self._request("POST", "/api/link-tokens", body=body)
        return CreateLinkTokenResponse.model_validate(payload)

    def exchange_link_token(
        self, link_token: str
    ) -> PendingLinkExchangeResponse | ConnectedLinkExchangeResponse:
        body = _exchange_link_token_body(self._client_id, self._client_secret, link_token)
        payload = self._request("POST", "/api/link-tokens/exchange", body=body)
        return EXCHANGE_LINK_TOKEN_ADAPTER.validate_python(payload)

    def exchange_authorization_code(self, code: str, redirect_uri: str) -> TokenResponse:
        body = _authorization_code_body(self._client_id, self._client_secret, code, redirect_uri)
        payload = self._request("POST", "/api/oauth/token", body=body)
        return TokenResponse.model_validate(payload)

    def refresh_token(self, refresh_token: str) -> TokenResponse:
        body = _refresh_token_body(self._client_id, self._client_secret, refresh_token)
        payload = self._request("POST", "/api/oauth/token", body=body)
        return TokenResponse.model_validate(payload)

    def list_tools(self, access_token: str) -> list[Tool]:
        payload = self._request("GET", "/api/tools", access_token=access_token)
        return ListToolsResponse.model_validate(payload).tools

    def search_tools(self, access_token: str, query: str, limit: int | None = None) -> list[Tool]:
        payload = self._request(
            "GET",
            "/api/tools/search",
            access_token=access_token,
            query_params=_search_tools_params(query, limit),
        )
        return SearchToolsResponse.model_validate(payload).tools

    def execute_tool(
        self, access_token: str, tool: str, params: dict[str, Any] | None = None
    ) -> ToolExecutionResponse:
        payload = self._request(
            "POST",
            "/api/tools/execute",
            access_token=access_token,
            body={"tool": tool, "params": params or {}},
        )
        return ToolExecutionResponse.model_validate(payload)

    def proxy(
        self,
        access_token: str,
        service: str,
        path: str,
        method: str = "GET",
        body: Any = None,
    ) -> Any:
        clean_path = path.lstrip("/")
        return self._request(
            method, f"/api/proxy/{service}/{clean_path}", access_token=access_token, body=body
        )

    def list_trigger_definitions(
        self, access_token: str, service: str | None = None
    ) -> list[TriggerDefinition]:
        payload = self._request(
            "GET",
            "/api/trigger-definitions",
            access_token=access_token,
            query_params=build_list_trigger_definitions_params(service),
        )
        return ListTriggerDefinitionsResponse.model_validate(payload).trigger_definitions

    def subscribe_trigger(
        self,
        access_token: str,
        service: str,
        trigger: str,
        config: dict[str, Any],
        callback_url: str,
    ) -> SubscribeTriggerResponse:
        body = build_subscribe_trigger_body(service, trigger, config, callback_url)
        payload = self._request("POST", "/api/triggers", access_token=access_token, body=body)
        return SubscribeTriggerResponse.model_validate(payload)

    def list_trigger_instances(self, access_token: str) -> list[TriggerInstance]:
        payload = self._request("GET", "/api/triggers", access_token=access_token)
        return ListTriggerInstancesResponse.model_validate(payload).triggers

    def get_trigger_instance(self, access_token: str, trigger_id: str) -> TriggerInstance:
        payload = self._request("GET", f"/api/triggers/{trigger_id}", access_token=access_token)
        return GetTriggerInstanceResponse.model_validate(payload).trigger

    def update_trigger_instance(
        self,
        access_token: str,
        trigger_id: str,
        status: str | None = None,
        callback_url: str | None = None,
        config: dict[str, Any] | None = None,
    ) -> TriggerInstance:
        body = build_update_trigger_instance_body(status, callback_url, config)
        payload = self._request(
            "PATCH", f"/api/triggers/{trigger_id}", access_token=access_token, body=body
        )
        return UpdateTriggerInstanceResponse.model_validate(payload).trigger

    def unsubscribe_trigger(self, access_token: str, trigger_id: str) -> bool:
        payload = self._request("DELETE", f"/api/triggers/{trigger_id}", access_token=access_token)
        return UnsubscribeTriggerResponse.model_validate(payload).revoked

    def list_deliveries(
        self,
        access_token: str,
        trigger_instance_id: str,
        status: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> ListDeliveriesResponse:
        payload = self._request(
            "GET",
            f"/api/triggers/{trigger_instance_id}/deliveries",
            access_token=access_token,
            query_params=build_list_deliveries_params(status, limit, cursor),
        )
        return ListDeliveriesResponse.model_validate(payload)

    def _request(
        self,
        method: str,
        path: str,
        *,
        body: Any = None,
        access_token: str | None = None,
        query_params: dict[str, str] | None = None,
    ) -> Any:
        client = self._get_http_client()
        try:
            response = client.request(
                method,
                f"{self._base_url}{path}",
                headers=_build_headers(access_token),
                params=query_params,
                json=body,
            )
        except httpx.HTTPError as exc:
            raise AppConnectError(f"Request failed: {exc}", status=0, code="network_error") from exc

        return _parse_response(response)
