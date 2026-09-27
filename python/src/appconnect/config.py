"""Environment-driven configuration resolution for the AppConnect Python SDK."""

from __future__ import annotations

import os

from appconnect.types import AppConnectError


class AppConnectConfig:
    """Resolved client configuration (never partially populated)."""

    __slots__ = ("base_url", "client_id", "client_secret")

    def __init__(self, base_url: str, client_id: str, client_secret: str) -> None:
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret


def resolve_config(
    base_url: str | None = None,
    client_id: str | None = None,
    client_secret: str | None = None,
) -> AppConnectConfig:
    """Resolve client configuration.

    Priority (highest to lowest):
    1. Constructor arguments
    2. `APPCONNECT_BASE_URL` / `APPCONNECT_CLIENT_ID` / `APPCONNECT_CLIENT_SECRET`
       environment variables

    Raises:
        AppConnectError: if a value is missing from both sources.
    """
    resolved_base_url = base_url or os.environ.get("APPCONNECT_BASE_URL")
    resolved_client_id = client_id or os.environ.get("APPCONNECT_CLIENT_ID")
    resolved_client_secret = client_secret or os.environ.get("APPCONNECT_CLIENT_SECRET")

    missing = [
        name
        for name, value in (
            ("base_url", resolved_base_url),
            ("client_id", resolved_client_id),
            ("client_secret", resolved_client_secret),
        )
        if not value
    ]
    if missing:
        raise AppConnectError(
            "Missing AppConnect configuration: "
            f"{', '.join(missing)}. Pass as constructor arguments or set "
            "APPCONNECT_BASE_URL / APPCONNECT_CLIENT_ID / APPCONNECT_CLIENT_SECRET.",
            status=0,
            code="config_error",
        )

    assert resolved_base_url and resolved_client_id and resolved_client_secret

    return AppConnectConfig(
        base_url=resolved_base_url.rstrip("/"),
        client_id=resolved_client_id,
        client_secret=resolved_client_secret,
    )
