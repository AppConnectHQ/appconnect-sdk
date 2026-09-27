import { defineConfig } from "tsdown";

// Three entries, one per publishable export:
//   .                    -> src/index.ts       (client, types, webhook-signature,
//                                                openai/anthropic adapters -- no
//                                                optional peer deps required)
//   ./ai-sdk             -> src/ai-sdk.ts       (needs the optional "ai" peer dep)
//   ./langchain          -> src/langchain.ts    (needs the optional "@langchain/core" peer dep)
//
// Framework adapters that pull in an optional peer dep get their own entry
// so `import { AppConnectClient } from "@appconnecthq/sdk"` never triggers a
// static resolution of "ai" or "@langchain/core" for consumers who didn't
// install them -- see src/framework/index.ts for the full rationale.
export default defineConfig({
  entry: {
    index: "src/index.ts",
    "ai-sdk": "src/ai-sdk.ts",
    langchain: "src/langchain.ts",
  },
  format: "esm",
  target: "es2022",
  // `webhook-signature.ts` imports Node's built-in `crypto` module, so this
  // package is Node-only, not runtime-agnostic.
  platform: "node",
  dts: true,
  sourcemap: true,
  clean: true,
  treeshake: true,
  // tsdown externalizes `dependencies` + `peerDependencies` by default;
  // listed explicitly as a safety net so a future dependency-array edit
  // can't silently start bundling these.
  deps: {
    neverBundle: ["ai", "@langchain/core", "zod"],
  },
  // This package sets "type": "module" and ships ESM only, so plain
  // `.js`/`.d.ts` are unambiguous -- match the package.json `exports`
  // paths instead of tsdown's default `.mjs`/`.d.mts`.
  outExtensions: () => ({ js: ".js", dts: ".d.ts" }),
});
