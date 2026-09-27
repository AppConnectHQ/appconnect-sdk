import { describe, expect, it } from "vitest";
import { executeOpenAIToolCall, toOpenAITools } from "./openai";
import { createMockClient, SAMPLE_TOOLS } from "./test-utils";

describe("toOpenAITools", () => {
  it("maps AppConnectTool fixtures to OpenAI function-calling shape", async () => {
    const { client, listTools } = createMockClient();

    const result = await toOpenAITools({ client, accessToken: "token-123" });

    expect(listTools).toHaveBeenCalledWith("token-123");
    expect(result).toEqual([
      {
        type: "function",
        function: {
          name: "google_calendar_list_events",
          description: "List upcoming events on the user's calendar.",
          parameters: { type: "object", properties: {}, required: [] },
        },
      },
      {
        type: "function",
        function: {
          name: "github_oauth_create_issue",
          description: "Create a new issue in a repository.",
          parameters: {
            type: "object",
            properties: {
              owner: { type: "string" },
              repo: { type: "string" },
              title: { type: "string" },
              body: { type: "string" },
            },
            required: ["owner", "repo", "title"],
          },
        },
      },
      {
        type: "function",
        function: {
          name: "aws_s3_list_buckets",
          // Falls back to displayName when description is null.
          description: "List S3 Buckets",
          parameters: { type: "object", properties: {}, required: undefined },
        },
      },
    ]);
  });

  it("uses pre-fetched tools without calling listTools", async () => {
    const { client, listTools } = createMockClient();
    const [onlyTool] = SAMPLE_TOOLS;

    const result = await toOpenAITools({
      client,
      accessToken: "token-123",
      tools: [onlyTool],
    });

    expect(listTools).not.toHaveBeenCalled();
    expect(result).toHaveLength(1);
    expect(result[0].function.name).toBe(onlyTool.id);
  });
});

describe("executeOpenAIToolCall", () => {
  it("parses arguments, calls executeTool, and returns a tool message", async () => {
    const { client, executeTool } = createMockClient({
      executeResult: { tool: "google_calendar_list_events", data: { events: [] } },
    });

    const message = await executeOpenAIToolCall(
      { client, accessToken: "token-123" },
      {
        id: "call_1",
        function: {
          name: "google_calendar_list_events",
          arguments: JSON.stringify({ maxResults: 5 }),
        },
      },
    );

    expect(executeTool).toHaveBeenCalledWith("token-123", "google_calendar_list_events", {
      maxResults: 5,
    });
    expect(message).toEqual({
      role: "tool",
      tool_call_id: "call_1",
      content: JSON.stringify({ events: [] }),
    });
  });

  it("defaults to an empty argument object when arguments string is empty", async () => {
    const { client, executeTool } = createMockClient();

    await executeOpenAIToolCall(
      { client, accessToken: "token-123" },
      { id: "call_2", function: { name: "aws_s3_list_buckets", arguments: "" } },
    );

    expect(executeTool).toHaveBeenCalledWith("token-123", "aws_s3_list_buckets", {});
  });

  it("passes through string data unchanged instead of double-encoding it", async () => {
    const { client } = createMockClient({
      executeResult: { tool: "some_tool", data: "already a string" },
    });

    const message = await executeOpenAIToolCall(
      { client, accessToken: "token-123" },
      { id: "call_3", function: { name: "some_tool", arguments: "{}" } },
    );

    expect(message.content).toBe("already a string");
  });
});
