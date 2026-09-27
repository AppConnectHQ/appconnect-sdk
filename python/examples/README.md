# SDK examples

Runnable end-to-end examples for the `appconnect` Python SDK. Companion to the
TypeScript example at `typescript/examples/`.

## `openai_agent.py`

Drives the full "list -> adapt -> model -> execute" loop:

1. `client.list_tools(access_token)` — list every tool the connected user
   has access to.
2. `to_openai_tools(client, access_token, tools)` — adapt them to OpenAI
   chat-completions function-calling format.
3. Call an OpenAI model with those tools attached.
4. For each `tool_calls` entry the model returns,
   `execute_openai_tool_call(client, access_token, tool_call)` runs it
   through AppConnect's `execute_tool` and the result is fed back to the
   model for a final answer.

### Prerequisites

1. AppConnect partner credentials (the SDK is in private beta; request access
   at https://www.appconnecthq.com/sdk).
2. An **AppConnect access token** for a user who already has at least one
   connected service: the bearer token `client.exchange_link_token(...)`
   returns after the user completes a hosted Link session.
3. The project venv, with dev deps installed:
   ```bash
   cd python
   uv venv          # if you haven't already
   uv pip install -e ".[dev]"
   ```

### Run it

```bash
export APPCONNECT_ACCESS_TOKEN=apphq_...

# Mocked model response (no OpenAI key needed / spent):
uv run python -m examples.openai_agent --mock

# Real OpenAI model:
export OPENAI_API_KEY=sk-...
uv run python -m examples.openai_agent
```

Run as a module (`-m examples.openai_agent`) from `python/`, not as a
bare script — `openai_agent.py` uses a relative import (`from .mock_model
import ...`) to reach its mock-turn helpers.

`--mock` (or simply omitting `OPENAI_API_KEY`) substitutes a deterministic
mocked model turn from `./mock_model.py` instead of calling OpenAI, so the
example is always runnable without spending API credits or holding an LLM
key. The mock **only ever calls a `GET` (read-only) tool** — never a
mutating one — so running it never writes to a connected service on your
behalf.

### Env vars

| Var                       | Required | Default                 | Purpose                             |
| ------------------------- | -------- | ----------------------- | ----------------------------------- |
| `APPCONNECT_ACCESS_TOKEN` | yes      | —                       | Bearer token for the connected user |
| `PRODUCTION_API_ORIGIN`   | yes      | —                       | Origin supplied during onboarding   |
| `OPENAI_API_KEY`          | no       | —                       | Real OpenAI key; absent ⇒ mock mode |
| `OPENAI_MODEL`            | no       | `gpt-4o-mini`           | Chat-completions model              |
| `APPCONNECT_PROMPT`       | no       | (a generic read prompt) | User message sent to the model      |

### Files

- `__init__.py` — package marker (not part of the installed `appconnect`
  package; only `src/appconnect` ships, see `pyproject.toml`). Lets the
  example run via `-m examples.openai_agent` and lets `tests/` import
  `examples.mock_model` (via `pythonpath = ["."]` in `pyproject.toml`).
- `openai_agent.py` — the runnable script (`main()`, OpenAI HTTP call via
  `httpx`, env parsing).
- `mock_model.py` — pure mock-turn logic, unit tested in
  `tests/test_example_mock_model.py` (`uv run pytest`). Kept separate so
  it's testable without touching the network or environment variables.
