"""Shared respx/httpx test helpers and client fixtures for `test_client*.py`.

Split out of `test_client.py` (rather than duplicated) once the trigger
method tests grew large enough to warrant their own file
(`test_client_triggers.py`) -- both files need the same `async_client`/
`sync_client` fixtures and `_success`/`_error` response builders.
"""

from __future__ import annotations

from typing import Any

import httpx
import pytest

from appconnect.client import AppConnectClient, SyncAppConnectClient

BASE_URL = "https://api.example.com"


def _success(data: Any, status: int = 200) -> httpx.Response:
    return httpx.Response(status, json={"success": True, "data": data})


def _error(code: str, message: str, status: int) -> httpx.Response:
    return httpx.Response(
        status, json={"success": False, "error": {"code": code, "message": message}}
    )


@pytest.fixture
def async_client() -> AppConnectClient:
    return AppConnectClient(base_url=BASE_URL, client_id="client_123", client_secret="secret_abc")


@pytest.fixture
def sync_client() -> SyncAppConnectClient:
    return SyncAppConnectClient(
        base_url=BASE_URL, client_id="client_123", client_secret="secret_abc"
    )
