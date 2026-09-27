import { describe, expect, it } from "vitest";
import { toAISDKTools } from "./ai-sdk";
import { createMockClient, SAMPLE_TOOLS } from "./test-utils";

describe("toAISDKTools", () => {
  it("maps AppConnectTool fixtures to an AI SDK v5 ToolSet keyed by tool id", async () => {
    const { client, listTools } = createMockClient();

    const toolSet = await toAISDKTools({ client, accessToken: "token-123" });

    expect(listTools).toHaveBeenCalledWith("token-123");
    expect(Object.keys(toolSet)).toEqual(SAMPLE_TOOLS.map((t) => t.id));

    const listEvents = toolSet.google_calendar_list_events;
    expect(listEvents.description).toBe("List upcoming events on the user's calendar.");
    expect(listEvents.inputSchema).toMatchObject({
      jsonSchema: { type: "object", properties: {}, required: [] },
    });

    const createIssue = toolSet.github_oauth_create_issue;
    expect(createIssue.description).toBe("Create a new issue in a repository.");
    expect(createIssue.inputSchema).toMatchObject({
      jsonSchema: {
        type: "object",
        properties: {
          owner: { type: "string" },
          repo: { type: "string" },
          title: { type: "string" },
          body: { type: "string" },
        },
        required: ["owner", "repo", "title"],
      },
    });
  });

  it("falls back to displayName and an empty-object schema when description/inputSchema are null", async () => {
    const { client } = createMockClient();

    const toolSet = await toAISDKTools({ client, accessToken: "token-123" });
    const s3ListBuckets = toolSet.aws_s3_list_buckets;

    expect(s3ListBuckets.description).toBe("List S3 Buckets");
    expect(s3ListBuckets.inputSchema).toMatchObject({
      jsonSchema: { type: "object", properties: {}, required: undefined },
    });
  });

  it("uses pre-fetched tools without calling listTools", async () => {
    const { client, listTools } = createMockClient();
    const [onlyTool] = SAMPLE_TOOLS;

    const toolSet = await toAISDKTools({
      client,
      accessToken: "token-123",
      tools: [onlyTool],
    });

    expect(listTools).not.toHaveBeenCalled();
    expect(Object.keys(toolSet)).toEqual([onlyTool.id]);
  });

  it("executes a tool call via executeTool and returns the raw result data", async () => {
    const { client, executeTool } = createMockClient({
      executeResult: { tool: "google_calendar_list_events", data: { events: [] } },
    });

    const toolSet = await toAISDKTools({ client, accessToken: "token-123" });
    const listEvents = toolSet.google_calendar_list_events;
    if (!listEvents.execute) {
      throw new Error("expected tool to have an execute function");
    }

    const result = await listEvents.execute(
      { maxResults: 5 },
      { toolCallId: "call_1", messages: [], context: undefined },
    );

    expect(executeTool).toHaveBeenCalledWith("token-123", "google_calendar_list_events", {
      maxResults: 5,
    });
    expect(result).toEqual({ events: [] });
  });

  it("defaults to an empty object when the tool is executed with no input", async () => {
    const { client, executeTool } = createMockClient();

    const toolSet = await toAISDKTools({ client, accessToken: "token-123" });
    const s3ListBuckets = toolSet.aws_s3_list_buckets;
    if (!s3ListBuckets.execute) {
      throw new Error("expected tool to have an execute function");
    }

    await s3ListBuckets.execute(undefined, {
      toolCallId: "call_2",
      messages: [],
      context: undefined,
    });

    expect(executeTool).toHaveBeenCalledWith("token-123", "aws_s3_list_buckets", {});
  });
});
