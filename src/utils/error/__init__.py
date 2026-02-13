"""
VibeCoding Error Module

6位错误码体系设计:
- 第1位: 错误大类 (1-9)
- 第2-3位: 错误子类 (01-99)
- 第4-6位: 具体错误 (001-999)

错误大类:
1xxxxx - 代码语法/类型错误 (Code Syntax/Type Errors)
2xxxxx - 输入验证错误 (Input Validation Errors)
3xxxxx - 外部API错误 (External API Errors)
4xxxxx - 资源/文件错误 (Resource/File Errors)
5xxxxx - 集成服务错误 (Integration Service Errors)
6xxxxx - 业务逻辑错误 (Business Logic Errors)
7xxxxx - 运行时错误 (Runtime Errors)
8xxxxx - 配置错误 (Configuration Errors)
9xxxxx - 未知错误 (Unknown Errors)
"""

from .codes import ErrorCode, ErrorCategory
from .exceptions import VibeCodingError, classify_error
from .classifier import ErrorClassifier

__all__ = [
    "ErrorCode",
    "ErrorCategory",
    "VibeCodingError",
    "classify_error",
    "ErrorClassifier",
]
