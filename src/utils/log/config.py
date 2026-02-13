"""
Application configuration
"""
import os
from pathlib import Path

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# 根据操作系统选择合适的日志目录
if os.name == 'nt':  # Windows
    LOG_DIR = Path(os.getenv("COZE_LOG_DIR", "logs/bypass"))
else:  # Linux/Unix
    LOG_DIR = Path(os.getenv("COZE_LOG_DIR", "/tmp/app/work/logs/bypass"))
