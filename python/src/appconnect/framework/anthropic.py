"""Anthropic Messages API tool-use adapter.

A near-passthrough JSON Schema mapper plus execute glue wired through
`execute_tool`. Mirrors `typescript/src/framework/anthropic.ts` 1:1 (note
`input_schema`, not `parameters`, and `tool_use`/`tool_result` content
blocks instead of OpenAI's `tool_calls`/`{role: "tool"}` messages). No
extra runtime dependency is needed (the `anthropic` package itself is never
imported), matching the empty `anthropic` extra reserved in `pyproject.toml`.
"""

from __future__ import annotations

import json
from typing import Any, Literal, TypedDict

from appconnect.client import AppConnectClient
from appconnect.types import Tool


class AnthropicInputSchema(TypedDict, total=False):
    """JSON Schema object shape Anthropic expects under `input_schema`."""

    type: Literal["object"]
    properties: dict[str, Any]
    required: list[str]


class AnthropicTool(TypedDict):
    """A tool in Anthropic Messages API tool-use shape."""

    name: str
    description: str
    input_schema: AnthropicInputSchema


class AnthropicToolUseBlock(TypedDict):
    """A `tool_use` content block from an Anthropic assistant message."""

    type: Literal["tool_use"]
    id: str
    name: str
    input: dict[str, Any]


class AnthropicToolResultBlock(TypedDict):
    """The `tool_result` content block Anthropic expects in the following
    user turn."""

    type: Literal["tool_result"]
    tool_use_id: str
    content: str


async def to_anthropic_tools(
    client: AppConnectClient,
    access_token: str,
    tools: list[Tool] | None = None,
) -> list[AnthropicTool]:
    """Maps AppConnect tools to Anthropic Messages API tool-use tools. Pass
    pre-fetched `tools` (e.g. from a prior `list_tools()` call) to skip a
    round trip.
    """
    resolved = tools if tools is not None else await client.list_tools(access_token)
    return [_to_anthropic_tool(tool) for tool in resolved]


def _to_anthropic_tool(tool: Tool) -> AnthropicTool:
    schema = tool.inputSchema
    input_schema: AnthropicInputSchema = {
        "type": "object",
        "properties": (schema.properties if schema else None) or {},
    }
    required = schema.required if schema else None
    if required is not None:
        input_schema["required"] = required
    return {
        "name": tool.id,
        "description": tool.description or tool.displayName,
        "input_schema": input_schema,
    }


async def execute_anthropic_tool_use(
    client: AppConnectClient,
    access_token: str,
    tool_use: AnthropicToolUseBlock,
) -> AnthropicToolResultBlock:
    """Executes a single Anthropic `tool_use` block via `execute_tool` and
    returns the `tool_result` content block to append to the next user
    turn.
    """
    result = await client.execute_tool(access_token, tool_use["name"], tool_use["input"])
    content = result.data if isinstance(result.data, str) else json.dumps(result.data)
    return {
        "type": "tool_result",
        "tool_use_id": tool_use["id"],
        "content": content,
    }
