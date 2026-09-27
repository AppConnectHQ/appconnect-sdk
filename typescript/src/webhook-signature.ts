import { createHmac, timingSafeEqual } from "crypto";

/**
 * Partner-side verification for AppConnect's outbound trigger deliveries.
 *
 * A partner's own webhook receiver calls this against the raw request body
 * and the `X-AppConnect-Signature: t=<unix_ts>,v1=<hex hmac>` header, using
 * the `signing_secret` returned once from `subscribeTrigger()`. It mirrors
 * AppConnect's server-side signer byte-for-byte: both HMAC-SHA256 the string
 * `${t}.${rawBody}` with the shared secret and compare hex digests.
 *
 * Exported standalone (not an `AppConnectClient` method) since it runs
 * inside the partner's own webhook handler, not against AppConnect's API.
 */
export function verifyWebhookSignature(
  rawBody: string,
  header: string,
  signingSecret: string,
  toleranceSeconds: number = 300,
): boolean {
  const parsed = parseSignatureHeader(header);
  if (!parsed) {
    return false;
  }
  const { timestamp, v1 } = parsed;

  if (toleranceSeconds > 0) {
    const nowSeconds = Math.floor(Date.now() / 1000);
    if (Math.abs(nowSeconds - timestamp) > toleranceSeconds) {
      return false;
    }
  }

  const signedPayload = `${timestamp}.${rawBody}`;
  const expected = createHmac("sha256", signingSecret).update(signedPayload, "utf8").digest("hex");

  const expectedBuf = Buffer.from(expected, "utf8");
  const actualBuf = Buffer.from(v1, "utf8");

  // timingSafeEqual throws if buffers have different lengths, so guard first.
  if (expectedBuf.length !== actualBuf.length) {
    return false;
  }

  return timingSafeEqual(expectedBuf, actualBuf);
}

function parseSignatureHeader(header: string): { timestamp: number; v1: string } | null {
  if (!header) {
    return null;
  }

  let timestamp: number | null = null;
  let v1: string | null = null;

  for (const part of header.split(",")) {
    const separatorIndex = part.indexOf("=");
    if (separatorIndex === -1) {
      continue;
    }
    const key = part.slice(0, separatorIndex).trim();
    const value = part.slice(separatorIndex + 1).trim();

    if (key === "t" && value) {
      const parsedTimestamp = Number.parseInt(value, 10);
      if (Number.isFinite(parsedTimestamp)) {
        timestamp = parsedTimestamp;
      }
    } else if (key === "v1" && value) {
      v1 = value;
    }
  }

  if (timestamp === null || v1 === null) {
    return null;
  }

  return { timestamp, v1 };
}
