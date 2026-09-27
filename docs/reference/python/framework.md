# Framework adapters

Import from `appconnect.framework`. `to_langchain_tools()` needs the `langchain` extra (`pip install "appconnect[langchain]"`).

## `OpenAIFunctionTool`

A tool in OpenAI chat-completions function-calling shape.

| Field | Type | Required |
| --- | --- | --- |
| `type` | `Literal['function']` | yes |
| `function` | `OpenAIFunctionDef` | yes |

## `OpenAIToolCall`

An OpenAI chat-completions tool call, as found on an assistant
message's `tool_calls`.

| Field | Type | Required |
| --- | --- | --- |
| `id` | `str` | yes |
| `function` | `OpenAIToolCallFunction` | yes |

## `OpenAIToolResultMessage`

The `{role: "tool", ...}` message OpenAI expects appended after a
tool call runs.

| Field | Type | Required |
| --- | --- | --- |
| `role` | `Literal['tool']` | yes |
| `tool_call_id` | `str` | yes |
| `content` | `str` | yes |

## `to_openai_tools()`

```python
async def to_openai_tools(client: AppConnectClient, access_token: str, tools: list[Tool] | None = None) -> list[OpenAIFunctionTool]
```

Maps AppConnect tools to OpenAI chat-completions function-calling
tools. Pass pre-fetched `tools` (e.g. from a prior `list_tools()` call)
to skip a round trip.

## `execute_openai_tool_call()`

```python
async def execute_openai_tool_call(client: AppConnectClient, access_token: str, tool_call: OpenAIToolCall) -> OpenAIToolResultMessage
```

Executes a single OpenAI tool call via `execute_tool` and returns the
`{role: "tool", ...}` message to append to the conversation.

## `AnthropicTool`

A tool in Anthropic Messages API tool-use shape.

| Field | Type | Required |
| --- | --- | --- |
| `name` | `str` | yes |
| `description` | `str` | yes |
| `input_schema` | `AnthropicInputSchema` | yes |

## `AnthropicToolUseBlock`

A `tool_use` content block from an Anthropic assistant message.

| Field | Type | Required |
| --- | --- | --- |
| `type` | `Literal['tool_use']` | yes |
| `id` | `str` | yes |
| `name` | `str` | yes |
| `input` | `dict[str, Any]` | yes |

## `AnthropicToolResultBlock`

The `tool_result` content block Anthropic expects in the following
user turn.

| Field | Type | Required |
| --- | --- | --- |
| `type` | `Literal['tool_result']` | yes |
| `tool_use_id` | `str` | yes |
| `content` | `str` | yes |

## `to_anthropic_tools()`

```python
async def to_anthropic_tools(client: AppConnectClient, access_token: str, tools: list[Tool] | None = None) -> list[AnthropicTool]
```

Maps AppConnect tools to Anthropic Messages API tool-use tools. Pass
pre-fetched `tools` (e.g. from a prior `list_tools()` call) to skip a
round trip.

## `execute_anthropic_tool_use()`

```python
async def execute_anthropic_tool_use(client: AppConnectClient, access_token: str, tool_use: AnthropicToolUseBlock) -> AnthropicToolResultBlock
```

Executes a single Anthropic `tool_use` block via `execute_tool` and
returns the `tool_result` content block to append to the next user
turn.

## `to_langchain_tools()`

```python
async def to_langchain_tools(client: AppConnectClient, access_token: str, tools: list[Tool] | None = None) -> list[StructuredTool]
```

Maps AppConnect tools to real LangChain `StructuredTool` instances.
Pass pre-fetched `tools` (e.g. from a prior `list_tools()` call) to skip
a round trip. Requires the `langchain` extra.
