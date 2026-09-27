"""Unit tests for appconnect.framework.langchain."""

from __future__ import annotations

import sys
from typing import cast
from unittest.mock import patch

import pytest
from _framework_fixtures import SAMPLE_TOOLS, make_mock_client
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, ValidationError

from appconnect.framework.langchain import to_langchain_tools
from appconnect.types import ToolExecutionResponse


async def test_to_langchain_tools_builds_real_structured_tool_instances() -> None:
    client = make_mock_client()

    tools = await to_langchain_tools(client, "token-123")

    client.list_tools.assert_awaited_once_with("token-123")
    assert len(tools) == len(SAMPLE_TOOLS)
    for tool in tools:
        assert isinstance(tool, StructuredTool)


async def test_names_describes_and_enforces_required_fields_via_pydantic() -> None:
    client = make_mock_client()

    _, create_issue_tool, _ = await to_langchain_tools(client, "token-123")

    assert create_issue_tool.name == "github_oauth_create_issue"
    assert create_issue_tool.description == "Create a new issue in a repository."

    # args_schema is a dynamically created pydantic model (see
    # `_create_pydantic_model`); cast narrows it from LangChain's broad
    # `type[BaseModel] | type[pydantic.v1.BaseModel] | dict | None` union
    # so `.model_validate` type-checks.
    args_schema = cast(type[BaseModel], create_issue_tool.args_schema)

    valid = args_schema.model_validate(
        {"owner": "octocat", "repo": "hello-world", "title": "Bug report"}
    )
    assert valid.owner == "octocat"  # type: ignore[attr-defined]

    with pytest.raises(ValidationError):
        args_schema.model_validate({"owner": "octocat"})


async def test_builds_empty_shape_model_when_input_schema_is_none() -> None:
    client = make_mock_client()

    _, _, s3_list_buckets_tool = await to_langchain_tools(client, "token-123")

    assert s3_list_buckets_tool.name == "aws_s3_list_buckets"
    assert s3_list_buckets_tool.description == "List S3 Buckets"
    args_schema = cast(type[BaseModel], s3_list_buckets_tool.args_schema)
    assert args_schema.model_validate({})


async def test_uses_pre_fetched_tools_without_calling_list_tools() -> None:
    client = make_mock_client()
    only_tool = SAMPLE_TOOLS[0]

    tools = await to_langchain_tools(client, "token-123", tools=[only_tool])

    client.list_tools.assert_not_awaited()
    assert len(tools) == 1
    assert tools[0].name == only_tool.id


async def test_invoking_tool_calls_execute_tool_and_stringifies_non_string_results() -> None:
    client = make_mock_client(
        execute_result=ToolExecutionResponse(
            tool="google_calendar_list_events", data={"events": []}
        )
    )

    list_events_tool, _, _ = await to_langchain_tools(client, "token-123")
    result = await list_events_tool.ainvoke({})

    client.execute_tool.assert_awaited_once_with("token-123", "google_calendar_list_events", {})
    assert result == '{"events": []}'


async def test_invoking_tool_passes_through_string_results_unchanged() -> None:
    client = make_mock_client(
        execute_result=ToolExecutionResponse(
            tool="github_oauth_create_issue", data="issue #42 created"
        )
    )

    _, create_issue_tool, _ = await to_langchain_tools(client, "token-123")
    result = await create_issue_tool.ainvoke(
        {"owner": "octocat", "repo": "hello-world", "title": "Bug report"}
    )

    assert result == "issue #42 created"


async def test_raises_helpful_import_error_when_langchain_core_is_unavailable() -> None:
    client = make_mock_client()

    with (
        patch.dict(sys.modules, {"langchain_core.tools": None}),
        pytest.raises(ImportError, match="pip install appconnect\\[langchain\\]"),
    ):
        await to_langchain_tools(client, "token-123")
