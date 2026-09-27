# @appconnecthq/sdk

Server-side SDK for [AppConnectHQ](https://www.appconnecthq.com/sdk) partner apps: create Link
sessions, exchange OAuth tokens, list and execute unified tools, manage
triggers, and verify inbound webhook signatures.

## Install

```bash
npm install @appconnecthq/sdk
```

## Documentation

Guides and the full API reference live in [`docs/`](../docs/). Release notes are in
[`CHANGELOG.md`](CHANGELOG.md).

## Usage

```ts
import { AppConnectClient } from "@appconnecthq/sdk";

const client = new AppConnectClient({
  clientId: process.env.APPCONNECT_CLIENT_ID!,
  clientSecret: process.env.APPCONNECT_CLIENT_SECRET!,
});

// Create a hosted Link session for a user to connect a service.
const { link_url } = await client.createLinkToken({
  userId: "user_123",
  redirectUri: "https://yourapp.com/callback",
});

// Once connected, list and execute the tools available to that user.
const { tools } = await client.listTools(accessToken);
const { data } = await client.executeTool(accessToken, tools[0].id, {});
```

### Framework adapters

The main entry also exports OpenAI- and Anthropic-shaped tool adapters
(`toOpenAITools`/`executeOpenAIToolCall`, `toAnthropicTools`/
`executeAnthropicToolUse`), which have no extra dependencies. Adapters that
need an optional peer dependency are published as their own subpaths so
installing them stays opt-in:

```ts
// Needs the "ai" package (Vercel AI SDK).
import { toAISDKTools } from "@appconnecthq/sdk/ai-sdk";

// Needs "@langchain/core".
import { toLangChainTools } from "@appconnecthq/sdk/langchain";
```

### Webhook signature verification

```ts
import { verifyWebhookSignature } from "@appconnecthq/sdk";

const valid = verifyWebhookSignature(rawBody, req.headers["x-appconnect-signature"], signingSecret);
```

See `examples/` in this package for a runnable end-to-end "list -> adapt ->
model -> execute" tool-calling loop.
