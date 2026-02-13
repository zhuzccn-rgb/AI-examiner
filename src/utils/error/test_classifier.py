#!/usr/bin/env python3
"""
测试脚本：分析 err_log.txt 中的错误并进行分类统计
"""

import re
import sys
from collections import defaultdict
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.error.classifier import ErrorClassifier
from utils.error.codes import ErrorCode, get_error_description


def parse_log_file(log_path: str, max_lines: int = None):
    """解析日志文件，提取错误信息"""
    errors = []

    with open(log_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if max_lines:
            lines = lines[:max_lines]

    for line_no, line in enumerate(lines, 1):
        # 提取任务名称
        node_match = re.search(r"(?:During|Before) task with name '(\w+)'", line)
        node_name = node_match.group(1) if node_match else "unknown"

        # 提取错误类型和消息
        # 格式: 'ErrorType: message' 或 "ErrorType: message"
        error_patterns = [
            # pydantic ValidationError 格式 (优先匹配，因为格式特殊)
            r'"(pydantic_core\._pydantic_core\.ValidationError): ([^"]+)"',
            r"'(pydantic_core\._pydantic_core\.ValidationError): ([^']+)'",
            # openai.APIError 格式
            r'"(openai\.APIError): ([^"]+)"',
            r"'(openai\.APIError): ([^']+)'",
            # langgraph 错误格式 (无引号包裹)
            r"(langgraph\.errors\.\w+Error): ([^'\"]+?)(?:'|\"|\]|,)",
            # requests 异常格式
            r"(requests\.exceptions\.\w+): ([^'\"]+?)(?:'|\"|\]|,|During)",
            # subprocess 异常格式
            r"(subprocess\.\w+): ([^'\"]+?)(?:'|\"|\]|,|During)",
            # greenlet 错误格式
            r"(greenlet\.error): ([^'\"]+?)(?:'|\"|\]|,|During)",
            # cv2 错误格式
            r"(cv2\.error): ([^'\"]+?)(?:'|\"|\]|,|During)",
            # botocore 错误格式
            r"(botocore\.errorfactory\.\w+): ([^'\"]+?)(?:'|\"|\]|,|During)",
            # 标准格式 (带模块路径): 'module.Error: message'
            r'"([\w.]+Error): ([^"]+)"',
            r"'([\w.]+Error): ([^']+)'",
            r'"([\w.]+Exception): ([^"]+)"',
            r"'([\w.]+Exception): ([^']+)'",
            # 无引号包裹的错误格式
            r"([\w.]+Error): ([^'\"]+?)(?:'|\"|\]|,|During)",
            r"([\w.]+Exception): ([^'\"]+?)(?:'|\"|\]|,|During)",
        ]

        for pattern in error_patterns:
            match = re.search(pattern, line)
            if match:
                error_type = match.group(1)
                # 简化类型名
                if "." in error_type:
                    error_type = error_type.split(".")[-1]
                error_message = match.group(2)
                errors.append({
                    "line_no": line_no,
                    "node_name": node_name,
                    "error_type": error_type,
                    "error_message": error_message[:300],
                })
                break

    return errors


def analyze_errors(errors: list):
    """使用 ErrorClassifier 分析错误"""
    classifier = ErrorClassifier()
    results = []

    for err in errors:
        # 创建模拟异常
        error_type = err["error_type"]
        error_message = err["error_message"]

        # 根据错误类型创建对应的异常
        exception_map = {
            "AttributeError": AttributeError,
            "TypeError": TypeError,
            "ValueError": ValueError,
            "KeyError": KeyError,
            "IndexError": IndexError,
            "NameError": NameError,
            "RuntimeError": RuntimeError,
            "NotImplementedError": NotImplementedError,
            "FileNotFoundError": FileNotFoundError,
            "ImportError": ImportError,
            "ModuleNotFoundError": ModuleNotFoundError,
            "OSError": OSError,
            "IOError": IOError,
            "ConnectionError": ConnectionError,
            "TimeoutError": TimeoutError,
            "UnboundLocalError": UnboundLocalError,
            "RecursionError": RecursionError,
            "PermissionError": PermissionError,
            "ZeroDivisionError": ZeroDivisionError,
            "StopIteration": StopIteration,
            "AssertionError": AssertionError,
            "SyntaxError": SyntaxError,
            "IndentationError": IndentationError,
            "UnicodeDecodeError": UnicodeDecodeError,
            "UnicodeEncodeError": UnicodeEncodeError,
        }

        exc_class = exception_map.get(error_type, Exception)

        # 特殊错误类型处理
        if "ValidationError" in error_type:
            # Pydantic ValidationError - 需要保留完整格式以便分类
            mock_error = Exception(f"pydantic ValidationError: {error_message}")
        elif "APIError" in error_type:
            mock_error = Exception(f"openai.APIError: {error_message}")
        elif "InvalidUpdateError" in error_type:
            mock_error = Exception(f"langgraph.InvalidUpdateError: {error_message}")
        elif "GraphRecursionError" in error_type:
            mock_error = RecursionError(error_message)
        elif "MissingSchema" in error_type or "InvalidSchema" in error_type:
            # requests URL schema 错误
            mock_error = Exception(f"requests.exceptions.{error_type}: {error_message}")
        elif "ConnectTimeout" in error_type or "ReadTimeout" in error_type:
            # requests 超时错误
            mock_error = TimeoutError(f"requests timeout: {error_message}")
        elif "ConnectionError" in error_type and "requests" in str(err.get("original_type", "")):
            mock_error = ConnectionError(f"requests connection: {error_message}")
        elif "TimeoutExpired" in error_type:
            # subprocess 超时
            mock_error = TimeoutError(f"subprocess timeout: {error_message}")
        elif "error" in error_type and ("greenlet" in error_type or "cv2" in error_type):
            # greenlet 或 cv2 错误
            mock_error = Exception(f"{error_type}: {error_message}")
        elif "NoSuchBucket" in error_type:
            # botocore S3 错误
            mock_error = Exception(f"S3 bucket not found: {error_message}")
        else:
            try:
                mock_error = exc_class(error_message)
            except:
                mock_error = Exception(f"{error_type}: {error_message}")

        # 分类错误
        error_info = classifier.extract_error_info(
            mock_error,
            {"node_name": err["node_name"]}
        )

        results.append({
            "line_no": err["line_no"],
            "node_name": err["node_name"],
            "original_type": err["error_type"],
            "original_message": err["error_message"][:100],
            "error_code": error_info.code,
            "error_category": error_info.category_name,
            "classified_message": error_info.message[:100],
        })

    return results


def print_statistics(results: list):
    """打印统计信息"""
    print("\n" + "=" * 80)
    print("错误分类统计报告")
    print("=" * 80)

    # 按错误码统计
    by_code = defaultdict(int)
    by_category = defaultdict(int)
    by_node = defaultdict(int)

    for r in results:
        by_code[r["error_code"]] += 1
        by_category[r["error_category"]] += 1
        by_node[r["node_name"]] += 1

    # 打印按类别统计
    print(f"\n总错误数: {len(results)}")
    print("\n【按错误大类统计】")
    print("-" * 50)
    for category, count in sorted(by_category.items(), key=lambda x: -x[1]):
        print(f"  {category:30s}: {count:5d} ({count*100/len(results):5.1f}%)")

    # 打印按错误码统计 (Top 20)
    print("\n【按错误码统计 (Top 20)】")
    print("-" * 70)
    for code, count in sorted(by_code.items(), key=lambda x: -x[1])[:20]:
        desc = get_error_description(code)
        print(f"  {code:6d} | {desc:40s} | {count:5d}")

    # 打印按节点统计 (Top 15)
    print("\n【按节点统计 (Top 15)】")
    print("-" * 50)
    for node, count in sorted(by_node.items(), key=lambda x: -x[1])[:15]:
        print(f"  {node:35s}: {count:5d}")

    # 打印详细样例
    print("\n【各类别错误样例】")
    print("-" * 80)
    printed_categories = set()
    for r in results:
        if r["error_category"] not in printed_categories:
            printed_categories.add(r["error_category"])
            print(f"\n[{r['error_code']}] {r['error_category']}")
            print(f"  节点: {r['node_name']}")
            print(f"  原始类型: {r['original_type']}")
            print(f"  原始消息: {r['original_message'][:80]}...")
            print(f"  分类消息: {r['classified_message'][:80]}...")


def main():
    # 日志文件路径
    log_path = Path(__file__).parent.parent.parent.parent.parent.parent.parent / "err_log.txt"

    if not log_path.exists():
        # 尝试其他路径
        log_path = Path("/Users/zsq/PycharmProjects/coze-coding/err_log.txt")

    if not log_path.exists():
        print(f"错误: 找不到日志文件 {log_path}")
        return 1

    print(f"正在分析日志文件: {log_path}")
    print(f"文件大小: {log_path.stat().st_size / 1024 / 1024:.2f} MB")

    # 解析日志
    print("\n正在解析日志文件...")
    errors = parse_log_file(str(log_path))
    print(f"共提取到 {len(errors)} 个错误")

    if not errors:
        print("未找到任何错误记录")
        return 0

    # 分析错误
    print("正在分类错误...")
    results = analyze_errors(errors)

    # 打印统计
    print_statistics(results)

    return 0


if __name__ == "__main__":
    sys.exit(main())
