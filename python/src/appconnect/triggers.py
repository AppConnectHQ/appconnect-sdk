"""Pure request-building helpers for the triggers/webhooks SDK surface, mirroring the TypeScript SDK's trigger
methods. Split out of `client.py` (rather than inlined per-method) so the
"only include a field if the caller actually supplied it" logic -- the same
class of bug fixed in `_create_link_token_body` (see
`test_create_link_token_omits_optional_fields_when_unset`) -- is unit
tested directly, and so `client.py` stays under the repo's 600-line file cap
now that both async and sync clients gain 7 new methods each.
"""

from __future__ import annotations

from typing import Any


def build_list_trigger_definitions_params(service: str | None) -> dict[str, str] | None:
    """`GET /api/trigger-definitions?service=...` -- omitted entirely when
    `service` is None rather than sent as an empty/`None` query value.
    """
    if service is None:
        return None
    return {"service": service}


def build_subscribe_trigger_body(
    service: str,
    trigger: str,
    config: dict[str, Any],
    callback_url: str,
) -> dict[str, Any]:
    """`POST /api/triggers` body. All fields are required by the server's
    `subscribeTriggerSchema`, so unlike the optional-field builders below
    this one always includes every key.
    """
    return {
        "service": service,
        "trigger": trigger,
        "config": config,
        "callback_url": callback_url,
    }


def build_update_trigger_instance_body(
    status: str | None,
    callback_url: str | None,
    config: dict[str, Any] | None,
) -> dict[str, Any]:
    """`PATCH /api/triggers/{id}` body -- only includes fields the caller
    actually supplied. httpx serializes a `None` value as JSON `null`, and
    the server's `updateTriggerInstanceSchema` treats these as
    optional-absent, not nullable, so omitting unset keys (rather than
    sending them as null) is required for the request to validate.
    """
    body: dict[str, Any] = {}
    if status is not None:
        body["status"] = status
    if callback_url is not None:
        body["callback_url"] = callback_url
    if config is not None:
        body["config"] = config
    return body


def build_list_deliveries_params(
    status: str | None,
    limit: int | None,
    cursor: str | None,
) -> dict[str, str] | None:
    """`GET /api/triggers/{id}/deliveries` query params -- only includes
    filters the caller actually supplied; returns None (no querystring at
    all) when none were.
    """
    params: dict[str, str] = {}
    if status is not None:
        params["status"] = status
    if limit is not None:
        params["limit"] = str(limit)
    if cursor is not None:
        params["cursor"] = cursor
    return params or None
