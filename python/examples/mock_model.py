"""Deterministic stand-ins for an LLM's turns, used by `openai_agent.py`
when no LLM API key is available (or `--mock` is passed) so the example
always runs end-to-end without spending API credits or requiring
credentials. Kept separate from the runnable script so this pure logic can
be unit tested without touching the network or environment variables.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypedDict

from appconnect.framework.openai import OpenAIToolCall, OpenAIToolResultMessage
from appconnect.types import Tool


class SystemOrUserMessage(TypedDict):
    role: Literal["system", "user"]
    content: str


class AssistantMessage(TypedDict):
    role: Literal["assistant"]
    content: str | None
    tool_calls: list[OpenAIToolCall] | None


ChatMessage = SystemOrUserMessage | AssistantMessage | OpenAIToolResultMessage


@dataclass
class AssistantTurn:
    """A model turn: either free-text `content` or one or more `tool_calls`."""

    content: str | None
    tool_calls: list[OpenAIToolCall] | None = None


def pick_mock_tool(tools: list[Tool]) -> Tool | None:
    """Picks a safe (read-only) tool to demonstrate the execute step in mock
    mode. Prefers a GET tool with no required parameters (so calling it
    with `{}` succeeds), falling back to the first GET tool otherwise.
    """
    read_only_tools = [tool for tool in tools if tool.method == "GET"]
    no_args_tool = next(
        (tool for tool in read_only_tools if not (tool.inputSchema and tool.inputSchema.required)),
        None,
    )
    if no_args_tool is not None:
        return no_args_tool
    return read_only_tools[0] if read_only_tools else None


def mock_model_turn(tools: list[Tool]) -> AssistantTurn:
    """Deterministic stand-in for the model's first turn. Only ever "calls" a
    GET (read-only) tool, so mock mode never mutates the connected user's
    data.
    """
    picked = pick_mock_tool(tools)
    if picked is None:
        return AssistantTurn(
            content=(
                f"Mock mode: no read-only (GET) tool is available among the {len(tools)} "
                "tool(s) I can see, so I won't call anything. Set an LLM API key (or drop "
                "--mock) to use a real model."
            )
        )
    return AssistantTurn(
        content=None,
        tool_calls=[{"id": "mock-call-1", "function": {"name": picked.id, "arguments": "{}"}}],
    )


def mock_model_final_turn(messages: list[ChatMessage]) -> AssistantTurn:
    """Deterministic stand-in for the model's follow-up turn after a tool
    result comes back."""
    tool_result: OpenAIToolResultMessage | None = None
    for message in reversed(messages):
        if message["role"] == "tool":
            tool_result = message
            break

    if tool_result is None:
        return AssistantTurn(content="Mock mode: no tool was called, nothing to summarize.")

    content = tool_result["content"]
    preview = content if len(content) <= 300 else f"{content[:300]}..."
    return AssistantTurn(content=f"Mock mode: executed the tool and got back: {preview}")
