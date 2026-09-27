import { describe, expect, it } from "vitest";
import { jsonSchemaObjectToZod, jsonSchemaPropertyToZod } from "./json-schema-to-zod";

describe("jsonSchemaPropertyToZod", () => {
  it("maps string/number/integer/boolean primitives", () => {
    expect(jsonSchemaPropertyToZod({ type: "string" }).safeParse("hi").success).toBe(true);
    expect(jsonSchemaPropertyToZod({ type: "string" }).safeParse(1).success).toBe(false);

    expect(jsonSchemaPropertyToZod({ type: "number" }).safeParse(1.5).success).toBe(true);
    expect(jsonSchemaPropertyToZod({ type: "number" }).safeParse("1.5").success).toBe(false);

    expect(jsonSchemaPropertyToZod({ type: "integer" }).safeParse(5).success).toBe(true);
    expect(jsonSchemaPropertyToZod({ type: "integer" }).safeParse(5.5).success).toBe(false);

    expect(jsonSchemaPropertyToZod({ type: "boolean" }).safeParse(true).success).toBe(true);
    expect(jsonSchemaPropertyToZod({ type: "boolean" }).safeParse("true").success).toBe(false);
  });

  it("maps enum to a Zod enum regardless of declared type", () => {
    const schema = jsonSchemaPropertyToZod({ type: "string", enum: ["open", "closed"] });
    expect(schema.safeParse("open").success).toBe(true);
    expect(schema.safeParse("archived").success).toBe(false);
  });

  it("maps array with typed items", () => {
    const schema = jsonSchemaPropertyToZod({ type: "array", items: { type: "string" } });
    expect(schema.safeParse(["a", "b"]).success).toBe(true);
    expect(schema.safeParse([1, 2]).success).toBe(false);
  });

  it("maps array with no items to an array of unknown", () => {
    const schema = jsonSchemaPropertyToZod({ type: "array" });
    expect(schema.safeParse([1, "a", true]).success).toBe(true);
  });

  it("maps object with nested properties recursively", () => {
    const schema = jsonSchemaPropertyToZod({
      type: "object",
      properties: {
        name: { type: "string" },
        age: { type: "integer" },
      },
      required: ["name"],
    });

    expect(schema.safeParse({ name: "Ada" }).success).toBe(true);
    expect(schema.safeParse({ name: "Ada", age: 30 }).success).toBe(true);
    expect(schema.safeParse({ age: 30 }).success).toBe(false);
    expect(schema.safeParse({ name: "Ada", age: "thirty" }).success).toBe(false);
  });

  it("maps object with no properties to a record of unknown", () => {
    const schema = jsonSchemaPropertyToZod({ type: "object" });
    expect(schema.safeParse({ anything: "goes", n: 1 }).success).toBe(true);
  });

  it("falls back to z.unknown() for a missing or unrecognized type", () => {
    expect(jsonSchemaPropertyToZod({}).safeParse("literally anything").success).toBe(true);
    expect(jsonSchemaPropertyToZod({ type: "null" }).safeParse(null).success).toBe(true);
    expect(jsonSchemaPropertyToZod(null).safeParse(42).success).toBe(true);
    expect(jsonSchemaPropertyToZod(undefined).safeParse(42).success).toBe(true);
  });

  it("attaches the description to the resulting schema", () => {
    const schema = jsonSchemaPropertyToZod({ type: "string", description: "A repo owner" });
    expect(schema.description).toBe("A repo owner");
  });
});

describe("jsonSchemaObjectToZod", () => {
  it("marks properties not listed in required as optional", () => {
    const schema = jsonSchemaObjectToZod({
      type: "object",
      properties: {
        owner: { type: "string" },
        repo: { type: "string" },
        body: { type: "string" },
      },
      required: ["owner", "repo"],
    });

    expect(schema.safeParse({ owner: "octocat", repo: "hello-world" }).success).toBe(true);
    expect(schema.safeParse({ repo: "hello-world" }).success).toBe(false);
  });

  it("returns an empty-shape object schema for a null/undefined input schema", () => {
    expect(jsonSchemaObjectToZod(null).safeParse({}).success).toBe(true);
    expect(jsonSchemaObjectToZod(undefined).safeParse({}).success).toBe(true);
  });

  it("returns an empty-shape object schema when properties is missing", () => {
    expect(jsonSchemaObjectToZod({ type: "object" }).safeParse({}).success).toBe(true);
  });
});
