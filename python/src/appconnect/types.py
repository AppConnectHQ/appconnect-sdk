"""Pydantic models and the single error type for the AppConnect Python SDK.

Field names intentionally mirror the wire JSON keys (matching `@appconnecthq/sdk`'s
TS shapes 1:1, see `typescript/src/index.ts`) rather than being renamed to
idiomatic snake_case, so `Model.model_validate()` can parse API responses
directly without an alias layer. OAuth-token fields were already snake_case
on the wire (e.g. `access_token`); tool/service fields were already
camelCase (`serviceName`, `inputSchema`) -- both are preserved as-is here.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, TypeAdapter


class AppConnectError(Exception):
    """Single error type for all AppConnect SDK failures.

    Mirrors the TS SDK's `AppConnectError`: HTTP/API failures carry the
    response `status` and optional server-provided `code`; client-side
    failures (missing configuration, network errors) use `status=0`.
    """

    def __init__(self, message: str, status: int = 0, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.status = status
        self.code = code

    def __repr__(self) -> str:
        return (
            f"AppConnectError(message={self.message!r}, status={self.status}, code={self.code!r})"
        )


class CreateLinkTokenResponse(BaseModel):
    link_token: str
    link_url: str
    expires_at: str


class PendingLinkExchangeResponse(BaseModel):
    status: Literal["pending"]
    user_id: str
    state: str | None = None
    message: str


class ConnectedLinkExchangeResponse(BaseModel):
    status: Literal["connected"]
    user_id: str
    state: str | None = None
    access_token: str
    refresh_token: str
    token_type: Literal["Bearer"]
    expires_at: str
    connected_services: list[str]


ExchangeLinkTokenResponse = Annotated[
    PendingLinkExchangeResponse | ConnectedLinkExchangeResponse,
    Field(discriminator="status"),
]

EXCHANGE_LINK_TOKEN_ADAPTER: TypeAdapter[
    PendingLinkExchangeResponse | ConnectedLinkExchangeResponse
] = TypeAdapter(ExchangeLinkTokenResponse)


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["Bearer"]
    expires_in: int
    refresh_token: str
    connected_services: list[str]


class ToolInputSchema(BaseModel):
    """JSON Schema for a tool's parameters, as `service_tools.input_schema`."""

    type: str
    properties: dict[str, Any] | None = None
    required: list[str] | None = None


class Tool(BaseModel):
    """A tool exposed by a connected service, as returned by `GET /api/tools`
    and `GET /api/tools/search`. Mirrors the server's `listUserTools`
    response shape.
    """

    id: str
    """Unified tool id, e.g. "google_calendar_list_events" -- what execute_tool expects."""
    service: str
    """Service slug, e.g. "google-calendar"."""
    serviceName: str
    name: str
    """Tool name within the service, e.g. "list_events"."""
    displayName: str
    description: str | None = None
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
    inputSchema: ToolInputSchema | None = None


class ListToolsResponse(BaseModel):
    tools: list[Tool]


class SearchToolsResponse(BaseModel):
    query: str
    tools: list[Tool]


class ToolExecutionResponse(BaseModel):
    tool: str
    data: Any = None


class TriggerDefinition(BaseModel):
    """A trigger type available for a connected service, as returned by
    `GET /api/trigger-definitions`. Mirrors the server's
    `listUserTriggerDefinitions` response shape.
    """

    id: str
    service: str
    serviceName: str
    slug: str
    """Trigger type slug within the service, e.g. "new_commit"."""
    displayName: str
    description: str | None = None
    mode: Literal["webhook", "polling"]
    configSchema: Any = None
    """JSON Schema describing what `subscribe_trigger`'s `config` must supply."""
    payloadSchema: Any = None
    """JSON Schema documenting the normalized payload shape delivered to `callback_url`."""


class ListTriggerDefinitionsResponse(BaseModel):
    trigger_definitions: list[TriggerDefinition]


class TriggerInstance(BaseModel):
    """A subscription to a trigger for a connected account, as returned by
    `api/triggers*`. Mirrors the server's `PublicTriggerInstance`
    response shape.
    """

    id: str
    service: str
    trigger: str
    """Trigger definition slug this instance subscribes to, e.g. "new_commit"."""
    config: dict[str, Any]
    callbackUrl: str
    status: str
    lastEventAt: str | None = None
    lastPolledAt: str | None = None
    errorMessage: str | None = None
    createdAt: str
    updatedAt: str


class ListTriggerInstancesResponse(BaseModel):
    triggers: list[TriggerInstance]


class GetTriggerInstanceResponse(BaseModel):
    trigger: TriggerInstance


class SubscribeTriggerResponse(BaseModel):
    trigger: TriggerInstance
    signing_secret: str
    """Returned exactly once -- store it to verify `X-AppConnect-Signature`
    on inbound deliveries via `verify_webhook_signature()`. Subsequent GETs
    never return it again."""


class UpdateTriggerInstanceResponse(BaseModel):
    trigger: TriggerInstance


class UnsubscribeTriggerResponse(BaseModel):
    revoked: Literal[True]


class DeliveryAttempt(BaseModel):
    """One HTTP attempt at delivering an event to a trigger instance's `callback_url`."""

    attemptNumber: int
    statusCode: int | None = None
    latencyMs: int | None = None
    errorMessage: str | None = None
    createdAt: str


class Delivery(BaseModel):
    """A queued/delivered event row, as returned by
    `GET /api/triggers/{id}/deliveries`. Mirrors the server's `PublicDelivery`
    response shape.
    """

    id: str
    eventId: str
    eventType: str
    status: str
    attempts: int
    maxAttempts: int
    nextAttemptAt: str
    lastAttemptAt: str | None = None
    lastStatusCode: int | None = None
    lastError: str | None = None
    createdAt: str
    updatedAt: str
    latestAttempt: DeliveryAttempt | None = None


class ListDeliveriesResponse(BaseModel):
    deliveries: list[Delivery]
    nextCursor: str | None = None
