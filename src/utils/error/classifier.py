"""
错误分类器 - 提供高层API用于错误分析和统计
"""

import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

from .codes import ErrorCategory, get_error_description
from .exceptions import VibeCodingError, classify_error
from ..log.err_trace import extract_core_stack

logger = logging.getLogger(__name__)


@dataclass
class ErrorInfo:
    """错误信息结构"""
    code: int
    message: str
    category: ErrorCategory
    category_name: str
    description: str
    original_type: str = ""
    original_message: str = ""
    node_name: str = ""
    task_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "category": self.category.value,
            "category_name": self.category_name,
            "description": self.description,
            "original_type": self.original_type,
            "node_name": self.node_name,
            "task_id": self.task_id,
        }


@dataclass
class ErrorStats:
    """错误统计结构"""
    total_count: int = 0
    by_category: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    by_code: Dict[int, int] = field(default_factory=lambda: defaultdict(int))
    by_node: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    recent_errors: List[ErrorInfo] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_count": self.total_count,
            "by_category": dict(self.by_category),
            "by_code": {str(k): v for k, v in self.by_code.items()},
            "by_node": dict(self.by_node),
            "recent_errors": [e.to_dict() for e in self.recent_errors[-10:]],  # 最近10个错误
        }


class ErrorClassifier:
    """
    错误分类器

    提供:
    1. 异常分类: classify() - 将异常转换为带错误码的VibeCodingError
    2. 错误信息提取: extract_error_info() - 从异常提取结构化错误信息
    3. 错误统计: 记录和统计错误分布
    """

    def __init__(self, max_recent_errors: int = 100):
        self._stats = ErrorStats()
        self._max_recent_errors = max_recent_errors

    def classify(
            self,
            error: BaseException,
            context: Optional[Dict[str, Any]] = None
    ) -> VibeCodingError:
        """
        分类错误并返回VibeCodingError

        Args:
            error: 原始异常
            context: 额外上下文 (如 node_name, task_id 等)

        Returns:
            VibeCodingError: 带有6位错误码的异常
        """
        err = classify_error(error, context)

        # 更新统计
        self._update_stats(err, context)

        return err

    def extract_error_info(
            self,
            error: BaseException,
            context: Optional[Dict[str, Any]] = None
    ) -> ErrorInfo:
        """
        从异常提取结构化错误信息

        Args:
            error: 原始异常
            context: 额外上下文

        Returns:
            ErrorInfo: 结构化错误信息
        """
        err = classify_error(error, context)
        ctx = context or {}

        return ErrorInfo(
            code=err.code,
            message=err.message,
            category=err.category,
            category_name=err.category.name,
            description=get_error_description(err.code),
            original_type=type(error).__name__,
            original_message=str(error)[:500],
            node_name=ctx.get("node_name", ""),
            task_id=ctx.get("task_id", ""),
        )

    def get_error_code(
            self,
            error: BaseException,
            context: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        获取错误码 (简化接口)

        Args:
            error: 原始异常
            context: 额外上下文

        Returns:
            int: 6位错误码
        """
        err = classify_error(error, context)
        return err.code

    def get_error_response(
            self,
            error: BaseException,
            context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        获取用于API响应的错误信息

        Args:
            error: 原始异常
            context: 额外上下文

        Returns:
            dict: 包含 code, message, category 的字典
        """
        err = self.classify(error, context)
        logger.error(f"Error classifier classify error: {error}, traceback: {extract_core_stack()}, get error code: {err.code}, error message: {err.message}, error category: {err.category.name}")

        return {
            "error_code": err.code,
            "error_message": err.message,
            "error_category": err.category.name,
        }

    def _update_stats(
            self,
            error: VibeCodingError,
            context: Optional[Dict[str, Any]] = None
    ):
        """更新错误统计"""
        ctx = context or {}

        self._stats.total_count += 1
        self._stats.by_category[error.category.name] += 1
        self._stats.by_code[error.code] += 1

        node_name = ctx.get("node_name", "unknown")
        if node_name:
            self._stats.by_node[node_name] += 1

        # 记录最近的错误
        error_info = ErrorInfo(
            code=error.code,
            message=error.message,
            category=error.category,
            category_name=error.category.name,
            description=get_error_description(error.code),
            original_type=ctx.get("original_type", ""),
            original_message=ctx.get("original_message", "")[:200],
            node_name=node_name,
            task_id=ctx.get("task_id", ""),
        )
        self._stats.recent_errors.append(error_info)

        # 限制最近错误数量
        if len(self._stats.recent_errors) > self._max_recent_errors:
            self._stats.recent_errors = self._stats.recent_errors[-self._max_recent_errors:]

    def get_stats(self) -> ErrorStats:
        """获取错误统计"""
        return self._stats

    def reset_stats(self):
        """重置统计"""
        self._stats = ErrorStats()

    @staticmethod
    def parse_error_from_log(log_line: str) -> Optional[ErrorInfo]:
        """
        从日志行解析错误信息

        支持解析格式:
        - "During task with name 'xxx' and id 'xxx'"
        - "Before task with name 'xxx'"
        - 标准 Python Traceback

        Args:
            log_line: 日志行

        Returns:
            ErrorInfo: 解析出的错误信息，解析失败返回None
        """
        try:
            # 提取任务名称
            node_match = re.search(r"(?:During|Before) task with name '(\w+)'", log_line)
            node_name = node_match.group(1) if node_match else ""

            # 提取任务ID
            task_match = re.search(r"id '([a-f0-9-]+)'", log_line)
            task_id = task_match.group(1) if task_match else ""

            # 提取错误类型和消息
            # 格式1: "ExceptionType: message"
            error_match = re.search(r"(\w+Error|\w+Exception): (.+?)(?:\"|\]|$)", log_line)
            if not error_match:
                # 格式2: 在 Traceback 列表中
                error_match = re.search(r"'(\w+Error|\w+Exception): (.+?)'", log_line)

            if error_match:
                error_type = error_match.group(1)
                error_message = error_match.group(2)

                # 创建模拟异常进行分类
                mock_error = _create_mock_exception(error_type, error_message)
                err = classify_error(mock_error, {"node_name": node_name, "task_id": task_id})

                return ErrorInfo(
                    code=err.code,
                    message=err.message,
                    category=err.category,
                    category_name=err.category.name,
                    description=get_error_description(err.code),
                    original_type=error_type,
                    original_message=error_message[:200],
                    node_name=node_name,
                    task_id=task_id,
                )

            return None

        except Exception as e:
            logger.warning(f"Failed to parse error from log: {e}")
            return None


def _create_mock_exception(error_type: str, error_message: str) -> BaseException:
    """创建模拟异常用于分类"""
    exception_map = {
        "AttributeError": AttributeError,
        "TypeError": TypeError,
        "ValueError": ValueError,
        "KeyError": KeyError,
        "IndexError": IndexError,
        "NameError": NameError,
        "ImportError": ImportError,
        "ModuleNotFoundError": ModuleNotFoundError,
        "SyntaxError": SyntaxError,
        "IndentationError": IndentationError,
        "RuntimeError": RuntimeError,
        "NotImplementedError": NotImplementedError,
        "TimeoutError": TimeoutError,
        "FileNotFoundError": FileNotFoundError,
        "IOError": IOError,
        "OSError": OSError,
        "MemoryError": MemoryError,
        "RecursionError": RecursionError,
    }

    # Pydantic ValidationError 特殊处理
    if "ValidationError" in error_type:
        return Exception(f"ValidationError: {error_message}")

    # API Error 特殊处理
    if "APIError" in error_type:
        return Exception(f"APIError: {error_message}")

    exception_class = exception_map.get(error_type, Exception)

    try:
        return exception_class(error_message)
    except Exception:
        return Exception(f"{error_type}: {error_message}")


# 全局分类器实例 (单例模式)
_global_classifier: Optional[ErrorClassifier] = None


def get_classifier() -> ErrorClassifier:
    """获取全局错误分类器实例"""
    global _global_classifier
    if _global_classifier is None:
        _global_classifier = ErrorClassifier()
    return _global_classifier
