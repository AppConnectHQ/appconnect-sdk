# @appconnecthq/sdk/langchain

LangChain adapter -- published as the `@appconnecthq/sdk/langchain`
subpath (see tsdown.config.ts) so importing it, and therefore statically
resolving the optional peer dep "@langchain/core", is opt-in. The main
`.` entry does not re-export this (see src/framework/index.ts).

## Functions

### toLangChainTools()

```ts
function toLangChainTools(options): Promise<DynamicStructuredTool<AppConnectZodSchema, {
[key: string]: unknown;
}, {
[key: string]: unknown;
}, any, unknown, string>[]>;
```

Maps AppConnect tools to real `DynamicStructuredTool` instances (not a
duck-typed plain-object shape) so they satisfy LangChain's runtime schema
checks. Each tool's `inputSchema` is converted to a genuine Zod object
schema via `jsonSchemaObjectToZod` -- LangChain accepts Zod or JSON
Schema for `schema`, but Zod is what the rest of the LangChain ecosystem
(agents, `.bind()`, structured output) expects to introspect.

#### Parameters

| Parameter | Type |
| ------ | ------ |
| `options` | [`ToolAdapterOptions`](sdk.md#tooladapteroptions) |

#### Returns

`Promise`\<`DynamicStructuredTool`\<`AppConnectZodSchema`, \{
\[`key`: `string`\]: `unknown`;
\}, \{
\[`key`: `string`\]: `unknown`;
\}, `any`, `unknown`, `string`\>[]\>
