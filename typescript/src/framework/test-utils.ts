import { vi } from "vitest";
import type { AppConnectClient, AppConnectTool, ToolExecutionResponse } from "../index";

/**
 * Representative AppConnectTool fixtures spanning the shapes adapters must
 * handle: a GET tool with no input properties, a POST tool with required
 * fields, and a tool with a null description/inputSchema (both nullable
 * per the wire type — see src/index.ts).
 */
export const SAMPLE_TOOLS: AppConnectTool[] = [
  {
    id: "google_calendar_list_events",
    service: "google-calendar",
    serviceName: "Google Calendar",
    name: "list_events",
    displayName: "List Events",
    description: "List upcoming events on the user's calendar.",
    method: "GET",
    inputSchema: { type: "object", properties: {}, required: [] },
  },
  {
    id: "github_oauth_create_issue",
    service: "github-oauth",
    serviceName: "GitHub",
    name: "create_issue",
    displayName: "Create Issue",
    description: "Create a new issue in a repository.",
    method: "POST",
    inputSchema: {
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
    id: "aws_s3_list_buckets",
    service: "aws",
    serviceName: "AWS",
    name: "s3_list_buckets",
    displayName: "List S3 Buckets",
    description: null,
    method: "GET",
    inputSchema: null,
  },
];

/**
 * Builds a mocked AppConnectClient exposing only `listTools`/`executeTool`
 * as vi.fn() spies, cast to AppConnectClient for adapter-under-test
 * consumption. Adapters never touch the client's other members.
 */
export function createMockClient(options?: {
  tools?: AppConnectTool[];
  executeResult?: ToolExecutionResponse;
}) {
  const listTools = vi.fn().mockResolvedValue({ tools: options?.tools ?? SAMPLE_TOOLS });
  const executeTool = vi
    .fn()
    .mockResolvedValue(options?.executeResult ?? { tool: "some_tool", data: { ok: true } });

  const client = { listTools, executeTool } as unknown as AppConnectClient;
  return { client, listTools, executeTool };
}
