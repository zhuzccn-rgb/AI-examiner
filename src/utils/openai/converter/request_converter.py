"""OpenAI 请求转换器: OpenAI Request → LangGraph Input"""

from typing import Dict, Any, List
from utils.openai.types.request import (
    ChatCompletionRequest,
    ChatMessage,
)
from utils.file.file import File, FileOps, infer_file_category


class RequestConverter:
    """将 OpenAI 请求转换为 LangGraph 输入"""

    @staticmethod
    def parse(payload: Dict[str, Any]) -> ChatCompletionRequest:
        """解析 JSON payload 为 ChatCompletionRequest"""
        messages_raw = payload.get("messages", [])
        messages: List[ChatMessage] = []

        for msg_data in messages_raw:
            messages.append(ChatMessage(
                role=msg_data.get("role", "user"),
                content=msg_data.get("content"),
                tool_calls=msg_data.get("tool_calls"),
                tool_call_id=msg_data.get("tool_call_id"),
            ))

        return ChatCompletionRequest(
            messages=messages,
            model=payload.get("model", "default"),
            stream=payload.get("stream", False),
            session_id=payload.get("session_id", ""),
            temperature=payload.get("temperature"),
            max_tokens=payload.get("max_tokens"),
        )

    @staticmethod
    def get_session_id(request: ChatCompletionRequest) -> str:
        """提取 session_id"""
        return request.session_id

    @staticmethod
    def to_stream_input(request: ChatCompletionRequest) -> Dict[str, Any]:
        """
        转换为 LangGraph stream 输入格式

        只取最后一条 user 消息进行处理，历史由 session_id + checkpointer 管理
        """
        # 找到最后一条 user 消息
        last_user_msg: ChatMessage | None = None
        for msg in reversed(request.messages):
            if msg.role == "user":
                last_user_msg = msg
                break

        if last_user_msg is None:
            return {"messages": []}

        content_parts = RequestConverter._convert_content(last_user_msg.content)
        return {"messages": [{"role": "user", "content": content_parts}]}

    @staticmethod
    def _convert_content(content: Any) -> List[Dict[str, Any]]:
        """
        转换消息内容为 LangGraph 格式

        支持:
        - 字符串: 直接转为 text 类型
        - 列表: 处理多模态内容 (text, image_url, video_url)
        """
        if content is None:
            return []

        # 字符串内容
        if isinstance(content, str):
            return [{"type": "text", "text": content}]

        # 多模态内容列表
        if isinstance(content, list):
            result: List[Dict[str, Any]] = []
            for part in content:
                converted = RequestConverter._convert_content_part(part)
                result.extend(converted)
            return result

        return []

    @staticmethod
    def _convert_content_part(part: Dict[str, Any]) -> List[Dict[str, Any]]:
        """转换单个内容部分"""
        part_type = part.get("type", "text")

        if part_type == "text":
            text = part.get("text", "")
            if text:
                return [{"type": "text", "text": text}]
            return []

        if part_type == "image_url":
            image_url_data = part.get("image_url", {})
            url = image_url_data.get("url", "")
            if url:
                return [
                    {"type": "text", "text": url},
                    {"type": "image_url", "image_url": {"url": url}},
                ]
            return []

        if part_type == "video_url":
            video_url_data = part.get("video_url", {})
            url = video_url_data.get("url", "")
            if url:
                return [
                    {"type": "text", "text": url},
                    {"type": "video_url", "video_url": {"url": url}},
                ]
            return []

        if part_type == "audio_url":
            audio_url_data = part.get("audio_url", {})
            url = audio_url_data.get("url", "")
            if url:
                return [{"type": "text", "text": f"audio url: {url}"}]
            return []

        if part_type == "file_url":
            # 处理文件 URL，提取文件内容
            file_url_data = part.get("file_url", {})
            url = file_url_data.get("url", "")
            file_name = file_url_data.get("file_name", "")
            if url:
                return RequestConverter._process_file_url(url, file_name)
            return []

        return []

    @staticmethod
    def _process_file_url(url: str, file_name: str = "") -> List[Dict[str, Any]]:
        """处理文件 URL，根据文件类型进行不同处理"""
        try:
            file_type, _ = infer_file_category(url)
            file_data = File(url=url, file_type=file_type)

            if file_type == "image":
                return [
                    {"type": "text", "text": url},
                    {"type": "image_url", "image_url": {"url": url}},
                ]
            elif file_type == "video":
                return [
                    {"type": "text", "text": url},
                    {"type": "video_url", "video_url": {"url": url}},
                ]
            elif file_type == "audio":
                return [{"type": "text", "text": f"audio url: {url}"}]
            else:
                # 其他文件类型，尝试提取文本内容
                file_content = FileOps.extract_text(file_data)
                return [{
                    "type": "text",
                    "text": f"file name: {file_name}, url: {url}\n\nFile Content:\n{file_content}",
                }]
        except Exception:
            # 如果文件处理失败，返回 URL 文本
            return [{"type": "text", "text": f"file url: {url}"}]
