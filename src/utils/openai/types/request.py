"""OpenAI Chat Completions API 请求类型定义"""

from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict, Any


@dataclass
class ChatMessage:
    """聊天消息"""
    role: str  # "user" | "assistant" | "tool" | "system"
    content: Union[str, List[Dict[str, Any]], None] = None  # 支持多模态
    tool_calls: Optional[List[Dict[str, Any]]] = None  # 工具调用 (assistant)
    tool_call_id: Optional[str] = None  # 工具响应关联ID (tool)


@dataclass
class ChatCompletionRequest:
    """聊天完成请求"""
    messages: List[ChatMessage] = field(default_factory=list)
    model: str = "default"
    stream: bool = False
    session_id: str = ""  # 扩展字段：会话 ID
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
