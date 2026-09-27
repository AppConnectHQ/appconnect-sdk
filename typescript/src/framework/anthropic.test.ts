import { describe, expect, it } from "vitest";
import { executeAnthropicToolUse, toAnthropicTools } from "./anthropic";
import { createMockClient, SAMPLE_TOOLS } from "./test-utils";

describe("toAnthropicTools", () => {
  it("maps AppConnectTool fixtures to Anthropic tool-use shape (input_schema, not parameters)", async () => {
    const { client, listTools } = createMockClient();

    const result = await toAnthropicTools({ client, accessToken: "token-123" });

    expect(listTools).toHaveBeenCalledWith("token-123");
    expect(result).toEqual([
      {
        name: "google_calendar_list_events",
        description: "List upcoming events on the user's calendar.",
        input_schema: { type: "object", properties: {}, required: [] },
      },
      {
        name: "github_oauth_create_issue",
        description: "Create a new issue in a repository.",
        input_schema: {
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
      {
        name: "aws_s3_list_buckets",
        description: "List S3 Buckets",
        input_schema: { type: "object", properties: {}, required: undefined },
      },
    ]);
  });

  it("uses pre-fetched tools without calling listTools", async () => {
    const { client, listTools } = createMockClient();
    const [, githubTool] = SAMPLE_TOOLS;

    const result = await toAnthropicTools({
      client,
      accessToken: "token-123",
      tools: [githubTool],
    });

    expect(listTools).not.toHaveBeenCalled();
    expect(result).toHaveLength(1);
    expect(result[0].name).toBe(githubTool.id);
  });
});

describe("executeAnthropicToolUse", () => {
  it("calls executeTool with the tool_use input and returns a tool_result block", async () => {
    const { client, executeTool } = createMockClient({
      executeResult: { tool: "github_oauth_create_issue", data: { number: 42 } },
    });

    const block = await executeAnthropicToolUse(
      { client, accessToken: "token-123" },
      {
        type: "tool_use",
        id: "toolu_1",
        name: "github_oauth_create_issue",
        input: { owner: "acme", repo: "widgets", title: "Bug" },
      },
    );

    expect(executeTool).toHaveBeenCalledWith("token-123", "github_oauth_create_issue", {
      owner: "acme",
      repo: "widgets",
      title: "Bug",
    });
    expect(block).toEqual({
      type: "tool_result",
      tool_use_id: "toolu_1",
      content: JSON.stringify({ number: 42 }),
    });
  });

  it("passes through string data unchanged instead of double-encoding it", async () => {
    const { client } = createMockClient({
      executeResult: { tool: "some_tool", data: "already a string" },
    });

    const block = await executeAnthropicToolUse(
      { client, accessToken: "token-123" },
      { type: "tool_use", id: "toolu_2", name: "some_tool", input: {} },
    );

    expect(block.content).toBe("already a string");
  });
});
