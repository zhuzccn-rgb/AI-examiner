"""OpenAI 响应转换器: LangGraph Stream → OpenAI Response"""

import json
import time
from typing import Iterator, Optional, List, Dict, Any

from utils.openai.types.response import (
    ChatCompletionChunk,
    ChatCompletionResponse,
    ChunkChoice,
    Delta,
    ToolCallChunk,
    ToolCallFunction,
    Choice,
    Message,
    Usage,
)


class ResponseConverter:
    """将 LangGraph 消息转换为 OpenAI 响应"""

    def __init__(self, request_id: str, model: str = "default"):
        self.request_id = request_id
        self.model = model
        self.created = int(time.time())
        self._sent_role = False  # 是否已发送 assistant role
        # 工具调用流式状态
        self._current_tool_calls: Dict[int, Dict[str, Any]] = {}  # index -> {id, name, args}

    def _create_chunk(
        self,
        delta: Delta,
        finish_reason: Optional[str] = None,
    ) -> ChatCompletionChunk:
        """创建流式响应 chunk"""
        return ChatCompletionChunk(
            id=self.request_id,
            object="chat.completion.chunk",
            created=self.created,
            model=self.model,
            choices=[
                ChunkChoice(
                    index=0,
                    delta=delta,
                    finish_reason=finish_reason,
                )
            ],
        )

    def iter_langgraph_stream(
        self, items: Iterator[Any]
    ) -> Iterator[str]:
        """
        直接处理 LangGraph 原始流，实现工具参数的增量输出

        Args:
            items: graph.stream(stream_mode="messages") 返回的迭代器
                   每个 item 是 (chunk, metadata) 元组

        Yields:
            SSE 格式字符串
        """
        # 跟踪是否已发送过 finish_reason（tool_calls 或 stop）
        sent_finish_reason = False

        for item in items:
            chunk, meta = item
            chunk_type = chunk.__class__.__name__

            # 过滤 tools 节点的消息
            if (meta or {}).get("langgraph_node") == "tools":
                # 但是 ToolMessage 需要处理
                if chunk_type != "ToolMessage":
                    continue

            # 处理前检查是否有工具调用（用于判断是否会发送 tool_calls finish_reason）
            had_tool_calls_before = bool(self._current_tool_calls)

            for sse_chunk in self._process_langgraph_chunk(chunk, meta):
                yield sse_chunk

            # 检查是否在处理过程中发送了 tool_calls finish_reason
            is_last = (meta or {}).get("chunk_position") == "last"
            if chunk_type == "AIMessageChunk" and is_last and had_tool_calls_before:
                # 处理过程中发送了 tool_calls finish_reason，重置标记
                sent_finish_reason = True
            elif chunk_type == "ToolMessage":
                # ToolMessage 后面还会有 assistant 消息，重置标记
                sent_finish_reason = False

        # 流结束时，如果发送过 role 但没有发送过 finish_reason，发送 stop
        if self._sent_role and not sent_finish_reason:
            yield self._chunk_to_sse(self._create_chunk(Delta(), finish_reason="stop"))

        yield "data: [DONE]\n\n"

    def _process_langgraph_chunk(
        self, chunk: Any, meta: Dict[str, Any]
    ) -> Iterator[str]:
        """处理单个 LangGraph chunk"""
        chunk_type = chunk.__class__.__name__
        is_last = (meta or {}).get("chunk_position") == "last"

        if chunk_type == "AIMessageChunk":
            yield from self._process_ai_message_chunk(chunk, meta, is_last)
        elif chunk_type == "AIMessage":
            yield from self._process_ai_message(chunk)
        elif chunk_type == "ToolMessage":
            yield from self._process_tool_message(chunk, meta, is_last)

    def _process_ai_message_chunk(
        self, chunk: Any, meta: Dict[str, Any], is_last: bool
    ) -> Iterator[str]:
        """处理 AIMessageChunk - 支持增量文本和工具调用"""
        # 处理文本内容
        text = getattr(chunk, "content", "")
        if text:
            # 先发送 role（如果还没发送）
            if not self._sent_role:
                self._sent_role = True
                yield self._chunk_to_sse(self._create_chunk(Delta(role="assistant")))
            yield self._chunk_to_sse(self._create_chunk(Delta(content=text)))

        # 处理工具调用增量
        tool_call_chunks = getattr(chunk, "tool_call_chunks", None)
        if tool_call_chunks:
            # 先发送 role（如果还没发送）
            if not self._sent_role:
                self._sent_role = True
                yield self._chunk_to_sse(self._create_chunk(Delta(role="assistant")))

            for tc_chunk in tool_call_chunks:
                yield from self._process_tool_call_chunk(tc_chunk)

        # 检查是否是工具调用结束
        finish_reason = None
        try:
            resp_meta = getattr(chunk, "response_metadata", {})
            if resp_meta and isinstance(resp_meta, dict):
                finish_reason = resp_meta.get("finish_reason")
        except Exception:
            pass

        if finish_reason == "tool_calls" or (is_last and self._current_tool_calls):
            # 工具调用结束，发送 finish_reason
            yield self._chunk_to_sse(self._create_chunk(Delta(), finish_reason="tool_calls"))
            self._current_tool_calls = {}
            self._sent_role = False

    def _process_tool_call_chunk(self, tc_chunk: Any) -> Iterator[str]:
        """处理单个工具调用增量 - 流式输出参数"""
        # 获取 chunk 属性
        if isinstance(tc_chunk, dict):
            index = tc_chunk.get("index", 0)
            tc_id = tc_chunk.get("id")
            tc_name = tc_chunk.get("name")
            tc_args = tc_chunk.get("args")
        else:
            index = getattr(tc_chunk, "index", 0)
            tc_id = getattr(tc_chunk, "id", None)
            tc_name = getattr(tc_chunk, "name", None)
            tc_args = getattr(tc_chunk, "args", None)

        if index is None:
            return

        # 规范化为字符串
        tc_id_str = self._normalize_to_string(tc_id)
        tc_name_str = self._normalize_to_string(tc_name)
        tc_args_str = self._normalize_to_string(tc_args)

        # 判断是否是新的工具调用
        is_new_tool_call = index not in self._current_tool_calls

        if is_new_tool_call:
            # 新工具调用，发送 id 和 name
            self._current_tool_calls[index] = {
                "id": tc_id_str,
                "name": tc_name_str,
                "args": tc_args_str,
            }
            # 发送初始 chunk（包含 id 和 name）
            tool_call = ToolCallChunk(
                index=index,
                id=tc_id_str if tc_id_str else None,
                type="function",
                function=ToolCallFunction(
                    name=tc_name_str,
                    arguments=tc_args_str,
                ),
            )
            yield self._chunk_to_sse(self._create_chunk(Delta(tool_calls=[tool_call])))
        else:
            # 已存在的工具调用，累加并发送增量
            existing = self._current_tool_calls[index]

            # 累加 id（通常 id 只在第一个 chunk 中）
            if tc_id_str:
                existing["id"] += tc_id_str

            # 累加 name（通常 name 只在前几个 chunk 中）
            if tc_name_str:
                existing["name"] += tc_name_str

            # 累加 args（参数是主要的流式内容）
            if tc_args_str:
                existing["args"] += tc_args_str
                # 发送参数增量
                tool_call = ToolCallChunk(
                    index=index,
                    id=None,  # 后续 chunk 不需要 id
                    type="function",
                    function=ToolCallFunction(
                        name="",  # 后续 chunk 不需要 name
                        arguments=tc_args_str,  # 只发送增量
                    ),
                )
                yield self._chunk_to_sse(self._create_chunk(Delta(tool_calls=[tool_call])))

    def _process_ai_message(self, chunk: Any) -> Iterator[str]:
        """处理完整的 AIMessage"""
        text = getattr(chunk, "content", "")
        if text:
            if not self._sent_role:
                self._sent_role = True
                yield self._chunk_to_sse(self._create_chunk(Delta(role="assistant")))
            yield self._chunk_to_sse(self._create_chunk(Delta(content=text)))

    def _process_tool_message(
        self, chunk: Any, meta: Dict[str, Any], is_last: bool
    ) -> Iterator[str]:
        """处理 ToolMessage - 工具执行结果"""
        is_streaming = (meta or {}).get("chunk_position") is not None

        # 只在完成时发送（非流式或 is_last）
        if not is_streaming or is_last:
            tool_call_id = getattr(chunk, "tool_call_id", "") or ""
            result = getattr(chunk, "content", "") or ""

            # 发送 tool 消息内容
            yield self._chunk_to_sse(
                self._create_chunk(
                    Delta(
                        role="tool",
                        tool_call_id=tool_call_id,
                        content=str(result),
                    )
                )
            )
            # 发送 tool 消息的 finish chunk
            yield self._chunk_to_sse(
                self._create_chunk(Delta(), finish_reason="stop")
            )

    @staticmethod
    def _normalize_to_string(value: Any) -> str:
        """将值规范化为字符串"""
        if value is None:
            return ""
        if isinstance(value, list):
            return "".join(str(x) for x in value)
        return str(value)

    def _chunk_to_sse(self, chunk: ChatCompletionChunk) -> str:
        """将 chunk 转换为 SSE 格式"""
        return f"data: {json.dumps(chunk.to_dict(), ensure_ascii=False)}\n\n"

    def collect_langgraph_to_response(
        self, items: Iterator[Any]
    ) -> ChatCompletionResponse:
        """
        从 LangGraph 原始流收集消息，返回非流式响应

        Args:
            items: graph.stream(stream_mode="messages") 返回的迭代器

        Note:
            非流式响应输出所有消息，包括 assistant、tool_calls、tool_response
            按消息顺序放入 choices 数组
        """
        # 收集所有消息，按顺序存储
        all_messages: List[Dict[str, Any]] = []

        # 当前 assistant 消息的累积状态
        current_content_parts: List[str] = []
        current_tool_calls: List[Dict[str, Any]] = []
        accumulated_tool_calls: Dict[int, Dict[str, Any]] = {}
        has_assistant_content = False

        def _flush_assistant_message():
            """将累积的 assistant 消息写入 all_messages"""
            nonlocal current_content_parts, current_tool_calls, accumulated_tool_calls, has_assistant_content

            # 先处理累积的工具调用
            if accumulated_tool_calls and not current_tool_calls:
                for index in sorted(accumulated_tool_calls.keys()):
                    tc_data = accumulated_tool_calls[index]
                    current_tool_calls.append({
                        "id": tc_data["id"],
                        "type": "function",
                        "function": {
                            "name": tc_data["name"],
                            "arguments": tc_data["args"],
                        },
                    })

            # 有内容或工具调用时才写入
            if current_content_parts or current_tool_calls:
                content = "".join(current_content_parts) if current_content_parts else None
                finish_reason = "tool_calls" if current_tool_calls else "stop"
                all_messages.append({
                    "role": "assistant",
                    "content": content,
                    "tool_calls": current_tool_calls if current_tool_calls else None,
                    "finish_reason": finish_reason,
                })

            # 重置状态
            current_content_parts = []
            current_tool_calls = []
            accumulated_tool_calls = {}
            has_assistant_content = False

        for item in items:
            chunk, meta = item
            chunk_type = chunk.__class__.__name__

            # 过滤 tools 节点的内部 AI 消息
            if (meta or {}).get("langgraph_node") == "tools":
                if chunk_type != "ToolMessage":
                    continue

            if chunk_type in ("AIMessageChunk", "AIMessage"):
                # 收集文本内容
                text = getattr(chunk, "content", "")
                if text:
                    current_content_parts.append(str(text))
                    has_assistant_content = True

                # 收集工具调用增量
                tc_chunks = getattr(chunk, "tool_call_chunks", None)
                if tc_chunks:
                    for tc in tc_chunks:
                        if isinstance(tc, dict):
                            index = tc.get("index", 0)
                            tc_id = tc.get("id")
                            tc_name = tc.get("name")
                            tc_args = tc.get("args")
                        else:
                            index = getattr(tc, "index", 0)
                            tc_id = getattr(tc, "id", None)
                            tc_name = getattr(tc, "name", None)
                            tc_args = getattr(tc, "args", None)

                        if index is None:
                            continue

                        tc_id_str = self._normalize_to_string(tc_id)
                        tc_name_str = self._normalize_to_string(tc_name)
                        tc_args_str = self._normalize_to_string(tc_args)

                        if index not in accumulated_tool_calls:
                            accumulated_tool_calls[index] = {
                                "id": tc_id_str,
                                "name": tc_name_str,
                                "args": tc_args_str,
                            }
                        else:
                            accumulated_tool_calls[index]["id"] += tc_id_str
                            accumulated_tool_calls[index]["name"] += tc_name_str
                            accumulated_tool_calls[index]["args"] += tc_args_str

                # 检查完整的 tool_calls (AIMessage)
                full_tool_calls = getattr(chunk, "tool_calls", None)
                if full_tool_calls and chunk_type == "AIMessage":
                    for tc in full_tool_calls:
                        tc_id = tc.get("id") if isinstance(tc, dict) else getattr(tc, "id", "")
                        tc_name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", "")
                        tc_args = tc.get("args") if isinstance(tc, dict) else getattr(tc, "args", {})

                        if isinstance(tc_args, str):
                            args_str = tc_args
                        else:
                            args_str = json.dumps(tc_args, ensure_ascii=False)

                        current_tool_calls.append({
                            "id": tc_id,
                            "type": "function",
                            "function": {
                                "name": tc_name,
                                "arguments": args_str,
                            },
                        })

            elif chunk_type == "ToolMessage":
                # 遇到 ToolMessage，先 flush 之前的 assistant 消息
                _flush_assistant_message()

                # 添加 tool 响应消息
                is_last = (meta or {}).get("chunk_position") == "last"
                is_streaming = (meta or {}).get("chunk_position") is not None

                # 只在完成时添加（非流式或 is_last）
                if not is_streaming or is_last:
                    tool_call_id = getattr(chunk, "tool_call_id", "") or ""
                    result = getattr(chunk, "content", "") or ""
                    all_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": str(result),
                        "finish_reason": "stop",
                    })

        # 最后 flush 剩余的 assistant 消息
        _flush_assistant_message()

        # 构建 choices
        choices: List[Choice] = []
        for idx, msg in enumerate(all_messages):
            if msg["role"] == "assistant":
                choices.append(
                    Choice(
                        index=idx,
                        message=Message(
                            role="assistant",
                            content=msg.get("content"),
                            tool_calls=msg.get("tool_calls"),
                        ),
                        finish_reason=msg.get("finish_reason", "stop"),
                    )
                )
            elif msg["role"] == "tool":
                choices.append(
                    Choice(
                        index=idx,
                        message=Message(
                            role="tool",
                            tool_call_id=msg.get("tool_call_id"),
                            content=msg.get("content"),
                        ),
                        finish_reason="stop",
                    )
                )

        # 如果没有任何消息，返回空 assistant 消息
        if not choices:
            choices.append(
                Choice(
                    index=0,
                    message=Message(role="assistant", content=None),
                    finish_reason="stop",
                )
            )

        return ChatCompletionResponse(
            id=self.request_id,
            object="chat.completion",
            created=self.created,
            model=self.model,
            choices=choices,
            usage=Usage(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
            ),
        )
