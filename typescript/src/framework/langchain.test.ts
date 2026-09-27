import { DynamicStructuredTool } from "@langchain/core/tools";
import { describe, expect, it } from "vitest";
import { toLangChainTools } from "./langchain";
import { createMockClient, SAMPLE_TOOLS } from "./test-utils";

describe("toLangChainTools", () => {
  it("maps AppConnectTool fixtures to real DynamicStructuredTool instances", async () => {
    const { client, listTools } = createMockClient();

    const tools = await toLangChainTools({ client, accessToken: "token-123" });

    expect(listTools).toHaveBeenCalledWith("token-123");
    expect(tools).toHaveLength(SAMPLE_TOOLS.length);
    for (const tool of tools) {
      expect(tool).toBeInstanceOf(DynamicStructuredTool);
    }
  });

  it("names, describes, and builds a Zod schema enforcing required fields", async () => {
    const { client } = createMockClient();

    const [, createIssueTool] = await toLangChainTools({ client, accessToken: "token-123" });

    expect(createIssueTool.name).toBe("github_oauth_create_issue");
    expect(createIssueTool.description).toBe("Create a new issue in a repository.");

    const valid = createIssueTool.schema.safeParse({
      owner: "octocat",
      repo: "hello-world",
      title: "Bug report",
    });
    expect(valid.success).toBe(true);

    const missingRequired = createIssueTool.schema.safeParse({ owner: "octocat" });
    expect(missingRequired.success).toBe(false);

    const wrongType = createIssueTool.schema.safeParse({
      owner: "octocat",
      repo: "hello-world",
      title: 123,
    });
    expect(wrongType.success).toBe(false);
  });

  it("builds an empty-shape Zod object when inputSchema is null", async () => {
    const { client } = createMockClient();

    const [, , s3ListBucketsTool] = await toLangChainTools({ client, accessToken: "token-123" });

    expect(s3ListBucketsTool.name).toBe("aws_s3_list_buckets");
    expect(s3ListBucketsTool.description).toBe("List S3 Buckets");
    expect(s3ListBucketsTool.schema.safeParse({}).success).toBe(true);
  });

  it("uses pre-fetched tools without calling listTools", async () => {
    const { client, listTools } = createMockClient();
    const [onlyTool] = SAMPLE_TOOLS;

    const tools = await toLangChainTools({
      client,
      accessToken: "token-123",
      tools: [onlyTool],
    });

    expect(listTools).not.toHaveBeenCalled();
    expect(tools).toHaveLength(1);
    expect(tools[0].name).toBe(onlyTool.id);
  });

  it("invokes the tool via executeTool and stringifies non-string results", async () => {
    const { client, executeTool } = createMockClient({
      executeResult: { tool: "google_calendar_list_events", data: { events: [] } },
    });

    const [listEventsTool] = await toLangChainTools({ client, accessToken: "token-123" });
    const result = await listEventsTool.invoke({});

    expect(executeTool).toHaveBeenCalledWith("token-123", "google_calendar_list_events", {});
    expect(result).toBe(JSON.stringify({ events: [] }));
  });

  it("passes through string results unchanged", async () => {
    const { client } = createMockClient({
      executeResult: { tool: "github_oauth_create_issue", data: "issue #42 created" },
    });

    const [, createIssueTool] = await toLangChainTools({ client, accessToken: "token-123" });
    const result = await createIssueTool.invoke({
      owner: "octocat",
      repo: "hello-world",
      title: "Bug report",
    });

    expect(result).toBe("issue #42 created");
  });
});
