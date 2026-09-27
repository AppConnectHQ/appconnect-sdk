#!/usr/bin/env bun
/**
 * End-to-end example: list AppConnect tools for a connected user, adapt
 * them to OpenAI chat-completions function-calling format, run a
 * tool-calling chat loop against a real OpenAI model, and execute whatever
 * tool call the model requests back through AppConnect's `executeTool`.
 *
 * This is the "list -> adapt -> model -> execute" loop, driven against the
 * SDK's default AppConnect API origin.
 *
 * Usage (from typescript/):
 *   bun examples/ts-openai-agent.ts
 *   bun examples/ts-openai-agent.ts --mock
 *
 * Required env var:
 *   APPCONNECT_ACCESS_TOKEN  Bearer token for a connected AppConnect user
 *                            (returned by exchangeLinkToken() after a
 *                            user completes a hosted Link session)
 *
 * Optional env vars:
 *   OPENAI_API_KEY           Real OpenAI key. When absent (or --mock is
 *                            passed) the script substitutes a deterministic
 *                            mocked model response (see ./mock-model.ts) so
 *                            the example always runs end-to-end without
 *                            spending API credits or requiring an LLM key.
 *   OPENAI_MODEL             Default: gpt-4o-mini
 *   APPCONNECT_PROMPT        User prompt sent to the model.
 *
 * See ./README.md for a full walkthrough.
 */

import {
  AppConnectClient,
  toOpenAITools,
  executeOpenAIToolCall,
  type OpenAIFunctionTool,
} from "../src/index";
import {
  mockModelTurn,
  mockModelFinalTurn,
  type AssistantTurn,
  type ChatMessage,
} from "./mock-model";

async function callOpenAI(
  apiKey: string,
  model: string,
  messages: ChatMessage[],
  tools: OpenAIFunctionTool[],
): Promise<AssistantTurn> {
  const response = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({ model, messages, tools: tools.length > 0 ? tools : undefined }),
  });

  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(`OpenAI request failed (${response.status}): ${JSON.stringify(payload)}`);
  }

  const message = payload?.choices?.[0]?.message;
  if (!message) {
    throw new Error(`OpenAI response missing choices[0].message: ${JSON.stringify(payload)}`);
  }

  return { content: message.content ?? null, tool_calls: message.tool_calls };
}

function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(
      `Missing required environment variable ${name}. See examples/README.md for setup.`,
    );
  }
  return value;
}

async function main(): Promise<void> {
  const mockFlag = process.argv.includes("--mock");
  const accessToken = requireEnv("APPCONNECT_ACCESS_TOKEN");
  const openaiApiKey = process.env.OPENAI_API_KEY;
  const useMock = mockFlag || !openaiApiKey;
  const model = process.env.OPENAI_MODEL ?? "gpt-4o-mini";
  const prompt =
    process.env.APPCONNECT_PROMPT ??
    "Look at the tools you have access to via AppConnect and, if there's a safe " +
      "read-only (list/get) tool available, call it to show me a small sample of data. " +
      "Otherwise just summarize what tools you have.";

  // clientId/clientSecret are only used by the OAuth/link-token endpoints,
  // not by listTools/executeTool — placeholders are fine here.
  const client = new AppConnectClient({ clientId: "example", clientSecret: "example" });

  console.log("[1/4] Listing AppConnect tools...");
  const { tools } = await client.listTools(accessToken);
  console.log(`      -> ${tools.length} tool(s) available`);

  console.log(`[2/4] Adapting tools to OpenAI function-calling format...`);
  const openaiTools = await toOpenAITools({ client, accessToken, tools });

  const messages: ChatMessage[] = [
    {
      role: "system",
      content:
        "You are a helpful assistant with access to the user's connected services via AppConnect tools.",
    },
    { role: "user", content: prompt },
  ];

  console.log(
    `[3/4] Calling the model${useMock ? " (mocked — no OPENAI_API_KEY / --mock)" : ` (${model})`}...`,
  );
  const firstTurn = useMock
    ? mockModelTurn(tools)
    : await callOpenAI(openaiApiKey!, model, messages, openaiTools);

  messages.push({
    role: "assistant",
    content: firstTurn.content,
    tool_calls: firstTurn.tool_calls,
  });

  if (!firstTurn.tool_calls || firstTurn.tool_calls.length === 0) {
    console.log("\nFinal assistant message (no tool calls):\n");
    console.log(firstTurn.content);
    return;
  }

  console.log(`[4/4] Executing ${firstTurn.tool_calls.length} tool call(s) via AppConnect...`);
  for (const toolCall of firstTurn.tool_calls) {
    console.log(`      -> ${toolCall.function.name}(${toolCall.function.arguments})`);
    const resultMessage = await executeOpenAIToolCall({ client, accessToken, tools }, toolCall);
    messages.push(resultMessage);
  }

  const finalTurn = useMock
    ? mockModelFinalTurn(messages)
    : await callOpenAI(openaiApiKey!, model, messages, openaiTools);

  console.log("\nFinal assistant message:\n");
  console.log(finalTurn.content);
}

main().catch((error: unknown) => {
  console.error(`\nExample failed: ${error instanceof Error ? error.message : String(error)}`);
  process.exit(1);
});
