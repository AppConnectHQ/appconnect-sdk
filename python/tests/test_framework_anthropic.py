"""Unit tests for appconnect.framework.anthropic."""

from __future__ import annotations

from _framework_fixtures import SAMPLE_TOOLS, make_mock_client

from appconnect.framework.anthropic import execute_anthropic_tool_use, to_anthropic_tools
from appconnect.types import ToolExecutionResponse


async def test_to_anthropic_tools_maps_sample_fixtures() -> None:
    client = make_mock_client()

    result = await to_anthropic_tools(client, "token-123")

    client.list_tools.assert_awaited_once_with("token-123")
    assert result == [
        {
            "name": "google_calendar_list_events",
            "description": "List upcoming events on the user's calendar.",
            "input_schema": {"type": "object", "properties": {}, "required": []},
        },
        {
            "name": "github_oauth_create_issue",
            "description": "Create a new issue in a repository.",
            "input_schema": {
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
        {
            "name": "aws_s3_list_buckets",
            "description": "List S3 Buckets",
            "input_schema": {"type": "object", "properties": {}},
        },
    ]
    assert "required" not in result[2]["input_schema"]


async def test_to_anthropic_tools_uses_pre_fetched_tools_without_calling_list_tools() -> None:
    client = make_mock_client()
    only_tool = SAMPLE_TOOLS[1]

    result = await to_anthropic_tools(client, "token-123", tools=[only_tool])

    client.list_tools.assert_not_awaited()
    assert len(result) == 1
    assert result[0]["name"] == only_tool.id


async def test_execute_anthropic_tool_use_calls_execute_tool_and_returns_result_block() -> None:
    client = make_mock_client(
        execute_result=ToolExecutionResponse(tool="github_oauth_create_issue", data={"number": 42})
    )

    block = await execute_anthropic_tool_use(
        client,
        "token-123",
        {
            "type": "tool_use",
            "id": "toolu_1",
            "name": "github_oauth_create_issue",
            "input": {"owner": "octocat", "repo": "hello-world", "title": "Bug report"},
        },
    )

    client.execute_tool.assert_awaited_once_with(
        "token-123",
        "github_oauth_create_issue",
        {"owner": "octocat", "repo": "hello-world", "title": "Bug report"},
    )
    assert block == {
        "type": "tool_result",
        "tool_use_id": "toolu_1",
        "content": '{"number": 42}',
    }


async def test_execute_anthropic_tool_use_passes_through_string_data_unchanged() -> None:
    client = make_mock_client(
        execute_result=ToolExecutionResponse(tool="some_tool", data="issue #42 created")
    )

    block = await execute_anthropic_tool_use(
        client, "token-123", {"type": "tool_use", "id": "toolu_2", "name": "some_tool", "input": {}}
    )

    assert block["content"] == "issue #42 created"
