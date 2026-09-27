"""Unit tests for appconnect.framework.openai."""

from __future__ import annotations

import json

from _framework_fixtures import SAMPLE_TOOLS, make_mock_client

from appconnect.framework.openai import execute_openai_tool_call, to_openai_tools
from appconnect.types import ToolExecutionResponse


async def test_to_openai_tools_maps_sample_fixtures() -> None:
    client = make_mock_client()

    result = await to_openai_tools(client, "token-123")

    client.list_tools.assert_awaited_once_with("token-123")
    assert result == [
        {
            "type": "function",
            "function": {
                "name": "google_calendar_list_events",
                "description": "List upcoming events on the user's calendar.",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "github_oauth_create_issue",
                "description": "Create a new issue in a repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "owner": {"type": "string"},
                        "repo": {"type": "string"},
                        "title": {"type": "string"},
                        "body": {"type": "string"},
                    },
                    "required": ["owner", "repo", "title"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "aws_s3_list_buckets",
                # Falls back to displayName when description is None.
                "description": "List S3 Buckets",
                "parameters": {"type": "object", "properties": {}},
            },
        },
    ]
    # "required" is omitted entirely (not set to []) when inputSchema is None.
    assert "required" not in result[2]["function"]["parameters"]


async def test_to_openai_tools_uses_pre_fetched_tools_without_calling_list_tools() -> None:
    client = make_mock_client()
    only_tool = SAMPLE_TOOLS[0]

    result = await to_openai_tools(client, "token-123", tools=[only_tool])

    client.list_tools.assert_not_awaited()
    assert len(result) == 1
    assert result[0]["function"]["name"] == only_tool.id


async def test_execute_openai_tool_call_parses_args_and_calls_execute_tool() -> None:
    client = make_mock_client(
        execute_result=ToolExecutionResponse(
            tool="google_calendar_list_events", data={"events": []}
        )
    )

    message = await execute_openai_tool_call(
        client,
        "token-123",
        {
            "id": "call_1",
            "function": {
                "name": "google_calendar_list_events",
                "arguments": json.dumps({"maxResults": 5}),
            },
        },
    )

    client.execute_tool.assert_awaited_once_with(
        "token-123", "google_calendar_list_events", {"maxResults": 5}
    )
    assert message == {
        "role": "tool",
        "tool_call_id": "call_1",
        "content": json.dumps({"events": []}),
    }


async def test_execute_openai_tool_call_defaults_empty_arguments_to_empty_dict() -> None:
    client = make_mock_client()

    await execute_openai_tool_call(
        client,
        "token-123",
        {"id": "call_2", "function": {"name": "aws_s3_list_buckets", "arguments": ""}},
    )

    client.execute_tool.assert_awaited_once_with("token-123", "aws_s3_list_buckets", {})


async def test_execute_openai_tool_call_passes_through_string_data_unchanged() -> None:
    client = make_mock_client(
        execute_result=ToolExecutionResponse(tool="some_tool", data="already a string")
    )

    message = await execute_openai_tool_call(
        client, "token-123", {"id": "call_3", "function": {"name": "some_tool", "arguments": "{}"}}
    )

    assert message["content"] == "already a string"
