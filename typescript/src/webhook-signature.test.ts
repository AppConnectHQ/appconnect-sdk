import { createHmac } from "crypto";
import { describe, expect, it } from "vitest";
import { verifyWebhookSignature } from "./webhook-signature";

const SECRET = "test-signing-secret";

/** Builds the same `t=<ts>,v1=<hex>` header the server-side signer produces. */
function sign(rawBody: string, secret: string, timestamp: number): string {
  const v1 = createHmac("sha256", secret).update(`${timestamp}.${rawBody}`, "utf8").digest("hex");
  return `t=${timestamp},v1=${v1}`;
}

describe("verifyWebhookSignature", () => {
  it("accepts a signature it just generated", () => {
    const rawBody = JSON.stringify({ event_id: "evt_1", data: { hello: "world" } });
    const now = Math.floor(Date.now() / 1000);
    const header = sign(rawBody, SECRET, now);

    expect(verifyWebhookSignature(rawBody, header, SECRET)).toBe(true);
  });

  it("rejects when the body was tampered with after signing", () => {
    const rawBody = JSON.stringify({ event_id: "evt_1" });
    const now = Math.floor(Date.now() / 1000);
    const header = sign(rawBody, SECRET, now);

    expect(verifyWebhookSignature(rawBody + "tampered", header, SECRET)).toBe(false);
  });

  it("rejects when verified against the wrong secret", () => {
    const rawBody = JSON.stringify({ event_id: "evt_1" });
    const now = Math.floor(Date.now() / 1000);
    const header = sign(rawBody, SECRET, now);

    expect(verifyWebhookSignature(rawBody, header, "wrong-secret")).toBe(false);
  });

  it("rejects a header missing the v1 component", () => {
    const rawBody = "{}";
    expect(verifyWebhookSignature(rawBody, `t=${Math.floor(Date.now() / 1000)}`, SECRET)).toBe(
      false,
    );
  });

  it("rejects a header missing the t component", () => {
    const rawBody = "{}";
    const now = Math.floor(Date.now() / 1000);
    const v1 = createHmac("sha256", SECRET).update(`${now}.${rawBody}`, "utf8").digest("hex");
    expect(verifyWebhookSignature(rawBody, `v1=${v1}`, SECRET)).toBe(false);
  });

  it("rejects a malformed / empty header", () => {
    expect(verifyWebhookSignature("{}", "", SECRET)).toBe(false);
    expect(verifyWebhookSignature("{}", "not-a-valid-header", SECRET)).toBe(false);
  });

  it("rejects a stale timestamp beyond the default 300s tolerance", () => {
    const rawBody = "{}";
    const staleTimestamp = Math.floor(Date.now() / 1000) - 301;
    const header = sign(rawBody, SECRET, staleTimestamp);

    expect(verifyWebhookSignature(rawBody, header, SECRET)).toBe(false);
  });

  it("accepts a timestamp within the default tolerance", () => {
    const rawBody = "{}";
    const recentTimestamp = Math.floor(Date.now() / 1000) - 299;
    const header = sign(rawBody, SECRET, recentTimestamp);

    expect(verifyWebhookSignature(rawBody, header, SECRET)).toBe(true);
  });

  it("respects a custom tolerance", () => {
    const rawBody = "{}";
    const timestamp = Math.floor(Date.now() / 1000) - 30;
    const header = sign(rawBody, SECRET, timestamp);

    expect(verifyWebhookSignature(rawBody, header, SECRET, 10)).toBe(false);
    expect(verifyWebhookSignature(rawBody, header, SECRET, 60)).toBe(true);
  });

  it("skips the staleness check when tolerance is 0", () => {
    const rawBody = "{}";
    const veryOldTimestamp = Math.floor(Date.now() / 1000) - 1_000_000;
    const header = sign(rawBody, SECRET, veryOldTimestamp);

    expect(verifyWebhookSignature(rawBody, header, SECRET, 0)).toBe(true);
  });

  it("ignores unknown extra components in the header", () => {
    const rawBody = "{}";
    const now = Math.floor(Date.now() / 1000);
    const v1 = createHmac("sha256", SECRET).update(`${now}.${rawBody}`, "utf8").digest("hex");
    expect(verifyWebhookSignature(rawBody, `t=${now},v1=${v1},v2=future-scheme`, SECRET)).toBe(
      true,
    );
  });
});
