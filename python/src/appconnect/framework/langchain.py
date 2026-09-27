"""LangChain adapter: real `StructuredTool` instances (not a duck-typed
plain-object shape) built via a dynamic Pydantic model generated from each
tool's JSON Schema.

Unlike MCP clients, which return content-block text that must be unwrapped,
AppConnect's `execute_tool` already returns parsed JSON
(`ToolExecutionResponse.data`), so there is no text-block unwrapping layer
here.

Only the `langchain_core.tools` import is guarded behind the optional
`langchain` extra (`pip install appconnect[langchain]`) -- it happens lazily
inside `to_langchain_tools` so importing this module (or
`appconnect.framework`) never requires langchain-core to be installed.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from appconnect.client import AppConnectClient
from appconnect.types import Tool

if TYPE_CHECKING:
    from langchain_core.tools import StructuredTool


async def to_langchain_tools(
    client: AppConnectClient,
    access_token: str,
    tools: list[Tool] | None = None,
) -> list[StructuredTool]:
    """Maps AppConnect tools to real LangChain `StructuredTool` instances.
    Pass pre-fetched `tools` (e.g. from a prior `list_tools()` call) to skip
    a round trip. Requires the `langchain` extra.
    """
    try:
        from langchain_core.tools import StructuredTool
    except ImportError as e:
        raise ImportError(
            "langchain-core is required for LangChain integration. "
            "Install with: pip install appconnect[langchain]"
        ) from e

    resolved = tools if tools is not None else await client.list_tools(access_token)
    langchain_tools: list[StructuredTool] = []

    for tool in resolved:
        schema = tool.inputSchema
        properties: dict[str, Any] = (schema.properties if schema else None) or {}
        required: list[str] = (schema.required if schema else None) or []

        args_schema = _create_pydantic_model(tool.id, properties, required)

        lc_tool = StructuredTool(
            name=tool.id,
            description=tool.description or tool.displayName,
            coroutine=_make_executor(client, access_token, tool.id),
            args_schema=args_schema,
        )
        langchain_tools.append(lc_tool)

    return langchain_tools


def _make_executor(client: AppConnectClient, access_token: str, tool_id: str) -> Any:
    async def call_tool(**kwargs: Any) -> str:
        result = await client.execute_tool(access_token, tool_id, kwargs)
        return result.data if isinstance(result.data, str) else json.dumps(result.data)

    return call_tool


def _create_pydantic_model(name: str, properties: dict[str, Any], required: list[str]) -> Any:
    from pydantic import create_model
    from pydantic.fields import FieldInfo

    fields: dict[str, Any] = {}

    for prop_name, prop_schema in properties.items():
        python_type = _json_schema_to_python_type(prop_schema)
        is_required = prop_name in required
        description = prop_schema.get("description", "") if isinstance(prop_schema, dict) else ""

        if is_required:
            fields[prop_name] = (python_type, FieldInfo(description=description))
        else:
            fields[prop_name] = (
                python_type | None,
                FieldInfo(default=None, description=description),
            )

    return create_model(f"{name}Args", **fields)


def _json_schema_to_python_type(schema: Any) -> type:
    if not isinstance(schema, dict):
        return str
    json_type = schema.get("type", "string")
    type_map: dict[str, type] = {
        "string": str,
        "integer": int,
        "number": float,
        "boolean": bool,
        "array": list,
        "object": dict,
    }
    return type_map.get(json_type, str)
