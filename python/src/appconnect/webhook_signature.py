"""Partner-side verification for AppConnect's outbound trigger deliveries.

A partner's own webhook receiver calls `verify_webhook_signature` against
the raw request body and the `X-AppConnect-Signature: t=<unix_ts>,v1=<hex
hmac>` header, using the `signing_secret` returned once from
`subscribe_trigger()`. It mirrors the server-side signer byte-for-byte
(and its TypeScript SDK twin `verifyWebhookSignature` in
`typescript/src/webhook-signature.ts`): both HMAC-SHA256 the string
`f"{t}.{raw_body}"` with the shared secret and compare hex digests.

Exported standalone (not a client method) since it runs inside the
partner's own webhook handler, not against AppConnect's API.
"""

from __future__ import annotations

import hashlib
import hmac
import time


def verify_webhook_signature(
    raw_body: str,
    header: str,
    signing_secret: str,
    tolerance_seconds: int = 300,
) -> bool:
    parsed = _parse_signature_header(header)
    if parsed is None:
        return False
    timestamp, v1 = parsed

    if tolerance_seconds > 0:
        now_seconds = int(time.time())
        if abs(now_seconds - timestamp) > tolerance_seconds:
            return False

    signed_payload = f"{timestamp}.{raw_body}"
    expected = hmac.new(
        signing_secret.encode("utf-8"),
        signed_payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, v1)


def _parse_signature_header(header: str) -> tuple[int, str] | None:
    if not header:
        return None

    timestamp: int | None = None
    v1: str | None = None

    for part in header.split(","):
        if "=" not in part:
            continue
        key, _, value = part.strip().partition("=")
        key = key.strip()
        value = value.strip()
        if key == "t" and value:
            try:
                timestamp = int(value)
            except ValueError:
                continue
        elif key == "v1" and value:
            v1 = value

    if timestamp is None or v1 is None:
        return None

    return timestamp, v1
