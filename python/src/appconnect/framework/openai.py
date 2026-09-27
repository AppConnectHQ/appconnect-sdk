"""OpenAI chat-completions function-calling adapter.

A near-passthrough JSON Schema mapper -- AppConnect tools already carry
plain JSON Schema `input_schema` -- plus execute glue wired through
`execute_tool`. Mirrors `typescript/src/framework/openai.ts` 1:1: no extra
runtime dependency is needed (the `openai` package itself is never
imported), matching the empty `openai` extra reserved in `pyproject.toml`.
"""

from __future__ import annotations

import json
from typing import Any, Literal, TypedDict

from appconnect.client import AppConnectClient
from appconnect.types import Tool


class OpenAIFunctionParameters(TypedDict, total=False):
    """JSON Schema object shape OpenAI expects under `function.parameters`."""

    type: Literal["object"]
    properties: dict[str, Any]
    required: list[str]


class OpenAIFunctionDef(TypedDict):
    name: str
    description: str
    parameters: OpenAIFunctionParameters


class OpenAIFunctionTool(TypedDict):
    """A tool in OpenAI chat-completions function-calling shape."""

    type: Literal["function"]
    function: OpenAIFunctionDef


class OpenAIToolCallFunction(TypedDict):
    name: str
    arguments: str


class OpenAIToolCall(TypedDict):
    """An OpenAI chat-completions tool call, as found on an assistant
    message's `tool_calls`."""

    id: str
    function: OpenAIToolCallFunction


class OpenAIToolResultMessage(TypedDict):
    """The `{role: "tool", ...}` message OpenAI expects appended after a
    tool call runs."""

    role: Literal["tool"]
    tool_call_id: str
    content: str


async def to_openai_tools(
    client: AppConnectClient,
    access_token: str,
    tools: list[Tool] | None = None,
) -> list[OpenAIFunctionTool]:
    """Maps AppConnect tools to OpenAI chat-completions function-calling
    tools. Pass pre-fetched `tools` (e.g. from a prior `list_tools()` call)
    to skip a round trip.
    """
    resolved = tools if tools is not None else await client.list_tools(access_token)
    return [_to_openai_tool(tool) for tool in resolved]


def _to_openai_tool(tool: Tool) -> OpenAIFunctionTool:
    schema = tool.inputSchema
    parameters: OpenAIFunctionParameters = {
        "type": "object",
        "properties": (schema.properties if schema else None) or {},
    }
    required = schema.required if schema else None
    if required is not None:
        parameters["required"] = required
    return {
        "type": "function",
        "function": {
            "name": tool.id,
            "description": tool.description or tool.displayName,
            "parameters": parameters,
        },
    }


async def execute_openai_tool_call(
    client: AppConnectClient,
    access_token: str,
    tool_call: OpenAIToolCall,
) -> OpenAIToolResultMessage:
    """Executes a single OpenAI tool call via `execute_tool` and returns the
    `{role: "tool", ...}` message to append to the conversation.
    """
    args = json.loads(tool_call["function"]["arguments"] or "{}")
    result = await client.execute_tool(access_token, tool_call["function"]["name"], args)
    content = result.data if isinstance(result.data, str) else json.dumps(result.data)
    return {
        "role": "tool",
        "tool_call_id": tool_call["id"],
        "content": content,
    }
