# Changelog

All notable changes to `@appconnecthq/sdk` are documented here. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the
project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0]

First public release on npmjs.com.

### Added

- `AppConnectClient` for server-side use: hosted Link sessions
  (`createLinkToken`, `exchangeLinkToken`), OAuth token exchange and refresh,
  tool listing, search, and execution, and an authenticated raw API `proxy`.
- Triggers: `listTriggerDefinitions`, `subscribeTrigger`,
  `listTriggerInstances`, `getTriggerInstance`, `updateTriggerInstance`,
  `unsubscribeTrigger`, and `listDeliveries`.
- `verifyWebhookSignature` for signed trigger deliveries.
- Framework adapters: OpenAI and Anthropic (main entry), Vercel AI SDK
  (`@appconnecthq/sdk/ai-sdk`), and LangChain (`@appconnecthq/sdk/langchain`).
- `AppConnectError` with `status` and `code`.

### Note on the earlier npm.w3api.dev build

A `0.1.0` build was published to `npm.w3api.dev` on 2026-08-05, before the SDK
moved to this repository. The npmjs.com `0.1.0` differs from it:

- `baseUrl` is optional and defaults to `https://www.appconnecthq.com`
  (it was required).
- `DEFAULT_BASE_URL` is exported.
- Source comments no longer reference internal paths.

The API surface is otherwise identical.

[Unreleased]: https://github.com/AppConnectHQ/appconnect-sdk/commits/main/typescript
[0.1.0]: https://github.com/AppConnectHQ/appconnect-sdk/tree/main/typescript
