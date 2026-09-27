"""End-to-end example: list AppConnect tools for a connected user, adapt
them to OpenAI chat-completions function-calling format, run a tool-calling
chat loop against a real OpenAI model, and execute whatever tool call the
model requests back through AppConnect's `execute_tool`.

This is the "list -> adapt -> model -> execute" loop, driven against the
AppConnect API origin configured through `PRODUCTION_API_ORIGIN`.

Usage (from `python/`, inside the project venv):
    uv run python -m examples.openai_agent
    uv run python -m examples.openai_agent --mock

Required env var:
    APPCONNECT_ACCESS_TOKEN  Bearer token for a connected AppConnect user
                             (returned by exchange_link_token() after a
                             user completes a hosted Link session)

Optional env vars:
    PRODUCTION_API_ORIGIN    Origin supplied during onboarding
    OPENAI_API_KEY           Real OpenAI key. When absent (or --mock is
                             passed) the script substitutes a deterministic
                             mocked model response (see ./mock_model.py) so
                             the example always runs end-to-end without
                             spending API credits or requiring an LLM key.
    OPENAI_MODEL             Default: gpt-4o-mini
    APPCONNECT_PROMPT        User prompt sent to the model.

See ./README.md for a full walkthrough.
"""

from __future__ import annotations

import asyncio
import os
import sys

import httpx

from appconnect import AppConnectClient
from appconnect.framework.openai import (
    OpenAIFunctionTool,
    execute_openai_tool_call,
    to_openai_tools,
)

from .mock_model import AssistantTurn, ChatMessage, mock_model_final_turn, mock_model_turn


async def call_openai(
    api_key: str,
    model: str,
    messages: list[ChatMessage],
    tools: list[OpenAIFunctionTool],
) -> AssistantTurn:
    async with httpx.AsyncClient(timeout=60) as http_client:
        response = await http_client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": model, "messages": messages, "tools": tools or None},
        )
    payload = response.json()
    if response.is_error:
        raise RuntimeError(f"OpenAI request failed ({response.status_code}): {payload}")

    choices = payload.get("choices") or []
    if not choices:
        raise RuntimeError(f"OpenAI response missing choices[0].message: {payload}")

    message = choices[0]["message"]
    return AssistantTurn(content=message.get("content"), tool_calls=message.get("tool_calls"))


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable {name}. See examples/README.md for setup."
        )
    return value


async def main() -> None:
    mock_flag = "--mock" in sys.argv
    base_url = os.environ["PRODUCTION_API_ORIGIN"]
    access_token = require_env("APPCONNECT_ACCESS_TOKEN")
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    use_mock = mock_flag or not openai_api_key
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    prompt = os.environ.get(
        "APPCONNECT_PROMPT",
        "Look at the tools you have access to via AppConnect and, if there's a safe "
        "read-only (list/get) tool available, call it to show me a small sample of data. "
        "Otherwise just summarize what tools you have.",
    )

    # client_id/client_secret are only used by the OAuth/link-token
    # endpoints, not by list_tools/execute_tool -- placeholders are fine here.
    async with AppConnectClient(
        base_url=base_url, client_id="example", client_secret="example"
    ) as client:
        print(f"[1/4] Listing AppConnect tools from {base_url}...")
        tools = await client.list_tools(access_token)
        print(f"      -> {len(tools)} tool(s) available")

        print("[2/4] Adapting tools to OpenAI function-calling format...")
        openai_tools = await to_openai_tools(client, access_token, tools)

        messages: list[ChatMessage] = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant with access to the user's connected "
                    "services via AppConnect tools."
                ),
            },
            {"role": "user", "content": prompt},
        ]

        mode_label = " (mocked -- no OPENAI_API_KEY / --mock)" if use_mock else f" ({model})"
        print(f"[3/4] Calling the model{mode_label}...")
        if use_mock:
            first_turn = mock_model_turn(tools)
        else:
            assert openai_api_key is not None
            first_turn = await call_openai(openai_api_key, model, messages, openai_tools)

        messages.append(
            {
                "role": "assistant",
                "content": first_turn.content,
                "tool_calls": first_turn.tool_calls,
            }
        )

        if not first_turn.tool_calls:
            print("\nFinal assistant message (no tool calls):\n")
            print(first_turn.content)
            return

        print(f"[4/4] Executing {len(first_turn.tool_calls)} tool call(s) via AppConnect...")
        for tool_call in first_turn.tool_calls:
            print(f"      -> {tool_call['function']['name']}({tool_call['function']['arguments']})")
            result_message = await execute_openai_tool_call(client, access_token, tool_call)
            messages.append(result_message)

        if use_mock:
            final_turn = mock_model_final_turn(messages)
        else:
            assert openai_api_key is not None
            final_turn = await call_openai(openai_api_key, model, messages, openai_tools)

        print("\nFinal assistant message:\n")
        print(final_turn.content)


if __name__ == "__main__":
    asyncio.run(main())
