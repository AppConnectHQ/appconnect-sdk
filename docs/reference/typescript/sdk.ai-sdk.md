# @appconnecthq/sdk/ai-sdk

Vercel AI SDK adapter -- published as the `@appconnecthq/sdk/ai-sdk`
subpath (see tsdown.config.ts) so importing it, and therefore statically
resolving the optional peer dep "ai", is opt-in. The main `.` entry does
not re-export this (see src/framework/index.ts).

## Functions

### toAISDKTools()

```ts
function toAISDKTools(options): Promise<ToolSet>;
```

Maps AppConnect tools to an AI SDK v5 `ToolSet` (the shape `streamText`/
`generateText`'s `tools` option expects): `tool({description, inputSchema:
jsonSchema(...), execute})` per tool, keyed by the tool's unified id.

Deliberately targets v5's `inputSchema` + `jsonSchema()` wrapper, not the
stale v3/v4 `parameters` shape.

#### Parameters

| Parameter | Type |
| ------ | ------ |
| `options` | [`ToolAdapterOptions`](sdk.md#tooladapteroptions) |

#### Returns

`Promise`\<`ToolSet`\>
