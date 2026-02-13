"""OpenAI Chat Completions API 响应类型定义"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any


@dataclass
class ToolCallFunction:
    """工具调用函数"""
    name: str = ""
    arguments: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "arguments": self.arguments}


@dataclass
class ToolCallChunk:
    """工具调用增量 (流式)"""
    index: int = 0
    id: Optional[str] = None
    type: str = "function"
    function: Optional[ToolCallFunction] = None

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {"index": self.index, "type": self.type}
        if self.id is not None:
            result["id"] = self.id
        if self.function is not None:
            result["function"] = self.function.to_dict()
        return result


@dataclass
class Delta:
    """流式响应增量"""
    role: Optional[str] = None  # "assistant" | "tool"
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCallChunk]] = None
    tool_call_id: Optional[str] = None  # role=tool 时使用

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        if self.role is not None:
            result["role"] = self.role
        if self.content is not None:
            result["content"] = self.content
        if self.tool_calls is not None:
            result["tool_calls"] = [tc.to_dict() for tc in self.tool_calls]
        if self.tool_call_id is not None:
            result["tool_call_id"] = self.tool_call_id
        return result


@dataclass
class ChunkChoice:
    """流式响应选项"""
    index: int = 0
    delta: Delta = field(default_factory=Delta)
    finish_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "index": self.index,
            "delta": self.delta.to_dict(),
        }
        # finish_reason 需要显式设置为 null
        result["finish_reason"] = self.finish_reason
        return result


@dataclass
class ChatCompletionChunk:
    """流式响应 chunk"""
    id: str = ""
    object: str = "chat.completion.chunk"
    created: int = 0
    model: str = "default"
    choices: List[ChunkChoice] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "object": self.object,
            "created": self.created,
            "model": self.model,
            "choices": [c.to_dict() for c in self.choices],
        }


@dataclass
class Usage:
    """Token 使用情况"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Message:
    """非流式响应消息"""
    role: str = "assistant"
    content: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {"role": self.role}
        if self.content is not None:
            result["content"] = self.content
        if self.tool_calls is not None:
            result["tool_calls"] = self.tool_calls
        if self.tool_call_id is not None:
            result["tool_call_id"] = self.tool_call_id
        return result


@dataclass
class Choice:
    """非流式响应选项"""
    index: int = 0
    message: Message = field(default_factory=Message)
    finish_reason: str = "stop"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "message": self.message.to_dict(),
            "finish_reason": self.finish_reason,
        }


@dataclass
class ChatCompletionResponse:
    """非流式响应"""
    id: str = ""
    object: str = "chat.completion"
    created: int = 0
    model: str = "default"
    choices: List[Choice] = field(default_factory=list)
    usage: Usage = field(default_factory=Usage)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "object": self.object,
            "created": self.created,
            "model": self.model,
            "choices": [c.to_dict() for c in self.choices],
            "usage": self.usage.to_dict(),
        }


@dataclass
class OpenAIError:
    """OpenAI 错误"""
    message: str = ""
    type: str = "internal_error"
    code: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message": self.message,
            "type": self.type,
            "code": self.code,
        }


@dataclass
class OpenAIErrorResponse:
    """OpenAI 错误响应"""
    error: OpenAIError = field(default_factory=OpenAIError)

    def to_dict(self) -> Dict[str, Any]:
        return {"error": self.error.to_dict()}
