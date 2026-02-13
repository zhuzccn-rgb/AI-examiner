"""
错误码定义

6位错误码体系:
- 第1位: 错误大类 (1-9)
- 第2-3位: 错误子类 (01-99)
- 第4-6位: 具体错误 (001-999)
"""

from enum import IntEnum
from typing import Dict


class ErrorCategory(IntEnum):
    """错误大类"""
    CODE_ERROR = 1        # 代码语法/类型错误
    VALIDATION_ERROR = 2  # 输入验证错误
    API_ERROR = 3         # 外部API错误
    RESOURCE_ERROR = 4    # 资源/文件错误
    INTEGRATION_ERROR = 5 # 集成服务错误
    BUSINESS_ERROR = 6    # 业务逻辑错误
    RUNTIME_ERROR = 7     # 运行时错误
    CONFIG_ERROR = 8      # 配置错误
    UNKNOWN_ERROR = 9     # 未知错误


class ErrorCode(IntEnum):
    """
    错误码枚举

    命名规则: {大类}_{子类}_{具体错误}
    """

    # ==================== 1xxxxx 代码语法/类型错误 ====================
    # 101xxx - AttributeError 属性错误
    CODE_ATTR_NOT_FOUND = 101001          # 属性不存在
    CODE_ATTR_METHOD_NOT_FOUND = 101002   # 方法不存在
    CODE_ATTR_MODEL_DUMP = 101003         # model_dump属性错误 (常见于Pydantic对象误用)
    CODE_ATTR_WRONG_TYPE = 101004         # 对象类型错误导致属性不存在

    # 102xxx - TypeError 类型错误
    CODE_TYPE_MISSING_ARG = 102001        # 缺少必需的位置参数
    CODE_TYPE_EXTRA_ARG = 102002          # 传入了多余的参数
    CODE_TYPE_WRONG_ARG = 102003          # 参数类型错误
    CODE_TYPE_NOT_CALLABLE = 102004       # 对象不可调用
    CODE_TYPE_NOT_ITERABLE = 102005       # 对象不可迭代
    CODE_TYPE_NOT_SUBSCRIPTABLE = 102006  # 对象不可下标访问

    # 103xxx - NameError 名称错误
    CODE_NAME_NOT_DEFINED = 103001        # 名称未定义
    CODE_NAME_IMPORT_ERROR = 103002       # 导入错误

    # 104xxx - SyntaxError 语法错误
    CODE_SYNTAX_INVALID = 104001          # 无效语法
    CODE_SYNTAX_INDENTATION = 104002      # 缩进错误
    CODE_SYNTAX_REGEX_ESCAPE = 104003     # 正则表达式转义错误

    # 105xxx - IndexError/KeyError 索引/键错误
    CODE_INDEX_OUT_OF_RANGE = 105001      # 索引越界
    CODE_KEY_NOT_FOUND = 105002           # 键不存在

    # ==================== 2xxxxx 输入验证错误 ====================
    # 201xxx - Pydantic ValidationError
    VALIDATION_FIELD_REQUIRED = 201001    # 必填字段缺失
    VALIDATION_FIELD_TYPE = 201002        # 字段类型错误
    VALIDATION_FIELD_VALUE = 201003       # 字段值不合法
    VALIDATION_FIELD_FORMAT = 201004      # 字段格式错误 (如日期格式)
    VALIDATION_FIELD_CONSTRAINT = 201005  # 字段约束不满足 (如长度、范围)

    # 202xxx - 自定义验证错误
    VALIDATION_INPUT_EMPTY = 202001       # 输入为空
    VALIDATION_INPUT_INVALID = 202002     # 输入无效
    VALIDATION_JSON_DECODE = 202003       # JSON解析错误
    VALIDATION_PYDANTIC_SCHEMA = 202004   # Pydantic Schema生成失败

    # ==================== 3xxxxx 外部API错误 ====================
    # 301xxx - LLM API错误 (OpenAI/火山方舟等)
    API_LLM_REQUEST_FAILED = 301001       # LLM请求失败
    API_LLM_RATE_LIMIT = 301002           # LLM速率限制
    API_LLM_TOKEN_LIMIT = 301003          # Token超限
    API_LLM_INVALID_REQUEST = 301004      # 无效请求
    API_LLM_AUTH_FAILED = 301005          # 认证失败
    API_LLM_MODEL_NOT_FOUND = 301006      # 模型不存在
    API_LLM_CONTENT_FILTER = 301007       # 内容过滤
    API_LLM_IMAGE_FORMAT = 301008         # 图片格式不支持
    API_LLM_VIDEO_FORMAT = 301009         # 视频格式不支持

    # 302xxx - 图片生成API错误
    API_IMAGE_GEN_FAILED = 302001         # 图片生成失败
    API_IMAGE_GEN_TIMEOUT = 302002        # 图片生成超时
    API_IMAGE_GEN_QUOTA = 302003          # 配额不足

    # 303xxx - 视频生成API错误
    API_VIDEO_GEN_FAILED = 303001         # 视频生成失败
    API_VIDEO_GEN_TIMEOUT = 303002        # 视频生成超时
    API_VIDEO_GEN_NOT_FOUND = 303003      # 视频生成端点404

    # 304xxx - 语音API错误
    API_AUDIO_GEN_FAILED = 304001         # 语音生成失败
    API_AUDIO_TRANSCRIBE_FAILED = 304002  # 语音转写失败

    # 305xxx - 网络请求错误
    API_NETWORK_TIMEOUT = 305001          # 网络超时
    API_NETWORK_CONNECTION = 305002       # 连接错误
    API_NETWORK_HTTP_ERROR = 305003       # HTTP错误
    API_NETWORK_URL_INVALID = 305004      # URL无效 (MissingSchema等)
    API_NETWORK_SSL_ERROR = 305005        # SSL错误
    API_NETWORK_BROKEN_PIPE = 305006      # 管道断开
    API_NETWORK_REMOTE_PROTOCOL = 305007  # 远程协议错误

    # ==================== 4xxxxx 资源/文件错误 ====================
    # 401xxx - 文件操作错误
    RESOURCE_FILE_NOT_FOUND = 401001      # 文件不存在
    RESOURCE_FILE_READ_ERROR = 401002     # 文件读取错误
    RESOURCE_FILE_WRITE_ERROR = 401003    # 文件写入错误
    RESOURCE_FILE_FORMAT_ERROR = 401004   # 文件格式错误
    RESOURCE_FILE_TOO_LARGE = 401005      # 文件过大

    # 402xxx - 存储服务错误
    RESOURCE_S3_UPLOAD_FAILED = 402001    # S3上传失败
    RESOURCE_S3_DOWNLOAD_FAILED = 402002  # S3下载失败
    RESOURCE_S3_URL_FAILED = 402003       # S3 URL生成失败

    # 403xxx - 媒体处理错误
    RESOURCE_IMAGE_PROCESS_FAILED = 403001  # 图片处理失败
    RESOURCE_VIDEO_PROCESS_FAILED = 403002  # 视频处理失败
    RESOURCE_AUDIO_PROCESS_FAILED = 403003  # 音频处理失败
    RESOURCE_FACE_NOT_DETECTED = 403004     # 未检测到人脸
    RESOURCE_VIDEO_SEGMENT_FAILED = 403005  # 视频片段生成失败
    RESOURCE_FFMPEG_FAILED = 403006         # FFmpeg处理失败
    RESOURCE_IMAGE_DOWNLOAD_FAILED = 403007 # 图片下载失败
    RESOURCE_VIDEO_DOWNLOAD_FAILED = 403008 # 视频下载失败

    # ==================== 5xxxxx 集成服务错误 ====================
    # 501xxx - 飞书集成错误
    INTEGRATION_FEISHU_AUTH_FAILED = 501001  # 飞书认证失败
    INTEGRATION_FEISHU_API_FAILED = 501002   # 飞书API调用失败
    INTEGRATION_FEISHU_DOC_FAILED = 501003   # 飞书文档操作失败

    # 502xxx - 微信集成错误
    INTEGRATION_WECHAT_AUTH_FAILED = 502001  # 微信认证失败
    INTEGRATION_WECHAT_API_FAILED = 502002   # 微信API调用失败

    # 503xxx - 数据库错误
    INTEGRATION_DB_CONNECTION = 503001       # 数据库连接错误
    INTEGRATION_DB_QUERY = 503002            # 数据库查询错误
    INTEGRATION_DB_ADMIN_SHUTDOWN = 503003   # 数据库管理员关闭连接
    INTEGRATION_DB_SSL_CLOSED = 503004       # 数据库SSL连接关闭
    INTEGRATION_DB_POOL_TIMEOUT = 503005     # 数据库连接池超时

    # 504xxx - 其他集成错误
    INTEGRATION_SERVICE_UNAVAILABLE = 504001 # 集成服务不可用
    INTEGRATION_CREDENTIAL_INVALID = 504002  # 集成凭证无效
    INTEGRATION_CREDENTIAL_EXPIRED = 504003  # 集成凭证过期

    # ==================== 6xxxxx 业务逻辑错误 ====================
    # 601xxx - 工作流错误
    BUSINESS_NODE_NOT_FOUND = 601001      # 节点不存在
    BUSINESS_NODE_FAILED = 601002         # 节点执行失败
    BUSINESS_GRAPH_INVALID = 601003       # 图结构无效

    # 602xxx - 数据处理错误
    BUSINESS_DATA_INVALID = 602001        # 数据无效
    BUSINESS_DATA_NOT_FOUND = 602002      # 数据不存在
    BUSINESS_DATA_DUPLICATE = 602003      # 数据重复

    # 603xxx - 业务规则错误
    BUSINESS_RULE_VIOLATED = 603001       # 业务规则违反
    BUSINESS_LIMIT_EXCEEDED = 603002      # 超出限制

    # 604xxx - 资源点/配额/权益错误 (BENEFIT_ERROR)
    BUSINESS_QUOTA_INSUFFICIENT = 604001  # 资源点不足
    BUSINESS_QUOTA_EXCEEDED = 604002      # 配额超限
    BUSINESS_BALANCE_OVERDUE = 604003     # 余额欠费

    # ==================== 7xxxxx 运行时错误 ====================
    # 701xxx - 执行错误
    RUNTIME_EXECUTION_FAILED = 701001     # 执行失败
    RUNTIME_TIMEOUT = 701002              # 执行超时
    RUNTIME_CANCELLED = 701003            # 执行被取消

    # 702xxx - 内存/资源错误
    RUNTIME_MEMORY_ERROR = 702001         # 内存错误
    RUNTIME_RECURSION_LIMIT = 702002      # 递归深度超限

    # 703xxx - 异步错误
    RUNTIME_ASYNC_NOT_IMPL = 703001       # 异步方法未实现
    RUNTIME_ASYNC_CANCELLED = 703002      # 异步任务取消

    # 704xxx - 进程/线程错误
    RUNTIME_SUBPROCESS_TIMEOUT = 704001   # 子进程超时
    RUNTIME_SUBPROCESS_FAILED = 704002    # 子进程执行失败
    RUNTIME_THREAD_ERROR = 704003         # 线程错误 (如greenlet错误)

    # ==================== 8xxxxx 配置错误 ====================
    # 801xxx - API Key配置错误
    CONFIG_API_KEY_MISSING = 801001       # API Key缺失
    CONFIG_API_KEY_INVALID = 801002       # API Key无效

    # 802xxx - 环境配置错误
    CONFIG_ENV_MISSING = 802001           # 环境变量缺失
    CONFIG_ENV_INVALID = 802002           # 环境变量无效
    CONFIG_TTS_MISSING = 802003           # TTS配置缺失

    # 803xxx - 浏览器配置错误
    CONFIG_BROWSER_NOT_FOUND = 803001     # 浏览器可执行文件不存在
    CONFIG_WEBDRIVER_FAILED = 803002      # WebDriver启动失败

    # ==================== 9xxxxx 未知错误 ====================
    UNKNOWN_ERROR = 900001                # 未知错误
    UNKNOWN_EXCEPTION = 900002            # 未知异常


# 错误码描述映射
ERROR_DESCRIPTIONS: Dict[int, str] = {
    # 1xxxxx 代码错误
    ErrorCode.CODE_ATTR_NOT_FOUND: "属性不存在",
    ErrorCode.CODE_ATTR_METHOD_NOT_FOUND: "方法不存在",
    ErrorCode.CODE_ATTR_MODEL_DUMP: "对象类型错误，尝试访问model_dump属性",
    ErrorCode.CODE_ATTR_WRONG_TYPE: "对象类型错误导致属性访问失败",
    ErrorCode.CODE_TYPE_MISSING_ARG: "函数调用缺少必需的参数",
    ErrorCode.CODE_TYPE_EXTRA_ARG: "函数调用传入了多余的参数",
    ErrorCode.CODE_TYPE_WRONG_ARG: "函数参数类型错误",
    ErrorCode.CODE_TYPE_NOT_CALLABLE: "对象不可调用",
    ErrorCode.CODE_TYPE_NOT_ITERABLE: "对象不可迭代",
    ErrorCode.CODE_TYPE_NOT_SUBSCRIPTABLE: "对象不支持下标访问",
    ErrorCode.CODE_NAME_NOT_DEFINED: "变量或函数名未定义",
    ErrorCode.CODE_NAME_IMPORT_ERROR: "模块导入错误",
    ErrorCode.CODE_SYNTAX_INVALID: "语法错误",
    ErrorCode.CODE_SYNTAX_INDENTATION: "缩进错误",
    ErrorCode.CODE_SYNTAX_REGEX_ESCAPE: "正则表达式转义错误",
    ErrorCode.CODE_INDEX_OUT_OF_RANGE: "索引越界",
    ErrorCode.CODE_KEY_NOT_FOUND: "字典键不存在",

    # 2xxxxx 验证错误
    ErrorCode.VALIDATION_FIELD_REQUIRED: "必填字段缺失",
    ErrorCode.VALIDATION_FIELD_TYPE: "字段类型错误",
    ErrorCode.VALIDATION_FIELD_VALUE: "字段值不合法",
    ErrorCode.VALIDATION_FIELD_FORMAT: "字段格式错误",
    ErrorCode.VALIDATION_FIELD_CONSTRAINT: "字段约束不满足",
    ErrorCode.VALIDATION_INPUT_EMPTY: "输入为空",
    ErrorCode.VALIDATION_INPUT_INVALID: "输入无效",
    ErrorCode.VALIDATION_JSON_DECODE: "JSON解析错误",
    ErrorCode.VALIDATION_PYDANTIC_SCHEMA: "Pydantic Schema生成失败",

    # 3xxxxx API错误
    ErrorCode.API_LLM_REQUEST_FAILED: "LLM请求失败",
    ErrorCode.API_LLM_RATE_LIMIT: "LLM请求频率超限",
    ErrorCode.API_LLM_TOKEN_LIMIT: "Token数量超限",
    ErrorCode.API_LLM_INVALID_REQUEST: "LLM请求参数无效",
    ErrorCode.API_LLM_AUTH_FAILED: "LLM认证失败",
    ErrorCode.API_LLM_MODEL_NOT_FOUND: "LLM模型不存在",
    ErrorCode.API_LLM_CONTENT_FILTER: "内容被安全过滤",
    ErrorCode.API_LLM_IMAGE_FORMAT: "图片格式不支持",
    ErrorCode.API_LLM_VIDEO_FORMAT: "视频格式不支持",
    ErrorCode.API_IMAGE_GEN_FAILED: "图片生成失败",
    ErrorCode.API_IMAGE_GEN_TIMEOUT: "图片生成超时",
    ErrorCode.API_IMAGE_GEN_QUOTA: "图片生成配额不足",
    ErrorCode.API_VIDEO_GEN_FAILED: "视频生成失败",
    ErrorCode.API_VIDEO_GEN_TIMEOUT: "视频生成超时",
    ErrorCode.API_VIDEO_GEN_NOT_FOUND: "视频生成服务不可用",
    ErrorCode.API_AUDIO_GEN_FAILED: "语音生成失败",
    ErrorCode.API_AUDIO_TRANSCRIBE_FAILED: "语音转写失败",
    ErrorCode.API_NETWORK_TIMEOUT: "网络请求超时",
    ErrorCode.API_NETWORK_CONNECTION: "网络连接失败",
    ErrorCode.API_NETWORK_HTTP_ERROR: "HTTP请求错误",
    ErrorCode.API_NETWORK_URL_INVALID: "URL格式无效",
    ErrorCode.API_NETWORK_SSL_ERROR: "SSL证书错误",
    ErrorCode.API_NETWORK_BROKEN_PIPE: "网络管道断开",
    ErrorCode.API_NETWORK_REMOTE_PROTOCOL: "远程协议错误",

    # 4xxxxx 资源错误
    ErrorCode.RESOURCE_FILE_NOT_FOUND: "文件不存在",
    ErrorCode.RESOURCE_FILE_READ_ERROR: "文件读取失败",
    ErrorCode.RESOURCE_FILE_WRITE_ERROR: "文件写入失败",
    ErrorCode.RESOURCE_FILE_FORMAT_ERROR: "文件格式错误",
    ErrorCode.RESOURCE_FILE_TOO_LARGE: "文件过大",
    ErrorCode.RESOURCE_S3_UPLOAD_FAILED: "文件上传失败",
    ErrorCode.RESOURCE_S3_DOWNLOAD_FAILED: "文件下载失败",
    ErrorCode.RESOURCE_S3_URL_FAILED: "文件URL生成失败",
    ErrorCode.RESOURCE_IMAGE_PROCESS_FAILED: "图片处理失败",
    ErrorCode.RESOURCE_VIDEO_PROCESS_FAILED: "视频处理失败",
    ErrorCode.RESOURCE_AUDIO_PROCESS_FAILED: "音频处理失败",
    ErrorCode.RESOURCE_FACE_NOT_DETECTED: "未检测到人脸",
    ErrorCode.RESOURCE_VIDEO_SEGMENT_FAILED: "视频片段生成失败",
    ErrorCode.RESOURCE_FFMPEG_FAILED: "FFmpeg处理失败",
    ErrorCode.RESOURCE_IMAGE_DOWNLOAD_FAILED: "图片下载失败",
    ErrorCode.RESOURCE_VIDEO_DOWNLOAD_FAILED: "视频下载失败",

    # 5xxxxx 集成错误
    ErrorCode.INTEGRATION_FEISHU_AUTH_FAILED: "飞书认证失败",
    ErrorCode.INTEGRATION_FEISHU_API_FAILED: "飞书API调用失败",
    ErrorCode.INTEGRATION_FEISHU_DOC_FAILED: "飞书文档操作失败",
    ErrorCode.INTEGRATION_WECHAT_AUTH_FAILED: "微信认证失败",
    ErrorCode.INTEGRATION_WECHAT_API_FAILED: "微信API调用失败",
    ErrorCode.INTEGRATION_DB_CONNECTION: "数据库连接失败",
    ErrorCode.INTEGRATION_DB_QUERY: "数据库查询失败",
    ErrorCode.INTEGRATION_DB_ADMIN_SHUTDOWN: "数据库连接被管理员关闭",
    ErrorCode.INTEGRATION_DB_SSL_CLOSED: "数据库SSL连接意外关闭",
    ErrorCode.INTEGRATION_DB_POOL_TIMEOUT: "数据库连接池超时",
    ErrorCode.INTEGRATION_SERVICE_UNAVAILABLE: "集成服务不可用",
    ErrorCode.INTEGRATION_CREDENTIAL_INVALID: "集成凭证无效",
    ErrorCode.INTEGRATION_CREDENTIAL_EXPIRED: "集成凭证过期",

    # 6xxxxx 业务错误
    ErrorCode.BUSINESS_NODE_NOT_FOUND: "工作流节点不存在",
    ErrorCode.BUSINESS_NODE_FAILED: "工作流节点执行失败",
    ErrorCode.BUSINESS_GRAPH_INVALID: "工作流图结构无效",
    ErrorCode.BUSINESS_DATA_INVALID: "数据无效",
    ErrorCode.BUSINESS_DATA_NOT_FOUND: "数据不存在",
    ErrorCode.BUSINESS_DATA_DUPLICATE: "数据重复",
    ErrorCode.BUSINESS_RULE_VIOLATED: "业务规则违反",
    ErrorCode.BUSINESS_LIMIT_EXCEEDED: "超出限制",
    ErrorCode.BUSINESS_QUOTA_INSUFFICIENT: "资源点不足，请升级为付费版套餐",
    ErrorCode.BUSINESS_QUOTA_EXCEEDED: "配额超限",
    ErrorCode.BUSINESS_BALANCE_OVERDUE: "余额欠费",

    # 7xxxxx 运行时错误
    ErrorCode.RUNTIME_EXECUTION_FAILED: "执行失败",
    ErrorCode.RUNTIME_TIMEOUT: "执行超时",
    ErrorCode.RUNTIME_CANCELLED: "执行被取消",
    ErrorCode.RUNTIME_MEMORY_ERROR: "内存错误",
    ErrorCode.RUNTIME_RECURSION_LIMIT: "递归深度超限",
    ErrorCode.RUNTIME_ASYNC_NOT_IMPL: "异步方法未实现",
    ErrorCode.RUNTIME_ASYNC_CANCELLED: "异步任务取消",
    ErrorCode.RUNTIME_SUBPROCESS_TIMEOUT: "子进程执行超时",
    ErrorCode.RUNTIME_SUBPROCESS_FAILED: "子进程执行失败",
    ErrorCode.RUNTIME_THREAD_ERROR: "线程切换错误",

    # 8xxxxx 配置错误
    ErrorCode.CONFIG_API_KEY_MISSING: "API Key未配置",
    ErrorCode.CONFIG_API_KEY_INVALID: "API Key无效",
    ErrorCode.CONFIG_ENV_MISSING: "环境变量未配置",
    ErrorCode.CONFIG_ENV_INVALID: "环境变量无效",
    ErrorCode.CONFIG_TTS_MISSING: "TTS配置缺失",
    ErrorCode.CONFIG_BROWSER_NOT_FOUND: "浏览器可执行文件不存在",
    ErrorCode.CONFIG_WEBDRIVER_FAILED: "WebDriver启动失败",

    # 9xxxxx 未知错误
    ErrorCode.UNKNOWN_ERROR: "未知错误",
    ErrorCode.UNKNOWN_EXCEPTION: "未知异常",
}


def get_error_description(code: int) -> str:
    """获取错误码描述"""
    return ERROR_DESCRIPTIONS.get(code, f"未知错误码: {code}")


def get_error_category(code: int) -> ErrorCategory:
    """根据错误码获取错误大类"""
    category = code // 100000
    try:
        return ErrorCategory(category)
    except ValueError:
        return ErrorCategory.UNKNOWN_ERROR
