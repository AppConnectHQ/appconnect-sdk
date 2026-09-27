"""Framework adapters mapping AppConnect tools to framework-native shapes.

Only `appconnect.framework.langchain`'s actual `langchain_core` import is
lazy/guarded (inside `to_langchain_tools`, behind a helpful `ImportError`) --
importing this barrel never requires the `langchain` extra to be installed.
`openai`/`anthropic` need no extra runtime dependency at all.
"""

from appconnect.framework.anthropic import (
    AnthropicTool,
    AnthropicToolResultBlock,
    AnthropicToolUseBlock,
    execute_anthropic_tool_use,
    to_anthropic_tools,
)
from appconnect.framework.langchain import to_langchain_tools
from appconnect.framework.openai import (
    OpenAIFunctionTool,
    OpenAIToolCall,
    OpenAIToolResultMessage,
    execute_openai_tool_call,
    to_openai_tools,
)

__all__ = [
    "OpenAIFunctionTool",
    "OpenAIToolCall",
    "OpenAIToolResultMessage",
    "to_openai_tools",
    "execute_openai_tool_call",
    "AnthropicTool",
    "AnthropicToolUseBlock",
    "AnthropicToolResultBlock",
    "to_anthropic_tools",
    "execute_anthropic_tool_use",
    "to_langchain_tools",
]
