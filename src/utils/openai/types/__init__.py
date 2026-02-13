"""OpenAI 类型定义"""

from utils.openai.types.request import (
    ChatMessage,
    ChatCompletionRequest,
)
from utils.openai.types.response import (
    ToolCallFunction,
    ToolCallChunk,
    Delta,
    ChunkChoice,
    ChatCompletionChunk,
    Usage,
    Message,
    Choice,
    ChatCompletionResponse,
    OpenAIError,
    OpenAIErrorResponse,
)

__all__ = [
    # Request types
    "ChatMessage",
    "ChatCompletionRequest",
    # Response types
    "ToolCallFunction",
    "ToolCallChunk",
    "Delta",
    "ChunkChoice",
    "ChatCompletionChunk",
    "Usage",
    "Message",
    "Choice",
    "ChatCompletionResponse",
    "OpenAIError",
    "OpenAIErrorResponse",
]
