# Clients and helpers

Import from `appconnect`. `AppConnectClient` is async; `SyncAppConnectClient` has the same methods for synchronous code.

## `AppConnectClient`

Async AppConnect API client.

### Constructor

```python
AppConnectClient(base_url: str | None = None, client_id: str | None = None, client_secret: str | None = None, timeout: int = 30, http_client: httpx.AsyncClient | None = None)
```

Supports `async with`; the underlying HTTP client is closed on exit.

### `aclose()`

```python
async def aclose() -> None
```

Close the underlying HTTP client, if this instance created it.

### `create_link_token()`

```python
async def create_link_token(user_id: str, redirect_uri: str, state: str | None = None, allowed_services: list[str] | None = None, expires_in: int | None = None) -> CreateLinkTokenResponse
```

### `exchange_link_token()`

```python
async def exchange_link_token(link_token: str) -> PendingLinkExchangeResponse | ConnectedLinkExchangeResponse
```

### `exchange_authorization_code()`

```python
async def exchange_authorization_code(code: str, redirect_uri: str) -> TokenResponse
```

### `refresh_token()`

```python
async def refresh_token(refresh_token: str) -> TokenResponse
```

### `list_tools()`

```python
async def list_tools(access_token: str) -> list[Tool]
```

### `search_tools()`

```python
async def search_tools(access_token: str, query: str, limit: int | None = None) -> list[Tool]
```

### `execute_tool()`

```python
async def execute_tool(access_token: str, tool: str, params: dict[str, Any] | None = None) -> ToolExecutionResponse
```

### `proxy()`

```python
async def proxy(access_token: str, service: str, path: str, method: str = 'GET', body: Any = None) -> Any
```

### `list_trigger_definitions()`

```python
async def list_trigger_definitions(access_token: str, service: str | None = None) -> list[TriggerDefinition]
```

### `subscribe_trigger()`

```python
async def subscribe_trigger(access_token: str, service: str, trigger: str, config: dict[str, Any], callback_url: str) -> SubscribeTriggerResponse
```

### `list_trigger_instances()`

```python
async def list_trigger_instances(access_token: str) -> list[TriggerInstance]
```

### `get_trigger_instance()`

```python
async def get_trigger_instance(access_token: str, trigger_id: str) -> TriggerInstance
```

### `update_trigger_instance()`

```python
async def update_trigger_instance(access_token: str, trigger_id: str, status: str | None = None, callback_url: str | None = None, config: dict[str, Any] | None = None) -> TriggerInstance
```

### `unsubscribe_trigger()`

```python
async def unsubscribe_trigger(access_token: str, trigger_id: str) -> bool
```

### `list_deliveries()`

```python
async def list_deliveries(access_token: str, trigger_instance_id: str, status: str | None = None, limit: int | None = None, cursor: str | None = None) -> ListDeliveriesResponse
```

## `SyncAppConnectClient`

Synchronous twin of `AppConnectClient`, built on `httpx.Client`.

### Constructor

```python
SyncAppConnectClient(base_url: str | None = None, client_id: str | None = None, client_secret: str | None = None, timeout: int = 30, http_client: httpx.Client | None = None)
```

Supports `with`; the underlying HTTP client is closed on exit.

### `close()`

```python
def close() -> None
```

Close the underlying HTTP client, if this instance created it.

### `create_link_token()`

```python
def create_link_token(user_id: str, redirect_uri: str, state: str | None = None, allowed_services: list[str] | None = None, expires_in: int | None = None) -> CreateLinkTokenResponse
```

### `exchange_link_token()`

```python
def exchange_link_token(link_token: str) -> PendingLinkExchangeResponse | ConnectedLinkExchangeResponse
```

### `exchange_authorization_code()`

```python
def exchange_authorization_code(code: str, redirect_uri: str) -> TokenResponse
```

### `refresh_token()`

```python
def refresh_token(refresh_token: str) -> TokenResponse
```

### `list_tools()`

```python
def list_tools(access_token: str) -> list[Tool]
```

### `search_tools()`

```python
def search_tools(access_token: str, query: str, limit: int | None = None) -> list[Tool]
```

### `execute_tool()`

```python
def execute_tool(access_token: str, tool: str, params: dict[str, Any] | None = None) -> ToolExecutionResponse
```

### `proxy()`

```python
def proxy(access_token: str, service: str, path: str, method: str = 'GET', body: Any = None) -> Any
```

### `list_trigger_definitions()`

```python
def list_trigger_definitions(access_token: str, service: str | None = None) -> list[TriggerDefinition]
```

### `subscribe_trigger()`

```python
def subscribe_trigger(access_token: str, service: str, trigger: str, config: dict[str, Any], callback_url: str) -> SubscribeTriggerResponse
```

### `list_trigger_instances()`

```python
def list_trigger_instances(access_token: str) -> list[TriggerInstance]
```

### `get_trigger_instance()`

```python
def get_trigger_instance(access_token: str, trigger_id: str) -> TriggerInstance
```

### `update_trigger_instance()`

```python
def update_trigger_instance(access_token: str, trigger_id: str, status: str | None = None, callback_url: str | None = None, config: dict[str, Any] | None = None) -> TriggerInstance
```

### `unsubscribe_trigger()`

```python
def unsubscribe_trigger(access_token: str, trigger_id: str) -> bool
```

### `list_deliveries()`

```python
def list_deliveries(access_token: str, trigger_instance_id: str, status: str | None = None, limit: int | None = None, cursor: str | None = None) -> ListDeliveriesResponse
```

## `AppConnectError`

Single error type for all AppConnect SDK failures.

Mirrors the TS SDK's `AppConnectError`: HTTP/API failures carry the
response `status` and optional server-provided `code`; client-side
failures (missing configuration, network errors) use `status=0`.

### Constructor

```python
AppConnectError(message: str, status: int = 0, code: str | None = None)
```

## `verify_webhook_signature()`

```python
def verify_webhook_signature(raw_body: str, header: str, signing_secret: str, tolerance_seconds: int = 300) -> bool
```
