# AppConnect SDKs

Official server-side SDKs for [AppConnect](https://www.appconnecthq.com/sdk): give your code and your AI agents authenticated, per-user access to the services your users connect, without building OAuth flows, token refresh, or credential storage yourself.

| Language   | Package                                   | Source                        |
| ---------- | ----------------------------------------- | ----------------------------- |
| TypeScript | [`@appconnecthq/sdk`](typescript/README.md) | [`typescript/`](typescript/) |
| Python     | [`appconnect`](python/README.md)          | [`python/`](python/)          |

Both SDKs expose the same surface:

- **Hosted Link**: create a session, send your user to it, and exchange it for an access token when they return.
- **Tools**: list, search, and execute the tools a connected user can use, or make an authenticated raw call through `proxy`.
- **Framework adapters**: turn a user's tools into OpenAI, Anthropic, Vercel AI SDK (TypeScript), or LangChain tool definitions.
- **Triggers**: subscribe to provider events and verify signed webhook deliveries.

> AppConnect is in private beta. [Request access](https://www.appconnecthq.com/early-access?from=sdk) to get partner credentials.

## Documentation

The [`docs/`](docs/) directory holds the developer documentation:

- [Quickstart](docs/quickstart.mdx) and [Concepts](docs/concepts.mdx)
- Guides: [Hosted Link](docs/guides/hosted-link.mdx), [Tools](docs/guides/tools.mdx), [Framework adapters](docs/guides/framework-adapters.mdx), [Triggers and webhooks](docs/guides/triggers-and-webhooks.mdx), [Errors](docs/guides/errors.mdx), [Mobile apps](docs/guides/mobile-apps.mdx), [Using a coding agent](docs/guides/coding-agents.mdx)
- API reference, generated from source: [TypeScript](docs/reference/typescript/index.md) and [Python](docs/reference/python/index.md)
- Changelogs: [TypeScript](typescript/CHANGELOG.md) and [Python](python/CHANGELOG.md)

## Security

The SDKs are server-side. Keep your client secret, AppConnect access tokens, and provider tokens on your backend; never ship them in a browser or mobile bundle. Report vulnerabilities to support@appconnecthq.com rather than opening a public issue.

## Development

```bash
# TypeScript
cd typescript && bun install && bun run typecheck && bun run test && bun run build

# Python
cd python && uv sync --extra dev && uv run ruff check . && uv run mypy src && uv run pytest
```

## Releases

Registries don't allow a published version to be replaced, so each SDK is released in two stages:

| SDK        | Stage 1 (automatic on a version bump to `main`) | Stage 2 (manual, after verifying stage 1) |
| ---------- | ------------------------------------------------ | ----------------------------------------- |
| TypeScript | `npm.w3api.dev`                                  | npmjs.com (`Publish TypeScript SDK`, `registry=npmjs`) |
| Python     | TestPyPI                                         | PyPI (`Publish Python SDK`, `target=pypi`) |

Stage 2 refuses to publish a version that stage 1 hasn't published yet.

## License

[MIT](LICENSE)
