# Changelog

All notable changes to the `appconnect` Python package are documented here. The
format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-09-27

First release on PyPI.

### Added

- Async `AppConnectClient` and synchronous `SyncAppConnectClient`, mirroring
  the TypeScript SDK: hosted Link sessions, OAuth token exchange and refresh,
  tool listing, search, and execution, and an authenticated raw API `proxy`.
- Triggers: definitions, subscribe, list, get, update, unsubscribe, and
  delivery history.
- `verify_webhook_signature` for signed trigger deliveries.
- Framework adapters in `appconnect.framework`: OpenAI, Anthropic, and
  LangChain (with the `langchain` extra).
- Pydantic response models whose field names mirror the API's JSON keys.
- `AppConnectError` with `status` and `code`, including `network_error` and
  `config_error`.

[Unreleased]: https://github.com/AppConnectHQ/appconnect-sdk/commits/main/python
[0.1.0]: https://pypi.org/project/appconnect/0.1.0/
