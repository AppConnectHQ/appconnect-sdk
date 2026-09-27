import { DynamicStructuredTool } from "@langchain/core/tools";
import type { z } from "zod";
import type { ToolAdapterOptions } from "./types";
import { resolveTools } from "./types";
import { jsonSchemaObjectToZod } from "./json-schema-to-zod";

/** The concrete Zod schema shape `jsonSchemaObjectToZod` always produces. */
type AppConnectZodSchema = z.ZodObject<Record<string, z.ZodTypeAny>>;

/**
 * Maps AppConnect tools to real `DynamicStructuredTool` instances (not a
 * duck-typed plain-object shape) so they satisfy LangChain's runtime schema
 * checks. Each tool's `inputSchema` is converted to a genuine Zod object
 * schema via `jsonSchemaObjectToZod` -- LangChain accepts Zod or JSON
 * Schema for `schema`, but Zod is what the rest of the LangChain ecosystem
 * (agents, `.bind()`, structured output) expects to introspect.
 */
export async function toLangChainTools(
  options: ToolAdapterOptions,
): Promise<DynamicStructuredTool<AppConnectZodSchema>[]> {
  const tools = await resolveTools(options);

  return tools.map(
    (appTool) =>
      new DynamicStructuredTool({
        name: appTool.id,
        description: appTool.description || appTool.displayName,
        schema: jsonSchemaObjectToZod(appTool.inputSchema),
        func: async (input) => {
          const result = await options.client.executeTool(
            options.accessToken,
            appTool.id,
            input as Record<string, unknown>,
          );
          return typeof result.data === "string" ? result.data : JSON.stringify(result.data);
        },
      }),
  );
}
