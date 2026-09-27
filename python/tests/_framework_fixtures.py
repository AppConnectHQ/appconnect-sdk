"""Shared fixtures for framework adapter tests (openai/anthropic/langchain).

Named with a leading underscore so pytest's default `test_*.py` collection
pattern skips it -- it is imported by the actual test modules, not
collected itself.

Mirrors `typescript/src/framework/test-utils.ts`'s `SAMPLE_TOOLS`: a GET
tool with no input properties, a POST tool with required fields, and a tool
with a null description/inputSchema (both nullable per `Tool` in
`appconnect/types.py`).
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, create_autospec

from appconnect.client import AppConnectClient
from appconnect.types import Tool, ToolExecutionResponse, ToolInputSchema

SAMPLE_TOOLS: list[Tool] = [
    Tool(
        id="google_calendar_list_events",
        service="google-calendar",
        serviceName="Google Calendar",
        name="list_events",
        displayName="List Events",
        description="List upcoming events on the user's calendar.",
        method="GET",
        inputSchema=ToolInputSchema(type="object", properties={}, required=[]),
    ),
    Tool(
        id="github_oauth_create_issue",
        service="github-oauth",
        serviceName="GitHub",
        name="create_issue",
        displayName="Create Issue",
        description="Create a new issue in a repository.",
        method="POST",
        inputSchema=ToolInputSchema(
            type="object",
            properties={
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "title": {"type": "string"},
                "body": {"type": "string"},
            },
            required=["owner", "repo", "title"],
        ),
    ),
    Tool(
        id="aws_s3_list_buckets",
        service="aws",
        serviceName="AWS",
        name="s3_list_buckets",
        displayName="List S3 Buckets",
        description=None,
        method="GET",
        inputSchema=None,
    ),
]


def make_mock_client(
    tools: list[Tool] | None = None,
    execute_result: ToolExecutionResponse | None = None,
) -> Any:
    """Builds an autospec'd `AppConnectClient` exposing only `list_tools`/
    `execute_tool` as awaitable mocks -- adapters never touch other members.

    Typed `-> Any` (rather than `-> AppConnectClient`) on purpose: the
    return value is a `MagicMock`, not a real `AppConnectClient` instance,
    and callers need unrestricted access to mock-only attributes like
    `.list_tools.assert_awaited_once_with(...)`.
    """
    client = create_autospec(AppConnectClient, instance=True)
    client.list_tools = AsyncMock(return_value=tools if tools is not None else SAMPLE_TOOLS)
    client.execute_tool = AsyncMock(
        return_value=execute_result or ToolExecutionResponse(tool="some_tool", data={"ok": True})
    )
    return client
