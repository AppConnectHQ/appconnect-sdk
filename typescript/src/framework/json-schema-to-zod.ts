import { z } from "zod";

/**
 * A flat JSON Schema property, matching the shapes AppConnect actually
 * emits in tool input schemas. This is not a
 * general JSON Schema implementation -- only the subset AppConnect uses:
 * string/number/integer/boolean/array/object, `enum`, `description`, and a
 * recursive `items`/`properties` for arrays and nested objects.
 */
export interface JsonSchemaProperty {
  type?: string;
  description?: string;
  format?: string;
  default?: unknown;
  enum?: string[];
  items?: JsonSchemaProperty;
  properties?: Record<string, unknown>;
  required?: string[];
}

/** The top-level shape AppConnectTool.inputSchema carries over the wire. */
export interface JsonSchemaObject {
  type: string;
  properties?: Record<string, unknown>;
  required?: string[];
}

function isJsonSchemaProperty(value: unknown): value is JsonSchemaProperty {
  return typeof value === "object" && value !== null;
}

/**
 * Converts a single JSON Schema property into a Zod schema. Falls back to
 * `z.unknown()` for shapes outside AppConnect's flat property model
 * (missing/unrecognized `type`, etc.) rather than throwing -- a tool schema
 * should still construct successfully even if one property is unusual.
 */
export function jsonSchemaPropertyToZod(prop: unknown): z.ZodTypeAny {
  if (!isJsonSchemaProperty(prop)) {
    return z.unknown();
  }

  let schema: z.ZodTypeAny;

  if (Array.isArray(prop.enum) && prop.enum.length > 0) {
    schema = z.enum(prop.enum);
  } else {
    switch (prop.type) {
      case "string":
        schema = z.string();
        break;
      case "number":
        schema = z.number();
        break;
      case "integer":
        schema = z.number().int();
        break;
      case "boolean":
        schema = z.boolean();
        break;
      case "array":
        schema = z.array(prop.items ? jsonSchemaPropertyToZod(prop.items) : z.unknown());
        break;
      case "object":
        schema = prop.properties
          ? jsonSchemaObjectToZod({
              type: "object",
              properties: prop.properties,
              required: prop.required,
            })
          : z.record(z.string(), z.unknown());
        break;
      default:
        schema = z.unknown();
    }
  }

  return prop.description ? schema.describe(prop.description) : schema;
}

/**
 * Converts an AppConnect-shaped JSON Schema object (top-level or nested)
 * into a Zod object schema, marking properties absent from `required` as
 * optional. This is the shape LangChain's `DynamicStructuredTool` expects
 * for its `schema` field.
 */
export function jsonSchemaObjectToZod(
  schema: JsonSchemaObject | null | undefined,
): z.ZodObject<Record<string, z.ZodTypeAny>> {
  const properties = schema?.properties ?? {};
  const required = new Set(schema?.required ?? []);

  const shape: Record<string, z.ZodTypeAny> = {};
  for (const [key, propSchema] of Object.entries(properties)) {
    const zodType = jsonSchemaPropertyToZod(propSchema);
    shape[key] = required.has(key) ? zodType : zodType.optional();
  }

  return z.object(shape);
}
