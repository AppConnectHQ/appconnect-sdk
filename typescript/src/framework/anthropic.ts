import type { ToolAdapterOptions } from "./types";
import { resolveTools } from "./types";

/** A tool in Anthropic Messages API tool-use shape. */
export interface AnthropicTool {
  name: string;
  description: string;
  input_schema: {
    type: "object";
    properties: Record<string, unknown>;
    required?: string[];
  };
}

/** A `tool_use` content block from an Anthropic assistant message. */
export interface AnthropicToolUseBlock {
  type: "tool_use";
  id: string;
  name: string;
  input: Record<string, unknown>;
}

/** The `tool_result` content block Anthropic expects in the following user turn. */
export interface AnthropicToolResultBlock {
  type: "tool_result";
  tool_use_id: string;
  content: string;
}

/**
 * Maps AppConnect tools to Anthropic Messages API tool-use tools.
 */
export async function toAnthropicTools(options: ToolAdapterOptions): Promise<AnthropicTool[]> {
  const tools = await resolveTools(options);
  return tools.map((tool) => ({
    name: tool.id,
    description: tool.description || tool.displayName,
    input_schema: {
      type: "object",
      properties: tool.inputSchema?.properties ?? {},
      required: tool.inputSchema?.required,
    },
  }));
}

/**
 * Executes a single Anthropic `tool_use` block via `executeTool` and
 * returns the `tool_result` content block to append to the next user turn.
 */
export async function executeAnthropicToolUse(
  options: ToolAdapterOptions,
  toolUse: AnthropicToolUseBlock,
): Promise<AnthropicToolResultBlock> {
  const result = await options.client.executeTool(options.accessToken, toolUse.name, toolUse.input);
  return {
    type: "tool_result",
    tool_use_id: toolUse.id,
    content: typeof result.data === "string" ? result.data : JSON.stringify(result.data),
  };
}
