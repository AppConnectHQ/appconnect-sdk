export type { ToolAdapterOptions } from "./types";

export type { OpenAIFunctionTool, OpenAIToolCall, OpenAIToolResultMessage } from "./openai";
export { toOpenAITools, executeOpenAIToolCall } from "./openai";

export type { AnthropicTool, AnthropicToolUseBlock, AnthropicToolResultBlock } from "./anthropic";
export { toAnthropicTools, executeAnthropicToolUse } from "./anthropic";

// `toAISDKTools` (needs "ai") and `toLangChainTools` (needs "@langchain/core")
// are deliberately NOT re-exported here. Both peer deps are optional, and
// re-exporting them from this module would pull a static `import` of "ai"
// / "@langchain/core" into the main `.` entry's dist bundle -- breaking
// `import { AppConnectClient } from "@appconnecthq/sdk"` for consumers who
// installed neither. They're published as their own subpath entries
// instead: `@appconnecthq/sdk/ai-sdk` and `@appconnecthq/sdk/langchain`
// (see src/ai-sdk.ts, src/langchain.ts, and tsdown.config.ts).

export type { JsonSchemaProperty, JsonSchemaObject } from "./json-schema-to-zod";
export { jsonSchemaPropertyToZod, jsonSchemaObjectToZod } from "./json-schema-to-zod";
