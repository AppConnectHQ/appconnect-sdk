import { describe, expect, it } from "vitest";
import type { AppConnectTool } from "../src/index";
import { mockModelFinalTurn, mockModelTurn, pickMockTool, type ChatMessage } from "./mock-model";

function makeTool(overrides: Partial<AppConnectTool> = {}): AppConnectTool {
  return {
    id: "google_calendar_list_events",
    service: "google-calendar",
    serviceName: "Google Calendar",
    name: "list_events",
    displayName: "List Events",
    description: "List calendar events",
    method: "GET",
    inputSchema: { type: "object", properties: {}, required: [] },
    ...overrides,
  };
}

describe("pickMockTool", () => {
  it("prefers a GET tool with no required parameters over one requiring args", () => {
    const tools = [
      makeTool({
        id: "google_calendar_get_event",
        method: "GET",
        inputSchema: { type: "object", properties: {}, required: ["calendarId", "eventId"] },
      }),
      makeTool({
        id: "google_calendar_list_calendars",
        method: "GET",
        inputSchema: { type: "object", properties: {} },
      }),
    ];
    expect(pickMockTool(tools)?.id).toBe("google_calendar_list_calendars");
  });

  it("falls back to the first GET tool when every GET tool requires parameters", () => {
    const tools = [
      makeTool({
        id: "google_calendar_get_event",
        method: "GET",
        inputSchema: { type: "object", properties: {}, required: ["calendarId", "eventId"] },
      }),
      makeTool({ id: "github_create_issue", method: "POST" }),
    ];
    expect(pickMockTool(tools)?.id).toBe("google_calendar_get_event");
  });

  it("returns null when no tool is GET", () => {
    const tools = [makeTool({ id: "github_create_issue", method: "POST" })];
    expect(pickMockTool(tools)).toBeNull();
  });

  it("returns null for an empty tool list", () => {
    expect(pickMockTool([])).toBeNull();
  });
});

describe("mockModelTurn", () => {
  it("emits a tool_calls turn targeting the picked GET tool with empty arguments", () => {
    const tools = [makeTool({ id: "google_calendar_list_events", method: "GET" })];
    const turn = mockModelTurn(tools);
    expect(turn.content).toBeNull();
    expect(turn.tool_calls).toEqual([
      { id: "mock-call-1", function: { name: "google_calendar_list_events", arguments: "{}" } },
    ]);
  });

  it("never selects a mutating (non-GET) tool, and explains why in content", () => {
    const tools = [makeTool({ id: "github_create_issue", method: "POST" })];
    const turn = mockModelTurn(tools);
    expect(turn.tool_calls).toBeUndefined();
    expect(turn.content).toContain("no read-only (GET) tool is available");
    expect(turn.content).toContain("1 tool(s)");
  });
});

describe("mockModelFinalTurn", () => {
  it("summarizes the most recent tool result message", () => {
    const messages: ChatMessage[] = [
      { role: "user", content: "hi" },
      { role: "tool", tool_call_id: "mock-call-1", content: JSON.stringify({ items: [] }) },
    ];
    const turn = mockModelFinalTurn(messages);
    expect(turn.content).toContain('{"items":[]}');
  });

  it("truncates long tool results", () => {
    const longContent = "x".repeat(500);
    const messages: ChatMessage[] = [
      { role: "tool", tool_call_id: "mock-call-1", content: longContent },
    ];
    const turn = mockModelFinalTurn(messages);
    expect(turn.content).toContain("...");
    expect(turn.content!.length).toBeLessThan(longContent.length);
  });

  it("reports nothing to summarize when no tool message is present", () => {
    const turn = mockModelFinalTurn([{ role: "user", content: "hi" }]);
    expect(turn.content).toBe("Mock mode: no tool was called, nothing to summarize.");
  });
});
