# appconnect (Python SDK)

Python client for the [AppConnectHQ](https://appconnecthq.com) unified connector
platform. Mirrors `@appconnecthq/sdk` (the TypeScript SDK in `../typescript`) 1:1:
same endpoints, same request/response shapes, one error type.

## Install

```bash
pip install appconnect
# or, from a checkout of this repo:
uv pip install -e python
```

## Documentation

Guides and the full API reference live in [`docs/`](https://github.com/AppConnectHQ/appconnect-sdk/tree/main/docs).
Release notes are in [`CHANGELOG.md`](https://github.com/AppConnectHQ/appconnect-sdk/blob/main/python/CHANGELOG.md).

## Usage

```python
import asyncio
import os
from appconnect import AppConnectClient

async def main() -> None:
    async with AppConnectClient(
        base_url=os.environ["PRODUCTION_API_ORIGIN"],
        client_id="your_client_id",
        client_secret="your_client_secret",
    ) as client:
        link = await client.create_link_token(
            user_id="user_123",
            redirect_uri="https://yourapp.com/callback",
        )
        print(link.link_url)

        tools = await client.list_tools(access_token="apphq_...")
        result = await client.execute_tool(
            access_token="apphq_...",
            tool="google_calendar_list_events",
            params={"calendarId": "primary"},
        )
        print(result.data)

asyncio.run(main())
```

A synchronous twin is available for non-async callers:

```python
from appconnect import SyncAppConnectClient

with SyncAppConnectClient(
    base_url=os.environ["PRODUCTION_API_ORIGIN"],
    client_id="your_client_id",
    client_secret="your_client_secret",
) as client:
    tools = client.list_tools(access_token="apphq_...")
```

`base_url` / `client_id` / `client_secret` can also be supplied via the
`APPCONNECT_BASE_URL` / `APPCONNECT_CLIENT_ID` / `APPCONNECT_CLIENT_SECRET`
environment variables instead of constructor arguments.

## Errors

Every failure -- HTTP error responses, `{"success": false}` API payloads, and
network-level errors -- raises a single `appconnect.AppConnectError` with
`.status` (0 for client-side/network failures) and an optional `.code`.

## Framework adapters

`appconnect.framework` maps AppConnect tools to framework-native shapes and
wires execution back through `execute_tool`. `openai`/`anthropic` need no extra
runtime dependency (`pip install appconnect` is enough); `langchain` needs
the `langchain` extra (`pip install appconnect[langchain]`).

```python
from appconnect import AppConnectClient
from appconnect.framework.openai import execute_openai_tool_call, to_openai_tools

async with AppConnectClient(...) as client:
    tools = await to_openai_tools(client, access_token="apphq_...")
    # pass `tools` to your OpenAI chat-completions call's `tools=` param;
    # for each returned tool_call, append the assistant message it produced:
    message = await execute_openai_tool_call(client, "apphq_...", tool_call)
```

`appconnect.framework.anthropic` mirrors this with `to_anthropic_tools` /
`execute_anthropic_tool_use` (Anthropic's `input_schema` +
`tool_use`/`tool_result` shapes). `appconnect.framework.langchain`'s
`to_langchain_tools` builds real `langchain_core.tools.StructuredTool`
instances (a dynamic Pydantic model enforces each tool's JSON Schema at
runtime) -- raises a helpful `ImportError` if `langchain-core` isn't
installed.

## Development

```bash
cd python
uv venv
uv pip install -e ".[dev]"
uv run pytest
uv run ruff check .
uv run mypy src
```

`dev` includes `langchain-core` so the full test suite (including
`tests/test_framework_langchain.py`) runs from a plain `.[dev]` install.
