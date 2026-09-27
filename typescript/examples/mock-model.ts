/**
 * Deterministic stand-ins for an LLM's turns, used by the example scripts
 * when no LLM API key is available (or `--mock` is passed) so the examples
 * always run end-to-end without spending API credits or requiring
 * credentials. Kept separate from the runnable script so this pure logic
 * can be unit tested without touching the network or process.env.
 */
import type { AppConnectTool, OpenAIToolCall, OpenAIToolResultMessage } from "../src/index";

export interface AssistantTurn {
  content: string | null;
  tool_calls?: OpenAIToolCall[];
}

export type ChatMessage =
  | { role: "system" | "user"; content: string }
  | { role: "assistant"; content: string | null; tool_calls?: OpenAIToolCall[] }
  | OpenAIToolResultMessage;

/**
 * Picks a safe (read-only) tool to demonstrate the execute step in mock
 * mode. Prefers a GET tool with no required parameters (so calling it with
 * `{}` succeeds), falling back to the first GET tool otherwise.
 */
export function pickMockTool(tools: AppConnectTool[]): AppConnectTool | null {
  const readOnlyTools = tools.filter((tool) => tool.method === "GET");
  const noArgsTool = readOnlyTools.find((tool) => !tool.inputSchema?.required?.length);
  return noArgsTool ?? readOnlyTools[0] ?? null;
}

/**
 * Deterministic stand-in for the model's first turn. Only ever "calls" a
 * GET (read-only) tool, so mock mode never mutates the connected user's
 * data.
 */
export function mockModelTurn(tools: AppConnectTool[]): AssistantTurn {
  const picked = pickMockTool(tools);
  if (!picked) {
    return {
      content:
        `Mock mode: no read-only (GET) tool is available among the ${tools.length} ` +
        `tool(s) I can see, so I won't call anything. Set an LLM API key (or drop ` +
        `--mock) to use a real model.`,
    };
  }
  return {
    content: null,
    tool_calls: [{ id: "mock-call-1", function: { name: picked.id, arguments: "{}" } }],
  };
}

/** Deterministic stand-in for the model's follow-up turn after a tool result comes back. */
export function mockModelFinalTurn(messages: ChatMessage[]): AssistantTurn {
  const toolResult = [...messages]
    .reverse()
    .find((message): message is OpenAIToolResultMessage => message.role === "tool");

  if (!toolResult) {
    return { content: "Mock mode: no tool was called, nothing to summarize." };
  }

  const preview =
    toolResult.content.length > 300 ? `${toolResult.content.slice(0, 300)}...` : toolResult.content;
  return {
    content: `Mock mode: executed the tool and got back: ${preview}`,
  };
}
