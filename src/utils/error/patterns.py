"""
错误模式匹配表

统一管理所有错误关键词到错误码的映射，避免在多个函数中重复定义匹配逻辑。
"""

from typing import List, Tuple, Optional
from .codes import ErrorCode


ErrorPattern = Tuple[List[str], int, str]

ERROR_PATTERNS: List[ErrorPattern] = [
    # ==================== 最高优先级模式 (防止误分类) ====================
    # 视频生成任务创建失败 - 优先于下载失败
    (['视频生成任务创建失败', '404 client error'],
     ErrorCode.API_VIDEO_GEN_NOT_FOUND, "视频生成端点404"),
    (['视频生成任务创建失败', '401 client error'],
     ErrorCode.API_LLM_AUTH_FAILED, "视频生成认证失败"),
    (['视频生成任务创建失败'],
     ErrorCode.API_VIDEO_GEN_FAILED, "视频生成任务创建失败"),
    
    # 飞书API错误 - 优先于下载失败
    (['飞书api错误', 'fieldnamenotfound'],
     ErrorCode.INTEGRATION_FEISHU_API_FAILED, "飞书字段不存在"),
    (['同步到飞书失败', '飞书api错误'],
     ErrorCode.INTEGRATION_FEISHU_API_FAILED, "飞书同步失败"),
    
    # model not found - 优先于通用 API 错误
    (['not found model', 'model not found'],
     ErrorCode.API_LLM_MODEL_NOT_FOUND, "模型未找到"),
    
    # InvalidUpdateError - 优先于业务节点失败
    (['invalidupdateerror', 'expected dict'],
     ErrorCode.CODE_TYPE_WRONG_ARG, "节点返回类型错误"),
    (['invalidupdateerror', 'can receive only one value'],
     ErrorCode.CODE_TYPE_WRONG_ARG, "节点返回值冲突"),

    # ==================== 代码执行超时 (高优先级) ====================
    (['代码执行超时'],
     ErrorCode.RUNTIME_TIMEOUT, "代码执行超时"),
    (['execution timeout', 'exceeded 900 seconds'],
     ErrorCode.RUNTIME_TIMEOUT, "执行超时"),
    (['代码服务器协议错误', '服务可能在处理请求时崩溃'],
     ErrorCode.API_NETWORK_REMOTE_PROTOCOL, "代码服务器协议错误"),

    # ==================== 模块导入错误 (高优先级) ====================
    (['no module named'],
     ErrorCode.CODE_NAME_IMPORT_ERROR, "模块未找到"),
    (['cannot import name'],
     ErrorCode.CODE_NAME_IMPORT_ERROR, "无法导入名称"),
    (['is not installed', 'pip install'],
     ErrorCode.CONFIG_ENV_MISSING, "依赖库未安装"),

    # ==================== JSON/语法错误 (高优先级) ====================
    (['invalid control character'],
     ErrorCode.VALIDATION_JSON_DECODE, "JSON包含非法控制字符"),
    (["expecting ',' delimiter", "expecting ','"],
     ErrorCode.VALIDATION_JSON_DECODE, "JSON格式错误"),
    (['positional argument follows keyword argument'],
     ErrorCode.CODE_SYNTAX_INVALID, "语法错误：位置参数在关键字参数之后"),
    (['parameter without a default follows parameter with a default'],
     ErrorCode.CODE_SYNTAX_INVALID, "语法错误：无默认值参数在有默认值参数之后"),

    # ==================== LLM 特定错误 (高优先级) ====================
    (['unsupported thinking type'],
     ErrorCode.API_LLM_INVALID_REQUEST, "不支持的思考模式"),
    (['invalid tool_call_id', 'no matching tool call'],
     ErrorCode.API_LLM_INVALID_REQUEST, "无效的工具调用ID"),
    (['apiconnectionerror', 'connection error'],
     ErrorCode.API_NETWORK_CONNECTION, "API连接错误"),
    (['api_key client option must be set', 'api_key is required'],
     ErrorCode.CONFIG_API_KEY_MISSING, "API Key未配置"),

    # ==================== 语法/缩进错误 (高优先级) ====================
    (['unexpected indent', 'indentationerror'],
     ErrorCode.CODE_SYNTAX_INDENTATION, "缩进错误"),
    (['unterminated string literal', 'unterminated triple-quoted'],
     ErrorCode.CODE_SYNTAX_INVALID, "字符串未终止"),
    (['syntaxerror:', 'invalid syntax'],
     ErrorCode.CODE_SYNTAX_INVALID, "语法错误"),
    (['relative import beyond top-level', 'attempted relative import'],
     ErrorCode.CODE_NAME_IMPORT_ERROR, "相对导入错误"),

    # ==================== 环境/配置错误 (高优先级) ====================
    (['display', 'no display name'],
     ErrorCode.CONFIG_ENV_MISSING, "DISPLAY环境变量未设置"),
    (['portaudio library not found', 'portaudio'],
     ErrorCode.CONFIG_ENV_MISSING, "PortAudio库未安装"),
    (['功能未实现'],
     ErrorCode.RUNTIME_ASYNC_NOT_IMPL, "功能未实现"),
    (['poppler', 'is poppler installed'],
     ErrorCode.CONFIG_ENV_MISSING, "Poppler未安装"),
    (['paddleocr', 'ocr模型未初始化'],
     ErrorCode.CONFIG_ENV_MISSING, "PaddleOCR未初始化"),

    # ==================== LangGraph 错误 (高优先级) ====================
    (['invalid_graph_node', 'unknown node'],
     ErrorCode.BUSINESS_GRAPH_INVALID, "LangGraph节点无效"),
    (['invalid_concurrent', 'langgraph/errors'],
     ErrorCode.BUSINESS_GRAPH_INVALID, "LangGraph并发错误"),
    (['edge starting at unknown node', 'unknown target'],
     ErrorCode.BUSINESS_GRAPH_INVALID, "LangGraph边定义错误"),

    # ==================== 业务数据错误 (高优先级) ====================
    (['应用启动失败', '未捕获到具体错误'],
     ErrorCode.RUNTIME_EXECUTION_FAILED, "应用启动失败"),
    (['请求失败:'],
     ErrorCode.API_NETWORK_HTTP_ERROR, "请求失败"),
    (['size of the input image', 'exceeds the limit'],
     ErrorCode.RESOURCE_FILE_TOO_LARGE, "图片大小超限"),
    (['headobject operation', 'not found'],
     ErrorCode.RESOURCE_S3_DOWNLOAD_FAILED, "S3对象不存在"),

    # ==================== OCR/文档处理错误 ====================
    (['ocr识别失败', '无法从响应中提取有效的json'],
     ErrorCode.RESOURCE_FILE_FORMAT_ERROR, "OCR识别失败"),
    (['文件读取失败', '找不到文件'],
     ErrorCode.RESOURCE_FILE_NOT_FOUND, "文件读取失败"),
    (['excel file format cannot be determined', 'specify an engine'],
     ErrorCode.RESOURCE_FILE_FORMAT_ERROR, "Excel格式无法识别"),
    (['file contains no valid workbook', 'workbook part'],
     ErrorCode.RESOURCE_FILE_FORMAT_ERROR, "Excel文件无效"),
    (['pdf内容提取失败', 'pdf读取失败'],
     ErrorCode.RESOURCE_FILE_FORMAT_ERROR, "PDF读取失败"),
    (['txt转csv失败', '没有生成有效数据'],
     ErrorCode.RESOURCE_FILE_FORMAT_ERROR, "TXT转换失败"),
    (['无法读取图片', '尝试修复文件失败'],
     ErrorCode.RESOURCE_IMAGE_PROCESS_FAILED, "图片读取失败"),
    (['未能提取到有效的数值数据', '识别图片表格失败'],
     ErrorCode.RESOURCE_FILE_FORMAT_ERROR, "数据提取失败"),

    # ==================== 邮件/网络服务错误 ====================
    (['邮箱连接失败', 'gaierror', 'name or service not known'],
     ErrorCode.API_NETWORK_CONNECTION, "邮箱连接失败"),
    (['wl-paste', 'xclip', '剪贴板'],
     ErrorCode.CONFIG_ENV_MISSING, "剪贴板工具缺失"),
    (['无头环境', '没有图形界面', '无法访问剪贴板'],
     ErrorCode.CONFIG_ENV_MISSING, "无图形界面环境"),

    # ==================== 视频/音频生成错误 ====================
    (['火山方舟api认证失败', '图片生成视频失败'],
     ErrorCode.API_LLM_AUTH_FAILED, "火山方舟认证失败"),
    (['视频生成服务端点不可用', '404错误'],
     ErrorCode.API_VIDEO_GEN_NOT_FOUND, "视频生成端点404"),
    (['没有音频可以合成视频', '标题和正文内容为空'],
     ErrorCode.VALIDATION_INPUT_EMPTY, "音频内容为空"),
    (['no images generated', 'cannot create video'],
     ErrorCode.RESOURCE_VIDEO_SEGMENT_FAILED, "无图片生成视频"),
    (['没有成功生成临时视频文件', '没有成功生成任何视频片段'],
     ErrorCode.RESOURCE_VIDEO_SEGMENT_FAILED, "视频片段生成失败"),
    (['生成的文案包含违规词', '平台规则'],
     ErrorCode.API_LLM_CONTENT_FILTER, "内容违规"),
    (['期望生成.*张图片', '实际生成'],
     ErrorCode.RESOURCE_IMAGE_PROCESS_FAILED, "图片生成数量不足"),
    (['没有可用的图片url', '图片生成节点'],
     ErrorCode.RESOURCE_IMAGE_PROCESS_FAILED, "图片URL缺失"),

    # ==================== API 错误补充 ====================
    (['openai.notfounderror', 'error code: 404'],
     ErrorCode.API_LLM_MODEL_NOT_FOUND, "OpenAI资源未找到"),
    (['openai.internalservererror', 'error code: 500'],
     ErrorCode.API_LLM_REQUEST_FAILED, "OpenAI服务器错误"),
    (['botocore.exceptions', 'invalidargument', 'putobject'],
     ErrorCode.RESOURCE_S3_UPLOAD_FAILED, "S3上传参数无效"),
    (['表格不存在或访问权限不足'],
     ErrorCode.INTEGRATION_CREDENTIAL_INVALID, "表格访问权限不足"),
    (['invalid appid', 'access_token 失败'],
     ErrorCode.INTEGRATION_CREDENTIAL_INVALID, "AppID无效"),

    # ==================== 编码错误 (高优先级) ====================
    (["codec can't encode", 'surrogates not allowed'],
     ErrorCode.RESOURCE_FILE_FORMAT_ERROR, "字符编码错误"),
    (['xml compatible', 'null bytes or control characters'],
     ErrorCode.RESOURCE_FILE_FORMAT_ERROR, "XML兼容性错误"),

    # ==================== 类型错误补充 ====================
    (['has no len()'],
     ErrorCode.CODE_TYPE_WRONG_ARG, "对象不支持len操作"),
    (['list index out of range'],
     ErrorCode.CODE_INDEX_OUT_OF_RANGE, "列表索引越界"),
    (["invalid literal for int()", "with base 10"],
     ErrorCode.VALIDATION_FIELD_TYPE, "整数解析错误"),

    # ==================== HTTP 请求错误 ====================
    (['执行请求时发生未知错误', '404:', 'error from'],
     ErrorCode.API_NETWORK_HTTP_ERROR, "HTTP请求错误"),
    (['执行请求时发生未知错误', '401:'],
     ErrorCode.API_LLM_AUTH_FAILED, "认证失败"),

    # ==================== URL/文件名验证错误 ====================
    (['no scheme supplied', "invalid url ''"],
     ErrorCode.API_NETWORK_URL_INVALID, "URL格式无效"),
    (['file name invalid', 's3 对象命名规范'],
     ErrorCode.VALIDATION_INPUT_INVALID, "文件名格式无效"),

    # ==================== 图片格式错误 ====================
    (['image format is not supported'],
     ErrorCode.API_LLM_IMAGE_FORMAT, "图片格式不支持"),

    # ==================== 视频/图片处理错误 (需要精确匹配) ====================
    (['视频处理失败', '视频解析失败', '视频转换失败'],
     ErrorCode.RESOURCE_VIDEO_PROCESS_FAILED, "视频处理错误"),
    (['图片处理失败', '图片解析失败', '图片转换失败'],
     ErrorCode.RESOURCE_IMAGE_PROCESS_FAILED, "图片处理错误"),
    (['invalid image', 'image is invalid', 'cannot identify image'],
     ErrorCode.RESOURCE_IMAGE_PROCESS_FAILED, "图片格式无效"),
    (['video codec', 'video format', 'unsupported video'],
     ErrorCode.RESOURCE_VIDEO_PROCESS_FAILED, "视频格式错误"),
    (['图片生成节点错误', '图片生成失败'],
     ErrorCode.API_IMAGE_GEN_FAILED, "图片生成失败"),
    (['加载图像失败', '加载头部图像失败'],
     ErrorCode.RESOURCE_IMAGE_PROCESS_FAILED, "图像加载失败"),
    (['图像预处理失败', 'magic number'],
     ErrorCode.RESOURCE_FILE_FORMAT_ERROR, "图像格式无效"),

    # ==================== 音频处理错误 ====================
    (['语音识别失败', 'asr 识别失败', 'asr识别失败'],
     ErrorCode.API_AUDIO_TRANSCRIBE_FAILED, "语音识别失败"),
    (['音频生成失败', '所有分段均未成功生成'],
     ErrorCode.API_AUDIO_GEN_FAILED, "音频生成失败"),
    (['bgm添加失败', 'audio_bitrate'],
     ErrorCode.RESOURCE_AUDIO_PROCESS_FAILED, "BGM添加失败"),

    # ==================== 网络请求失败 (业务层) ====================
    (['网络请求失败', '400 client error'],
     ErrorCode.API_NETWORK_HTTP_ERROR, "HTTP 400错误"),
    (['网络请求失败', '404 client error'],
     ErrorCode.API_NETWORK_HTTP_ERROR, "HTTP 404错误"),
    (['http 错误', 'bad request'],
     ErrorCode.API_NETWORK_HTTP_ERROR, "HTTP请求错误"),
    (['http请求失败', '状态码'],
     ErrorCode.API_NETWORK_HTTP_ERROR, "HTTP请求失败"),

    # ==================== 业务节点失败细分 ====================
    (['expected dict, got', 'invalidupdateerror'],
     ErrorCode.CODE_TYPE_WRONG_ARG, "节点返回类型错误"),
    (['爬取.*失败', '爬取抖音'],
     ErrorCode.INTEGRATION_SERVICE_UNAVAILABLE, "爬虫服务失败"),
    (['获取邮件失败', 'login fail', 'account is abnormal'],
     ErrorCode.INTEGRATION_CREDENTIAL_INVALID, "邮件登录失败"),
    (['标题改写失败', 'expecting value'],
     ErrorCode.VALIDATION_JSON_DECODE, "JSON解析失败"),
    (['调用.*api.*失败', 'openrouter api'],
     ErrorCode.API_LLM_REQUEST_FAILED, "API调用失败"),
    (['获取股票数据失败', '数据为空'],
     ErrorCode.BUSINESS_DATA_NOT_FOUND, "数据获取失败"),
    (['failed to generate any frames', 'generate any frames'],
     ErrorCode.RESOURCE_VIDEO_SEGMENT_FAILED, "视频帧生成失败"),
    (['下载视频文件失败', 'file name too long'],
     ErrorCode.RESOURCE_FILE_FORMAT_ERROR, "文件名过长"),
    (['moviepy', 'imagesequenceclip', 'all images to have the same size'],
     ErrorCode.RESOURCE_VIDEO_PROCESS_FAILED, "MoviePy图像尺寸不一致"),
    (['service /root/.wdm', 'chromedriver'],
     ErrorCode.CONFIG_WEBDRIVER_FAILED, "ChromeDriver启动失败"),
    (['视频抽帧失败', 'http 403', '签名可能已过期'],
     ErrorCode.RESOURCE_VIDEO_PROCESS_FAILED, "视频抽帧失败"),
    (['所有视频生成端点都尝试失败', '所有视频生成任务均失败'],
     ErrorCode.API_VIDEO_GEN_FAILED, "视频生成端点失败"),
    (['上传pdf失败', 'unable to locate credentials'],
     ErrorCode.CONFIG_API_KEY_MISSING, "AWS凭证缺失"),
    (['生成pdf报告失败', 'stylesheet'],
     ErrorCode.RESOURCE_FILE_FORMAT_ERROR, "PDF样式错误"),
    (['从数据库查询', '失败'],
     ErrorCode.INTEGRATION_DB_QUERY, "数据库查询失败"),
    (['excel文件解析', '表格结构检测失败'],
     ErrorCode.RESOURCE_FILE_FORMAT_ERROR, "Excel解析失败"),
    (['文档生成失败'],
     ErrorCode.RESOURCE_FILE_FORMAT_ERROR, "文档生成失败"),
    (['读取.*对照表失败', '读取远程文件失败'],
     ErrorCode.RESOURCE_S3_DOWNLOAD_FAILED, "远程文件读取失败"),
    (['工资验证失败', '工资计算失败', '计算工资失败'],
     ErrorCode.BUSINESS_RULE_VIOLATED, "工资处理失败"),
    (['unsupported format string', 'undefined.__fo'],
     ErrorCode.CODE_TYPE_WRONG_ARG, "格式化字符串错误"),

    # ==================== 微信集成错误 ====================
    (['微信公众号', '凭证获取失败'],
     ErrorCode.INTEGRATION_WECHAT_API_FAILED, "微信公众号凭证获取失败"),

    # ==================== 视频生成任务错误 ====================
    (['视频生成任务创建失败'],
     ErrorCode.API_VIDEO_GEN_FAILED, "视频生成任务创建失败"),

    # ==================== 数据库相关错误 ====================
    (['adminshutdown', 'terminating connection due to administrator command'],
     ErrorCode.INTEGRATION_DB_ADMIN_SHUTDOWN, "数据库连接被管理员关闭"),
    (['ssl connection has been closed unexpectedly'],
     ErrorCode.INTEGRATION_DB_SSL_CLOSED, "数据库SSL连接意外关闭"),
    (['pooltimeout', "couldn't get a connection"],
     ErrorCode.INTEGRATION_DB_POOL_TIMEOUT, "数据库连接池超时"),
    (['the connection is closed'],
     ErrorCode.INTEGRATION_DB_CONNECTION, "数据库连接已关闭"),
    (['psycopg2', 'postgresql'],
     ErrorCode.INTEGRATION_DB_QUERY, "数据库错误"),

    # ==================== 网络相关错误 ====================
    (['broken pipe', 'errno 32'],
     ErrorCode.API_NETWORK_BROKEN_PIPE, "网络管道断开"),
    (['remoteprotocolerror'],
     ErrorCode.API_NETWORK_REMOTE_PROTOCOL, "远程协议错误"),
    (['error while downloading'],
     ErrorCode.RESOURCE_S3_DOWNLOAD_FAILED, "文件下载失败"),
    (['nosuchkey', 'specified key does not exist'],
     ErrorCode.RESOURCE_S3_DOWNLOAD_FAILED, "S3对象不存在"),
    (['max retries exceeded', 'connectionpool'],
     ErrorCode.API_NETWORK_CONNECTION, "网络连接失败"),
    (['server error', '500 internal server error'],
     ErrorCode.API_NETWORK_HTTP_ERROR, "服务器500错误"),

    # ==================== Pydantic/验证相关错误 ====================
    (['validation error for chatgenerationchunk', 'basemessagechunk'],
     ErrorCode.VALIDATION_FIELD_TYPE, "LangChain消息类型错误"),
    (['paragraph text', '<para>'],
     ErrorCode.RESOURCE_FILE_FORMAT_ERROR, "文档段落格式错误"),
    (['pydanticinvalidforjsonschema', 'cannot generate a jsonschema'],
     ErrorCode.VALIDATION_PYDANTIC_SCHEMA, "Pydantic JSON Schema生成失败"),
    (['unable to generate pydantic-core schema'],
     ErrorCode.VALIDATION_PYDANTIC_SCHEMA, "Pydantic Schema生成失败"),
    (['model-field-overridden'],
     ErrorCode.VALIDATION_PYDANTIC_SCHEMA, "Pydantic字段覆盖错误"),

    # ==================== 正则表达式错误 ====================
    (['bad escape'],
     ErrorCode.CODE_SYNTAX_REGEX_ESCAPE, "正则表达式转义错误"),

    # ==================== 浏览器/WebDriver 错误 ====================
    (['webdriverexception'],
     ErrorCode.CONFIG_WEBDRIVER_FAILED, "WebDriver启动失败"),
    (["executable doesn't exist", 'browsertype.launch'],
     ErrorCode.CONFIG_BROWSER_NOT_FOUND, "浏览器可执行文件不存在"),
    (['chrome failed to start'],
     ErrorCode.CONFIG_WEBDRIVER_FAILED, "Chrome启动失败"),
    (['unable to obtain driver'],
     ErrorCode.CONFIG_WEBDRIVER_FAILED, "无法获取WebDriver"),

    # ==================== 视频相关错误 ====================
    (['视频文件不存在'],
     ErrorCode.RESOURCE_FILE_NOT_FOUND, "视频文件不存在"),
    (['剪映草稿文件不存在'],
     ErrorCode.RESOURCE_FILE_NOT_FOUND, "剪映草稿文件不存在"),
    (['视频片段生成失败', '所有视频片段生成失败'],
     ErrorCode.RESOURCE_VIDEO_SEGMENT_FAILED, "视频片段生成失败"),
    (['没有生成任何视频片段', '未能成功生成任何视频片段', '没有可用的视频片段'],
     ErrorCode.RESOURCE_VIDEO_SEGMENT_FAILED, "无可用视频片段"),
    (['下载视频失败', '视频下载失败'],
     ErrorCode.RESOURCE_VIDEO_DOWNLOAD_FAILED, "视频下载失败"),
    (['视频预处理失败'],
     ErrorCode.RESOURCE_FFMPEG_FAILED, "视频预处理失败"),
    (['ffmpeg'],
     ErrorCode.RESOURCE_FFMPEG_FAILED, "FFmpeg处理失败"),

    # ==================== 图片相关错误 ====================
    (['无法下载图片', '下载图片失败'],
     ErrorCode.RESOURCE_IMAGE_DOWNLOAD_FAILED, "图片下载失败"),
    (['图片url列表为空'],
     ErrorCode.VALIDATION_INPUT_EMPTY, "图片URL列表为空"),
    (['所有图片都无法访问'],
     ErrorCode.RESOURCE_IMAGE_DOWNLOAD_FAILED, "图片无法访问"),
    (['输入的图片url无法访问'],
     ErrorCode.RESOURCE_IMAGE_DOWNLOAD_FAILED, "图片URL无法访问"),

    # ==================== TTS 相关错误 ====================
    (['腾讯云 tts', '腾讯云tts'],
     ErrorCode.API_AUDIO_GEN_FAILED, "腾讯云TTS生成失败"),

    # ==================== 飞书相关错误 ====================
    (['获取草稿列表失败'],
     ErrorCode.INTEGRATION_FEISHU_API_FAILED, "飞书获取草稿列表失败"),
    (['飞书api错误'],
     ErrorCode.INTEGRATION_FEISHU_API_FAILED, "飞书API错误"),
    (['feishu api', 'feishu error'],
     ErrorCode.INTEGRATION_FEISHU_API_FAILED, "飞书API错误"),

    # ==================== Webhook 错误 ====================
    (['获取webhook密钥失败'],
     ErrorCode.CONFIG_API_KEY_MISSING, "Webhook密钥获取失败"),

    # ==================== LLM/API 相关错误 ====================
    (['total tokens', 'exceed max'],
     ErrorCode.API_LLM_TOKEN_LIMIT, "Token总数超限"),
    (['input length', 'exceeds the maximum'],
     ErrorCode.API_LLM_TOKEN_LIMIT, "输入长度超限"),
    (['context_length_exceeded', 'maximum context length'],
     ErrorCode.API_LLM_TOKEN_LIMIT, "上下文长度超限"),
    (['llm model received multi-modal messages'],
     ErrorCode.API_LLM_INVALID_REQUEST, "LLM不支持多模态消息"),
    (['invalid messages'],
     ErrorCode.API_LLM_INVALID_REQUEST, "消息格式无效"),
    (['modelnotopen', 'has not activated the model'],
     ErrorCode.API_LLM_MODEL_NOT_FOUND, "模型未开通"),
    (['model not found'],
     ErrorCode.API_LLM_MODEL_NOT_FOUND, "模型未找到"),
    (['资源点不足', 'errbalanceoverdue'],
     ErrorCode.BUSINESS_QUOTA_INSUFFICIENT, "资源点不足"),
    (['errtoomanyrequest', '触发限流', 'rate limit'],
     ErrorCode.API_LLM_RATE_LIMIT, "请求频率限制"),

    # ==================== 递归限制错误 ====================
    (['recursion limit', 'graph_recursion_limit'],
     ErrorCode.RUNTIME_RECURSION_LIMIT, "递归深度超限"),

    # ==================== 类型/代码错误 ====================
    (['structuredtool', 'not callable'],
     ErrorCode.CODE_TYPE_NOT_CALLABLE, "StructuredTool对象不可调用"),
    (['object is not callable'],
     ErrorCode.CODE_TYPE_NOT_CALLABLE, "对象不可调用"),
    (['zerodivisionerror', 'division by zero'],
     ErrorCode.CODE_TYPE_WRONG_ARG, "除零错误"),
    (['unicodedecodeerror', 'unicodeencodeerror'],
     ErrorCode.RESOURCE_FILE_FORMAT_ERROR, "编码错误"),
    (['too many values to unpack', 'not enough values to unpack'],
     ErrorCode.CODE_TYPE_WRONG_ARG, "解包错误"),
    (['is not defined'],
     ErrorCode.CODE_NAME_NOT_DEFINED, "变量未定义"),
    (['cannot access local variable'],
     ErrorCode.CODE_NAME_NOT_DEFINED, "局部变量未定义"),
    (['got an unexpected keyword argument'],
     ErrorCode.CODE_TYPE_EXTRA_ARG, "函数参数错误"),
    (["can't compare offset-naive and offset-aware datetimes"],
     ErrorCode.CODE_TYPE_WRONG_ARG, "时区类型不兼容"),

    # ==================== AttributeError 模式 ====================
    (["'str' object has no attribute"],
     ErrorCode.CODE_ATTR_WRONG_TYPE, "字符串类型错误"),
    (["'nonetype' object has no attribute"],
     ErrorCode.CODE_ATTR_WRONG_TYPE, "对象为None"),
    (["'dict' object has no attribute"],
     ErrorCode.CODE_ATTR_WRONG_TYPE, "字典类型错误"),
    (["'list' object has no attribute"],
     ErrorCode.CODE_ATTR_WRONG_TYPE, "列表类型错误"),
    (['model_dump'],
     ErrorCode.CODE_ATTR_MODEL_DUMP, "对象类型错误"),
    (['object has no attribute'],
     ErrorCode.CODE_ATTR_NOT_FOUND, "属性不存在"),

    # ==================== 集成服务错误 ====================
    (['integration not found', 'code=190000006'],
     ErrorCode.INTEGRATION_SERVICE_UNAVAILABLE, "集成服务未找到"),
    (['integration credential failed', 'credential request failed'],
     ErrorCode.INTEGRATION_CREDENTIAL_INVALID, "集成凭证请求失败"),
    (['imap连接失败', 'imap error', 'imap失败'],
     ErrorCode.INTEGRATION_SERVICE_UNAVAILABLE, "邮件连接失败"),
    (['邮件发送失败', '邮件连接失败', '邮件操作失败'],
     ErrorCode.INTEGRATION_SERVICE_UNAVAILABLE, "邮件操作失败"),

    # ==================== 文件相关错误 ====================
    (['读取excel失败'],
     ErrorCode.RESOURCE_FILE_FORMAT_ERROR, "Excel读取失败"),
    (['解压文件失败', '解压失败'],
     ErrorCode.RESOURCE_FILE_FORMAT_ERROR, "解压文件失败"),
    (['openpyxl does not support'],
     ErrorCode.RESOURCE_FILE_FORMAT_ERROR, "Excel格式不支持"),
    (['文件不存在', 'file not found', 'not exist'],
     ErrorCode.RESOURCE_FILE_NOT_FOUND, "文件不存在"),

    # ==================== URL 相关错误 ====================
    (['url不支持直接使用', '临时签名url'],
     ErrorCode.API_NETWORK_URL_INVALID, "临时签名URL不支持"),
    (['链接已过期', 'url已过期'],
     ErrorCode.API_NETWORK_URL_INVALID, "链接已过期"),

    # ==================== 输入验证错误 ====================
    (['输入验证失败'],
     ErrorCode.VALIDATION_INPUT_INVALID, "输入验证失败"),
    (['没有有效的', '可供处理'],
     ErrorCode.VALIDATION_INPUT_EMPTY, "无有效输入"),
    (['未找到任何对话内容'],
     ErrorCode.VALIDATION_INPUT_EMPTY, "内容为空"),

    # ==================== 业务数据错误 ====================
    (['无法从搜索结果中提取'],
     ErrorCode.BUSINESS_DATA_NOT_FOUND, "数据提取失败"),
    (['未识别到', '无法识别'],
     ErrorCode.BUSINESS_DATA_NOT_FOUND, "识别失败"),
    (['最大搜索调用次数限制'],
     ErrorCode.BUSINESS_QUOTA_EXCEEDED, "搜索调用次数超限"),

    # ==================== 抖音相关错误 ====================
    (['抖音需要登录', 'douyin', 'cookie'],
     ErrorCode.CONFIG_API_KEY_MISSING, "抖音需要登录cookies"),
    (['解析抖音链接失败', '无法从抖音'],
     ErrorCode.BUSINESS_DATA_NOT_FOUND, "抖音链接解析失败"),

    # ==================== 通用失败模式 (优先级较低，放在最后) ====================
    (['抓取页面失败', '爬取失败', '页面抓取失败'],
     ErrorCode.API_NETWORK_HTTP_ERROR, "页面抓取失败"),
    (['大模型调用失败', 'llm调用失败', 'llm connection failed'],
     ErrorCode.API_NETWORK_CONNECTION, "大模型调用连接失败"),
    (['测试异常'],
     ErrorCode.RUNTIME_EXECUTION_FAILED, "测试异常"),

    # ==================== 剩余 900002 错误模式补充 ====================
    # 键不存在 (中文前缀)
    (['键不存在'],
     ErrorCode.CODE_KEY_NOT_FOUND, "键不存在"),
    
    # 类型错误 (中文前缀)
    (['类型错误', 'unsupported operand type'],
     ErrorCode.CODE_TYPE_WRONG_ARG, "类型错误"),
    
    # 缺少必需参数 (中文前缀)
    (['缺少必需参数'],
     ErrorCode.CODE_TYPE_MISSING_ARG, "缺少必需参数"),
    
    # bash 脚本错误
    (['bash:', 'no such file or directory', '进程退出码'],
     ErrorCode.RESOURCE_FILE_NOT_FOUND, "bash脚本文件不存在"),
    
    # 值错误 (中文前缀)
    (['值错误', 'time data', 'does not match format'],
     ErrorCode.VALIDATION_FIELD_VALUE, "时间格式错误"),
    (['值错误'],
     ErrorCode.VALIDATION_FIELD_VALUE, "值错误"),
    
    # 视频生成过程出错
    (['视频生成过程出错', '403 client error'],
     ErrorCode.API_LLM_AUTH_FAILED, "视频生成认证失败"),
    (['视频生成过程出错'],
     ErrorCode.API_VIDEO_GEN_FAILED, "视频生成过程出错"),
    
    # 运行时错误 (中文前缀)
    (['运行时错误', 'no current event loop'],
     ErrorCode.RUNTIME_THREAD_ERROR, "事件循环错误"),
    (['运行时错误'],
     ErrorCode.RUNTIME_EXECUTION_FAILED, "运行时错误"),
    
    # 视频生成失败 (中文前缀)
    (['视频生成失败', '403 client error'],
     ErrorCode.API_LLM_AUTH_FAILED, "视频生成认证失败"),
    (['视频生成失败', 'timeout'],
     ErrorCode.RUNTIME_TIMEOUT, "视频生成超时"),
    (['视频生成失败', 'no such file'],
     ErrorCode.RESOURCE_FILE_NOT_FOUND, "视频生成文件不存在"),
    (['视频生成失败'],
     ErrorCode.API_VIDEO_GEN_FAILED, "视频生成失败"),
    
    # 视频生成服务不可用
    (['视频生成服务不可用', '404'],
     ErrorCode.API_VIDEO_GEN_NOT_FOUND, "视频生成服务404"),
    (['视频生成服务不可用'],
     ErrorCode.API_VIDEO_GEN_FAILED, "视频生成服务不可用"),
    
    # ChatGeneration 类型错误
    (['unsupported operand type', 'chatgeneration'],
     ErrorCode.CODE_TYPE_WRONG_ARG, "LangChain类型错误"),
    
    # Function docstring 错误
    (['function must have a docstring'],
     ErrorCode.VALIDATION_FIELD_REQUIRED, "函数缺少docstring"),
    
    # 无法连接到代码服务器
    (['无法连接到代码服务器'],
     ErrorCode.API_NETWORK_CONNECTION, "代码服务器连接失败"),
    
    # JSON解析错误 (中文前缀)
    (['json解析错误'],
     ErrorCode.VALIDATION_JSON_DECODE, "JSON解析错误"),
    
    # Expecting property name (JSON错误)
    (['expecting property name enclosed in double quotes'],
     ErrorCode.VALIDATION_JSON_DECODE, "JSON格式错误"),
    
    # Missing required key(s) (LangGraph状态错误)
    (['missing required key', 'state_schema'],
     ErrorCode.BUSINESS_GRAPH_INVALID, "LangGraph状态缺少必需键"),
    
    # 参数数量错误 (中文前缀)
    (['参数数量错误'],
     ErrorCode.CODE_TYPE_EXTRA_ARG, "参数数量错误"),
    
    # 路径不存在
    (['路径', '不存在'],
     ErrorCode.RESOURCE_FILE_NOT_FOUND, "路径不存在"),
    
    # 对象不可迭代 (中文前缀)
    (['对象不可迭代'],
     ErrorCode.CODE_TYPE_NOT_ITERABLE, "对象不可迭代"),

    # ==================== 最后的边缘情况补充 ====================
    # INFO 日志误报 (非真正错误)
    (['info:', 'agents.coordinator'],
     ErrorCode.UNKNOWN_EXCEPTION, "日志信息误报"),
    
    # API请求无效
    (['api请求无效', 'invalid combination'],
     ErrorCode.API_LLM_INVALID_REQUEST, "API请求参数无效"),
    
    # 写入失败 + validation error
    (['写入', '失败', 'validation error'],
     ErrorCode.VALIDATION_FIELD_VALUE, "数据验证失败"),
    
    # 视频特征提取失败
    (['视频特征提取失败'],
     ErrorCode.RESOURCE_VIDEO_PROCESS_FAILED, "视频特征提取失败"),
    
    # keyword argument repeated
    (['keyword argument repeated'],
     ErrorCode.CODE_SYNTAX_INVALID, "关键字参数重复"),
    
    # unindent does not match
    (['unindent does not match'],
     ErrorCode.CODE_SYNTAX_INDENTATION, "缩进不匹配"),
    
    # invalid character (Unicode错误)
    (['invalid character', 'u+'],
     ErrorCode.CODE_SYNTAX_INVALID, "非法Unicode字符"),
    
    # got unexpected keyword arguments
    (['got unexpected keyword argument'],
     ErrorCode.CODE_TYPE_EXTRA_ARG, "函数参数错误"),
    
    # 需要配置环境变量
    (['需要配置', '环境变量', 'api_key'],
     ErrorCode.CONFIG_API_KEY_MISSING, "API Key未配置"),
    
    # 风格迁移失败
    (['风格迁移失败'],
     ErrorCode.API_IMAGE_GEN_FAILED, "风格迁移失败"),
    
    # 内存不足
    (['内存不足', 'bad_alloc'],
     ErrorCode.RUNTIME_MEMORY_ERROR, "内存不足"),
    
    # 视频内容分析失败
    (['视频内容分析失败'],
     ErrorCode.RESOURCE_VIDEO_PROCESS_FAILED, "视频内容分析失败"),
    
    # execute command error
    (['execute command error'],
     ErrorCode.RUNTIME_EXECUTION_FAILED, "命令执行错误"),
    
    # expected 'except' or 'finally' block
    (["expected 'except'", "'finally' block"],
     ErrorCode.CODE_SYNTAX_INVALID, "语法错误：缺少except/finally"),
    
    # 视频转存失败
    (['视频转存失败'],
     ErrorCode.RESOURCE_VIDEO_DOWNLOAD_FAILED, "视频转存失败"),
    
    # Attribute name is reserved
    (['attribute name', 'is reserved'],
     ErrorCode.CODE_ATTR_NOT_FOUND, "属性名保留字冲突"),
    
    # 视频生成超时
    (['视频生成超时'],
     ErrorCode.RUNTIME_TIMEOUT, "视频生成超时"),
    
    # ToolRuntime missing arguments
    (['toolruntime', 'missing', 'required positional argument'],
     ErrorCode.CODE_TYPE_MISSING_ARG, "ToolRuntime缺少必需参数"),
    
    # SQLAlchemy Table already defined
    (['table', 'is already defined', 'metadata'],
     ErrorCode.INTEGRATION_DB_QUERY, "数据库表定义重复"),
]

TRACEBACK_EXCEPTION_PATTERNS: List[ErrorPattern] = [
    # ==================== Python 内置异常 (从 Traceback 中提取) ====================
    # TypeError 细分
    (['typeerror: got an unexpected keyword argument'],
     ErrorCode.CODE_TYPE_EXTRA_ARG, "函数参数错误"),
    (["typeerror: missing"],
     ErrorCode.CODE_TYPE_MISSING_ARG, "缺少必需参数"),
    (['typeerror: \'nonetype\'', "typeerror: 'nonetype'"],
     ErrorCode.CODE_ATTR_WRONG_TYPE, "对象为None"),
    (['not callable'],
     ErrorCode.CODE_TYPE_NOT_CALLABLE, "对象不可调用"),
    (['not iterable'],
     ErrorCode.CODE_TYPE_NOT_ITERABLE, "对象不可迭代"),
    (['not subscriptable'],
     ErrorCode.CODE_TYPE_NOT_SUBSCRIPTABLE, "对象不支持下标访问"),
    (['typeerror:'],
     ErrorCode.CODE_TYPE_WRONG_ARG, "类型错误"),

    # ValueError 细分 - 注意：视频/图片相关的 ValueError 放在 ERROR_PATTERNS 中处理
    (['valueerror:'],
     ErrorCode.VALIDATION_FIELD_VALUE, "值错误"),

    # KeyError / IndexError
    (['keyerror:'],
     ErrorCode.CODE_KEY_NOT_FOUND, "键不存在"),
    (['indexerror:'],
     ErrorCode.CODE_INDEX_OUT_OF_RANGE, "索引越界"),

    # AttributeError 细分
    (['attributeerror:', 'model_dump'],
     ErrorCode.CODE_ATTR_MODEL_DUMP, "对象类型错误"),
    (["attributeerror: 'nonetype'"],
     ErrorCode.CODE_ATTR_WRONG_TYPE, "对象为None"),
    (['attributeerror:'],
     ErrorCode.CODE_ATTR_NOT_FOUND, "属性不存在"),

    # NameError / ImportError
    (['nameerror:'],
     ErrorCode.CODE_NAME_NOT_DEFINED, "名称未定义"),
    (['unboundlocalerror:'],
     ErrorCode.CODE_NAME_NOT_DEFINED, "名称未定义"),
    (['modulenotfounderror:'],
     ErrorCode.CODE_NAME_IMPORT_ERROR, "模块导入错误"),
    (['importerror:'],
     ErrorCode.CODE_NAME_IMPORT_ERROR, "模块导入错误"),
    (['filenotfounderror:'],
     ErrorCode.RESOURCE_FILE_NOT_FOUND, "文件不存在"),

    # IO 错误
    (['oserror:'],
     ErrorCode.RESOURCE_FILE_READ_ERROR, "文件读取错误"),
    (['ioerror:'],
     ErrorCode.RESOURCE_FILE_READ_ERROR, "文件读取错误"),
    (['cannot open resource'],
     ErrorCode.RESOURCE_FILE_READ_ERROR, "文件读取错误"),
    (['permissionerror:'],
     ErrorCode.RESOURCE_FILE_READ_ERROR, "权限错误"),

    # 运行时错误
    (['timeouterror:'],
     ErrorCode.RUNTIME_TIMEOUT, "执行超时"),
    (['asyncio.timeouterror'],
     ErrorCode.RUNTIME_TIMEOUT, "执行超时"),
    (['runtimeerror:'],
     ErrorCode.RUNTIME_EXECUTION_FAILED, "运行时错误"),
    (['recursionerror:'],
     ErrorCode.RUNTIME_RECURSION_LIMIT, "递归深度超限"),
    (['memoryerror:'],
     ErrorCode.RUNTIME_MEMORY_ERROR, "内存错误"),

    # ==================== Pydantic 验证错误 ====================
    (['validationerror:', 'field required'],
     ErrorCode.VALIDATION_FIELD_REQUIRED, "必填字段缺失"),
    (['validationerror:', 'missing'],
     ErrorCode.VALIDATION_FIELD_REQUIRED, "必填字段缺失"),
    (['validationerror:', 'input should be'],
     ErrorCode.VALIDATION_FIELD_TYPE, "字段类型错误"),
    (['validationerror:'],
     ErrorCode.VALIDATION_FIELD_CONSTRAINT, "验证失败"),

    # ==================== API 相关错误 ====================
    # 下载错误优先 - 防止被通用 apierror 捕获
    (['apierror:', 'error while downloading'],
     ErrorCode.RESOURCE_S3_DOWNLOAD_FAILED, "API下载失败"),
    (['apierror:', 'download'],
     ErrorCode.RESOURCE_S3_DOWNLOAD_FAILED, "下载失败"),
    (['openai.apierror:', 'error while downloading'],
     ErrorCode.RESOURCE_S3_DOWNLOAD_FAILED, "OpenAI下载失败"),
    # model not found
    (['apierror:', 'not found model'],
     ErrorCode.API_LLM_MODEL_NOT_FOUND, "模型不存在"),
    (['apierror:', 'model not found'],
     ErrorCode.API_LLM_MODEL_NOT_FOUND, "模型不存在"),
    (['apierror:', 'rate limit'],
     ErrorCode.API_LLM_RATE_LIMIT, "请求频率超限"),
    (['apierror:', 'token limit'],
     ErrorCode.API_LLM_TOKEN_LIMIT, "Token超限"),
    (['apierror:', 'context_length_exceeded'],
     ErrorCode.API_LLM_TOKEN_LIMIT, "Token超限"),
    (['apierror:', '401'],
     ErrorCode.API_LLM_AUTH_FAILED, "API认证失败"),
    (['apierror:', 'unauthorized'],
     ErrorCode.API_LLM_AUTH_FAILED, "API认证失败"),
    (['apierror:'],
     ErrorCode.API_LLM_REQUEST_FAILED, "API请求失败"),

    # ==================== LangGraph 错误 ====================
    (['invalidupdateerror', 'expected dict'],
     ErrorCode.CODE_TYPE_WRONG_ARG, "节点返回类型错误"),
    (['invalidupdateerror'],
     ErrorCode.CODE_TYPE_WRONG_ARG, "节点返回值无效"),
    (['graphrecursionerror'],
     ErrorCode.RUNTIME_RECURSION_LIMIT, "LangGraph递归限制"),

    # ==================== 网络错误 ====================
    (['connectionerror:'],
     ErrorCode.API_NETWORK_CONNECTION, "网络连接错误"),
    (['connectionrefusederror:'],
     ErrorCode.API_NETWORK_CONNECTION, "网络连接错误"),
    (['httperror:'],
     ErrorCode.API_NETWORK_HTTP_ERROR, "HTTP错误"),
    (['httpx.connecterror', 'httpx connecterror'],
     ErrorCode.API_NETWORK_CONNECTION, "HTTPX连接错误"),
    (['httpx.timeout', 'httpx timeout'],
     ErrorCode.API_NETWORK_TIMEOUT, "HTTPX超时错误"),
    (['remoteprotocolerror'],
     ErrorCode.API_NETWORK_REMOTE_PROTOCOL, "远程协议错误"),

    # ==================== 其他错误 ====================
    (['zerodivisionerror:'],
     ErrorCode.CODE_TYPE_WRONG_ARG, "除零错误"),
    (['assertionerror:'],
     ErrorCode.VALIDATION_FIELD_VALUE, "断言错误"),
    (['subprocesserror:'],
     ErrorCode.RUNTIME_SUBPROCESS_FAILED, "子进程执行失败"),
]

CUSTOM_EXCEPTION_PATTERNS: List[ErrorPattern] = [
    # ==================== 视频相关 ====================
    (['视频生成失败'],
     ErrorCode.API_VIDEO_GEN_FAILED, "视频生成失败"),
    (['没有生成任何视频片段', '视频片段生成失败'],
     ErrorCode.RESOURCE_VIDEO_SEGMENT_FAILED, "视频片段生成失败"),
    (['无法下载任何视频片段', '视频下载失败'],
     ErrorCode.RESOURCE_VIDEO_DOWNLOAD_FAILED, "视频下载失败"),
    (['failed to merge video', 'failed to create video'],
     ErrorCode.RESOURCE_FFMPEG_FAILED, "视频合并失败"),
    (['视频合成失败', '视频合并失败'],
     ErrorCode.RESOURCE_FFMPEG_FAILED, "视频合成失败"),

    # ==================== 图片相关 ====================
    (['无法下载图片', '图片下载失败'],
     ErrorCode.RESOURCE_IMAGE_DOWNLOAD_FAILED, "图片下载失败"),
    (['敏感内容', 'sensitive content'],
     ErrorCode.API_LLM_CONTENT_FILTER, "内容被安全过滤"),
    (['提交文生图任务失败'],
     ErrorCode.API_IMAGE_GEN_FAILED, "文生图任务失败"),
    (['图片识别失败'],
     ErrorCode.RESOURCE_IMAGE_PROCESS_FAILED, "图片识别失败"),

    # ==================== 下载相关 ====================
    (['下载失败', 'download failed'],
     ErrorCode.RESOURCE_S3_DOWNLOAD_FAILED, "下载失败"),
    (['所有下载策略都失败'],
     ErrorCode.RESOURCE_S3_DOWNLOAD_FAILED, "所有下载策略失败"),

    # ==================== API 相关 ====================
    (['api调用失败', 'api请求失败', 'api call failed'],
     ErrorCode.API_LLM_REQUEST_FAILED, "API调用失败"),
    (['llm调用失败', '大模型调用失败'],
     ErrorCode.API_LLM_REQUEST_FAILED, "LLM调用失败"),
    (['pixabay'],
     ErrorCode.API_NETWORK_HTTP_ERROR, "Pixabay API失败"),
    (['和风天气', 'qweather'],
     ErrorCode.API_NETWORK_HTTP_ERROR, "和风天气API失败"),

    # ==================== 解析相关 ====================
    (['解析失败', 'parse failed'],
     ErrorCode.RESOURCE_FILE_FORMAT_ERROR, "解析失败"),
    (['无法解析json', 'json解析失败', 'json decode error'],
     ErrorCode.VALIDATION_JSON_DECODE, "JSON解析失败"),

    # ==================== 配置相关 ====================
    (['请在config', '请设置环境变量'],
     ErrorCode.CONFIG_ENV_MISSING, "配置缺失"),
    (['access key', 'api_key缺失', 'api key missing'],
     ErrorCode.CONFIG_API_KEY_MISSING, "API Key缺失"),

    # ==================== 文件相关 ====================
    (['不支持的文件类型'],
     ErrorCode.RESOURCE_FILE_FORMAT_ERROR, "不支持的文件类型"),
    (['上传失败', 'upload failed'],
     ErrorCode.RESOURCE_S3_UPLOAD_FAILED, "上传失败"),
    (['no such file or directory', 'no such file'],
     ErrorCode.RESOURCE_FILE_NOT_FOUND, "文件不存在"),

    # ==================== 天气/外部服务 ====================
    (['无法获取实时天气', '无法获取天气'],
     ErrorCode.INTEGRATION_SERVICE_UNAVAILABLE, "天气服务不可用"),
    (['无法使用浏览器截图', '无法使用浏览器'],
     ErrorCode.CONFIG_WEBDRIVER_FAILED, "浏览器截图失败"),

    # ==================== 类型/键错误 ====================
    (['can only concatenate str'],
     ErrorCode.CODE_TYPE_WRONG_ARG, "字符串拼接类型错误"),
    (['键不存在', 'keyerror'],
     ErrorCode.CODE_KEY_NOT_FOUND, "键不存在"),
    (['缺少必需参数', 'missing required positional'],
     ErrorCode.CODE_TYPE_MISSING_ARG, "缺少必需参数"),

    # ==================== JSON/格式错误 ====================
    (['expecting property name enclosed in double quotes'],
     ErrorCode.VALIDATION_JSON_DECODE, "JSON属性名格式错误"),
    (['extra data:', 'line 1 column'],
     ErrorCode.VALIDATION_JSON_DECODE, "JSON包含多余数据"),
    (['invalid json format'],
     ErrorCode.VALIDATION_JSON_DECODE, "JSON格式无效"),

    # ==================== 运行时错误 ====================
    (['no current event loop', 'threadpoolexecutor'],
     ErrorCode.RUNTIME_ASYNC_NOT_IMPL, "事件循环错误"),
    (['视频生成过程出错', '403 client error', 'forbidden'],
     ErrorCode.API_LLM_AUTH_FAILED, "视频生成权限错误"),
    (['无法连接到代码服务器', '服务可能未启动'],
     ErrorCode.INTEGRATION_SERVICE_UNAVAILABLE, "代码服务器不可用"),
    (["'<' not supported between", "not supported between instances"],
     ErrorCode.CODE_TYPE_WRONG_ARG, "类型比较错误"),
    (['time data', 'does not match format'],
     ErrorCode.VALIDATION_FIELD_FORMAT, "时间格式错误"),
    (['missing required key', 'state_schema'],
     ErrorCode.VALIDATION_FIELD_REQUIRED, "状态字段缺失"),
    (['tool_calls that do not have', 'toolmessage'],
     ErrorCode.API_LLM_INVALID_REQUEST, "工具调用消息不匹配"),
    (['需要.*张.*图', '当前只有'],
     ErrorCode.VALIDATION_INPUT_INVALID, "图片数量不足"),
    (['takes 1 positional argument', 'positional argument but'],
     ErrorCode.CODE_TYPE_EXTRA_ARG, "参数数量错误"),
    (["unsupported operand type", "nonetype"],
     ErrorCode.CODE_ATTR_WRONG_TYPE, "None类型操作错误"),
]


def match_error_pattern(
    error_str: str,
    patterns: List[ErrorPattern] = None,
    require_all: bool = False
) -> Tuple[Optional[int], Optional[str]]:
    """
    使用模式表匹配错误消息
    
    Args:
        error_str: 错误消息字符串
        patterns: 要使用的模式表，默认使用 ERROR_PATTERNS
        require_all: 是否要求所有关键词都匹配（默认只需匹配一个）
    
    Returns:
        (error_code, error_message) 或 (None, None) 如果没有匹配
    """
    if patterns is None:
        patterns = ERROR_PATTERNS
    
    error_lower = error_str.lower()
    
    for keywords, code, msg_template in patterns:
        if require_all:
            if all(kw.lower() in error_lower for kw in keywords):
                return code, f"{msg_template}: {error_str[:200]}"
        else:
            if any(kw.lower() in error_lower for kw in keywords):
                return code, f"{msg_template}: {error_str[:200]}"
    
    return None, None


def match_traceback_pattern(error_str: str) -> Tuple[Optional[int], Optional[str]]:
    """匹配 Traceback 中的异常类型"""
    return match_error_pattern(error_str, TRACEBACK_EXCEPTION_PATTERNS)


def match_custom_exception_pattern(error_str: str) -> Tuple[Optional[int], Optional[str]]:
    """匹配自定义 Exception 的模式"""
    return match_error_pattern(error_str, CUSTOM_EXCEPTION_PATTERNS)
