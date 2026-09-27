"""AppConnect Python SDK.

A thin REST client for the AppConnectHQ unified connector platform, mirroring
`@appconnecthq/sdk` (`typescript/src/index.ts`) 1:1.

    from appconnect import AppConnectClient

    async with AppConnectClient(
        base_url=os.environ["PRODUCTION_API_ORIGIN"],
        client_id="...",
        client_secret="...",
    ) as client:
        tools = await client.list_tools(access_token)
"""

from appconnect.client import AppConnectClient, SyncAppConnectClient
from appconnect.types import (
    AppConnectError,
    ConnectedLinkExchangeResponse,
    CreateLinkTokenResponse,
    Delivery,
    DeliveryAttempt,
    ExchangeLinkTokenResponse,
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
    ToolInputSchema,
    TriggerDefinition,
    TriggerInstance,
    UnsubscribeTriggerResponse,
    UpdateTriggerInstanceResponse,
)
from appconnect.webhook_signature import verify_webhook_signature

__version__ = "0.1.0"

__all__ = [
    "AppConnectClient",
    "SyncAppConnectClient",
    "AppConnectError",
    "ConnectedLinkExchangeResponse",
    "CreateLinkTokenResponse",
    "Delivery",
    "DeliveryAttempt",
    "ExchangeLinkTokenResponse",
    "GetTriggerInstanceResponse",
    "ListDeliveriesResponse",
    "ListToolsResponse",
    "ListTriggerDefinitionsResponse",
    "ListTriggerInstancesResponse",
    "PendingLinkExchangeResponse",
    "SearchToolsResponse",
    "SubscribeTriggerResponse",
    "TokenResponse",
    "Tool",
    "ToolExecutionResponse",
    "ToolInputSchema",
    "TriggerDefinition",
    "TriggerInstance",
    "UnsubscribeTriggerResponse",
    "UpdateTriggerInstanceResponse",
    "verify_webhook_signature",
    "__version__",
]
