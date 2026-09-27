import type { ToolAdapterOptions } from "./types";
import { resolveTools } from "./types";

/** A tool in OpenAI chat-completions function-calling shape. */
export interface OpenAIFunctionTool {
  type: "function";
  function: {
    name: string;
    description: string;
    parameters: {
      type: "object";
      properties: Record<string, unknown>;
      required?: string[];
    };
  };
}

/** An OpenAI chat-completions tool call, as found on an assistant message's `tool_calls`. */
export interface OpenAIToolCall {
  id: string;
  function: {
    name: string;
    arguments: string;
  };
}

/** The `{role: "tool", ...}` message OpenAI expects appended after a tool call runs. */
export interface OpenAIToolResultMessage {
  role: "tool";
  tool_call_id: string;
  content: string;
}

/**
 * Maps AppConnect tools to OpenAI chat-completions function-calling tools.
 */
export async function toOpenAITools(options: ToolAdapterOptions): Promise<OpenAIFunctionTool[]> {
  const tools = await resolveTools(options);
  return tools.map((tool) => ({
    type: "function",
    function: {
      name: tool.id,
      description: tool.description || tool.displayName,
      parameters: {
        type: "object",
        properties: tool.inputSchema?.properties ?? {},
        required: tool.inputSchema?.required,
      },
    },
  }));
}

/**
 * Executes a single OpenAI tool call via `executeTool` and returns the
 * `{role: "tool", ...}` message to append to the conversation.
 */
export async function executeOpenAIToolCall(
  options: ToolAdapterOptions,
  toolCall: OpenAIToolCall,
): Promise<OpenAIToolResultMessage> {
  const args = JSON.parse(toolCall.function.arguments || "{}") as Record<string, unknown>;
  const result = await options.client.executeTool(
    options.accessToken,
    toolCall.function.name,
    args,
  );
  return {
    role: "tool",
    tool_call_id: toolCall.id,
    content: typeof result.data === "string" ? result.data : JSON.stringify(result.data),
  };
}
