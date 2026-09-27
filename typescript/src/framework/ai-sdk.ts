import type { JSONSchema7, ToolSet } from "ai";
import { jsonSchema, tool } from "ai";
import type { AppConnectTool } from "../index";
import type { ToolAdapterOptions } from "./types";
import { resolveTools } from "./types";

/**
 * Converts an AppConnectTool's `inputSchema` into a plain JSON Schema 7
 * object for `jsonSchema()`. AppConnect's wire schema is a flat, JSON-Schema-7
 * compatible object already -- this only fills in the always-required
 * `type: "object"` and defaults a missing/null schema to an empty object.
 */
function toJsonSchema7(inputSchema: AppConnectTool["inputSchema"]): JSONSchema7 {
  return {
    type: "object",
    properties: (inputSchema?.properties ?? {}) as JSONSchema7["properties"],
    required: inputSchema?.required,
  };
}

/**
 * Maps AppConnect tools to an AI SDK v5 `ToolSet` (the shape `streamText`/
 * `generateText`'s `tools` option expects): `tool({description, inputSchema:
 * jsonSchema(...), execute})` per tool, keyed by the tool's unified id.
 *
 * Deliberately targets v5's `inputSchema` + `jsonSchema()` wrapper, not the
 * stale v3/v4 `parameters` shape.
 */
export async function toAISDKTools(options: ToolAdapterOptions): Promise<ToolSet> {
  const tools = await resolveTools(options);
  const toolSet: ToolSet = {};

  for (const appTool of tools) {
    toolSet[appTool.id] = tool({
      description: appTool.description || appTool.displayName,
      inputSchema: jsonSchema(toJsonSchema7(appTool.inputSchema)),
      execute: async (input) => {
        const result = await options.client.executeTool(
          options.accessToken,
          appTool.id,
          (input ?? {}) as Record<string, unknown>,
        );
        return result.data;
      },
    });
  }

  return toolSet;
}
