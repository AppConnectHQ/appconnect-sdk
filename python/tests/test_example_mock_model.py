"""Unit tests for examples/mock_model.py's pure mock-turn logic."""

from __future__ import annotations

from appconnect.types import Tool
from examples.mock_model import ChatMessage, mock_model_final_turn, mock_model_turn, pick_mock_tool


def make_tool(**overrides: object) -> Tool:
    base: dict[str, object] = {
        "id": "google_calendar_list_events",
        "service": "google-calendar",
        "serviceName": "Google Calendar",
        "name": "list_events",
        "displayName": "List Events",
        "description": "List calendar events",
        "method": "GET",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    }
    base.update(overrides)
    return Tool.model_validate(base)


def test_pick_mock_tool_prefers_a_no_args_get_tool_over_one_requiring_args() -> None:
    tools = [
        make_tool(
            id="google_calendar_get_event",
            method="GET",
            inputSchema={"type": "object", "properties": {}, "required": ["calendarId", "eventId"]},
        ),
        make_tool(
            id="google_calendar_list_calendars",
            method="GET",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]
    picked = pick_mock_tool(tools)
    assert picked is not None
    assert picked.id == "google_calendar_list_calendars"


def test_pick_mock_tool_falls_back_to_first_get_tool_when_all_require_args() -> None:
    tools = [
        make_tool(
            id="google_calendar_get_event",
            method="GET",
            inputSchema={"type": "object", "properties": {}, "required": ["calendarId", "eventId"]},
        ),
        make_tool(id="github_create_issue", method="POST"),
    ]
    picked = pick_mock_tool(tools)
    assert picked is not None
    assert picked.id == "google_calendar_get_event"


def test_pick_mock_tool_returns_none_when_no_get_tool() -> None:
    tools = [make_tool(id="github_create_issue", method="POST")]
    assert pick_mock_tool(tools) is None


def test_pick_mock_tool_returns_none_for_empty_list() -> None:
    assert pick_mock_tool([]) is None


def test_mock_model_turn_emits_tool_call_for_picked_get_tool() -> None:
    tools = [make_tool(id="google_calendar_list_events", method="GET")]
    turn = mock_model_turn(tools)
    assert turn.content is None
    assert turn.tool_calls == [
        {
            "id": "mock-call-1",
            "function": {"name": "google_calendar_list_events", "arguments": "{}"},
        }
    ]


def test_mock_model_turn_never_calls_a_mutating_tool() -> None:
    tools = [make_tool(id="github_create_issue", method="POST")]
    turn = mock_model_turn(tools)
    assert turn.tool_calls is None
    assert turn.content is not None
    assert "no read-only (GET) tool is available" in turn.content
    assert "1 tool(s)" in turn.content


def test_mock_model_final_turn_summarizes_most_recent_tool_result() -> None:
    messages: list[ChatMessage] = [
        {"role": "user", "content": "hi"},
        {"role": "tool", "tool_call_id": "mock-call-1", "content": '{"items": []}'},
    ]
    turn = mock_model_final_turn(messages)
    assert turn.content is not None
    assert '{"items": []}' in turn.content


def test_mock_model_final_turn_truncates_long_results() -> None:
    long_content = "x" * 500
    messages: list[ChatMessage] = [
        {"role": "tool", "tool_call_id": "mock-call-1", "content": long_content}
    ]
    turn = mock_model_final_turn(messages)
    assert turn.content is not None
    assert "..." in turn.content
    assert len(turn.content) < len(long_content)


def test_mock_model_final_turn_reports_nothing_to_summarize_without_a_tool_message() -> None:
    turn = mock_model_final_turn([{"role": "user", "content": "hi"}])
    assert turn.content == "Mock mode: no tool was called, nothing to summarize."
