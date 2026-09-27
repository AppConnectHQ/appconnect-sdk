/**
 * Vercel AI SDK adapter -- published as the `@appconnecthq/sdk/ai-sdk`
 * subpath (see tsdown.config.ts) so importing it, and therefore statically
 * resolving the optional peer dep "ai", is opt-in. The main `.` entry does
 * not re-export this (see src/framework/index.ts).
 */
export { toAISDKTools } from "./framework/ai-sdk";
