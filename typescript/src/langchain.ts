/**
 * LangChain adapter -- published as the `@appconnecthq/sdk/langchain`
 * subpath (see tsdown.config.ts) so importing it, and therefore statically
 * resolving the optional peer dep "@langchain/core", is opt-in. The main
 * `.` entry does not re-export this (see src/framework/index.ts).
 *
 * @module sdk/langchain
 */
export { toLangChainTools } from "./framework/langchain";
