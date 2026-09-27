import type { AppConnectClient, AppConnectTool } from "../index";

/**
 * Shared contract for every framework adapter (OpenAI, Anthropic, ...).
 *
 * AppConnect's client is multi-tenant per-request — every call needs an
 * `accessToken` — so unlike single-tenant SDKs, adapters thread the token
 * explicitly instead of storing it on the client.
 */
export interface ToolAdapterOptions {
  /** The AppConnectClient used to list/execute tools. */
  client: AppConnectClient;
  /** Bearer token identifying the connected user. */
  accessToken: string;
  /** Pass pre-fetched tools to skip a listTools() round trip. */
  tools?: AppConnectTool[];
}

/**
 * Resolves the tool list an adapter should map: the caller's pre-fetched
 * `tools` if provided, otherwise a fresh `listTools()` call.
 */
export async function resolveTools(options: ToolAdapterOptions): Promise<AppConnectTool[]> {
  if (options.tools) {
    return options.tools;
  }
  const response = await options.client.listTools(options.accessToken);
  return response.tools;
}
