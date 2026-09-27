# SDK examples

Runnable end-to-end examples for `@appconnecthq/sdk`. Companion to the Python
example at `python/examples/`.

## `ts-openai-agent.ts`

Drives the full "list -> adapt -> model -> execute" loop:

1. `client.listTools(accessToken)` — list every tool the connected user has
   access to.
2. `toOpenAITools({ client, accessToken, tools })` — adapt them to OpenAI
   chat-completions function-calling format.
3. Call an OpenAI model with those tools attached.
4. For each `tool_calls` entry the model returns,
   `executeOpenAIToolCall({ client, accessToken, tools }, toolCall)` runs it
   through AppConnect's `executeTool` and the result is fed back to the
   model for a final answer.

### Prerequisites

1. AppConnect partner credentials (the SDK is in private beta; request access
   at https://www.appconnecthq.com/sdk).
2. An **AppConnect access token** for a user who already has at least one
   connected service: the bearer token `client.exchangeLinkToken(...)`
   returns after the user completes a hosted Link session.

### Run it

```bash
export APPCONNECT_ACCESS_TOKEN=apphq_...

# Mocked model response (no OpenAI key needed / spent):
bun examples/ts-openai-agent.ts --mock

# Real OpenAI model:
export OPENAI_API_KEY=sk-...
bun examples/ts-openai-agent.ts
```

`--mock` (or simply omitting `OPENAI_API_KEY`) substitutes a deterministic
mocked model turn from `./mock-model.ts` instead of calling OpenAI, so the
example is always runnable without spending API credits or holding an LLM
key. The mock **only ever calls a `GET` (read-only) tool** — never a
mutating one — so running it never writes to a connected service on your
behalf.

### Env vars

| Var                       | Required | Default                 | Purpose                             |
| ------------------------- | -------- | ----------------------- | ----------------------------------- |
| `APPCONNECT_ACCESS_TOKEN` | yes      | —                       | Bearer token for the connected user |
| `OPENAI_API_KEY`          | no       | —                       | Real OpenAI key; absent ⇒ mock mode |
| `OPENAI_MODEL`            | no       | `gpt-4o-mini`           | Chat-completions model              |
| `APPCONNECT_PROMPT`       | no       | (a generic read prompt) | User message sent to the model      |

### Files

- `ts-openai-agent.ts` — the runnable script (`main()`, OpenAI HTTP call,
  env parsing).
- `mock-model.ts` — pure mock-turn logic, unit tested in
  `mock-model.test.ts` (`bun run test`). Kept separate
  so it's testable without touching the network or `process.env`.
