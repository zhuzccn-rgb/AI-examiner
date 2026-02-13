# LM Studio 本地大模型配置指南

## 📋 概述

本指南说明如何配置流水线以调用本地运行的LM Studio大模型服务。

## 🎯 需要修改的配置文件

工作流中有**3个配置文件**需要修改：

### 1. `config/lm_studio_cfg.json` ⭐ 主要配置文件

这是**统一的LM Studio配置文件**，控制所有节点对LM Studio API的调用。

```json
{
  "base_url": "http://localhost:1234/v1",
  "chat_model": "local-model",
  "embedding_model": "local-embedding",
  "temperature": 0.0,
  "top_p": 0.9,
  "max_tokens": 4000,
  "timeout": 60
}
```

**配置说明**：

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `base_url` | string | `http://localhost:1234/v1` | LM Studio API的地址 ⭐ **必须修改** |
| `chat_model` | string | `local-model` | 聊天模型的名称 |
| `embedding_model` | string | `local-embedding` | 嵌入模型的名称 |
| `temperature` | float | 0.0 | 温度参数（0-1，越低越确定） |
| `top_p` | float | 0.9 | Top-p采样参数 |
| `max_tokens` | integer | 4000 | 最大生成token数 |
| `timeout` | integer | 60 | 请求超时时间（秒） |

### 2. `config/questions_analysis_cfg.json` - 题目分析节点配置

这是题目分析节点专用的配置文件，包含系统提示词和模型配置。

```json
{
  "config": {
    "base_url": "http://localhost:1234/v1",  ⭐ 确保与lm_studio_cfg.json一致
    "model": "local-model",
    "temperature": 0.0,
    "top_p": 0.9,
    "max_completion_tokens": 4000,
    "timeout": 600,
    "thinking": "disabled"
  },
  "sp": "# 角色定义\n你是试卷题目分析专家...",
  "up": "请分析以下试卷内容..."
}
```

## 🔧 详细配置步骤

### 步骤1: 启动LM Studio并配置API服务

#### 1.1 安装LM Studio

下载并安装LM Studio：https://lmstudio.ai/

#### 1.2 加载模型

1. 打开LM Studio
2. 在左侧搜索栏搜索并下载模型，例如：
   - `Llama 3.1 8B Instruct`
   - `Qwen2.5 7B Instruct`
   - `Mistral 7B Instruct`

#### 1.3 启动API服务

1. 点击左侧的 **💬 Local Server**
2. 选择加载的模型
3. 配置服务器端口（默认端口：**1234**）
4. 点击 **Start Server** 启动服务

#### 1.4 验证API可用性

```bash
# 测试聊天API
curl http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "local-model",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'

# 测试embedding API（如果模型支持）
curl http://localhost:1234/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "local-embedding",
    "input": "Hello world"
  }'
```

### 步骤2: 修改配置文件

#### 2.1 修改 `config/lm_studio_cfg.json`

根据您的LM Studio配置修改：

```json
{
  "base_url": "http://localhost:1234/v1",  // 如果LM Studio使用其他端口，修改这里
  "chat_model": "Llama-3.1-8B-Instruct",  // 修改为您的模型名称
  "embedding_model": "local-embedding",   // 如果没有embedding模型，可以使用相同的聊天模型
  "temperature": 0.0,
  "top_p": 0.9,
  "max_tokens": 4000,
  "timeout": 60
}
```

**常见配置场景**：

**场景1: LM Studio运行在默认端口1234**
```json
{
  "base_url": "http://localhost:1234/v1",
  "chat_model": "Llama-3.1-8B-Instruct",
  "embedding_model": "Llama-3.1-8B-Instruct",
  ...
}
```

**场景2: LM Studio运行在其他端口（如8080）**
```json
{
  "base_url": "http://localhost:8080/v1",
  "chat_model": "Qwen2.5-7B-Instruct",
  "embedding_model": "Qwen2.5-7B-Instruct",
  ...
}
```

**场景3: LM Studio运行在远程服务器**
```json
{
  "base_url": "http://192.168.1.100:1234/v1",
  "chat_model": "Mistral-7B-Instruct",
  "embedding_model": "Mistral-7B-Instruct",
  ...
}
```

#### 2.2 确认 `config/questions_analysis_cfg.json`

确保该文件中的 `base_url` 与 `lm_studio_cfg.json` 一致：

```json
{
  "config": {
    "base_url": "http://localhost:1234/v1",  // ⭐ 确保一致
    "model": "Llama-3.1-8B-Instruct",         // ⭐ 使用正确的模型名称
    ...
  }
}
```

### 步骤3: 测试配置

#### 3.1 测试题目分析节点

```bash
bash scripts/local_run.sh -m node -n questions_analysis_node -i '{
  "markdown_content": "## 第1页\n\n1. 这是一个选择题。\n2. 这是一个填空题。"
}'
```

#### 3.2 测试完整工作流

```bash
bash scripts/local_run.sh -m flow -i '{
  "pdf_url": "https://example.com/exam.pdf",
  "knowledge_pdf_path": "./assets/knowledge.pdf",
  "required_score": 100,
  "knowledge_range": "基础概念",
  "cover_title": "测试试卷"
}'
```

## 🔍 常见问题

### Q1: 连接被拒绝（Connection refused）

**错误信息**：
```
HTTPConnectionPool(host='localhost', port=1234): Max retries exceeded
```

**解决方案**：
1. 确认LM Studio已启动
2. 检查端口配置是否正确
3. 查看LM Studio的Server tab确认端口号
4. 在配置文件中修改 `base_url` 为正确的端口

### Q2: 模型未找到

**错误信息**：
```
Model 'local-model' not found
```

**解决方案**：
1. 在LM Studio中加载模型
2. 确认模型名称（在LM Studio的Server tab中查看）
3. 在配置文件中修改 `chat_model` 为正确的模型名称

### Q3: API响应慢或超时

**解决方案**：
1. 在配置文件中增加 `timeout` 值
2. 使用更小的模型（如7B而非70B）
3. 确保硬件资源充足（GPU/CPU）

### Q4: Embedding模型不可用

**解决方案**：
1. 如果模型不支持embedding，使用相同的聊天模型：
   ```json
   {
     "embedding_model": "Llama-3.1-8B-Instruct"
   }
   ```
2. 或使用专用的embedding模型（如 `bge-small-zh-v1.5`）

## 📊 配置示例合集

### 示例1: 本地LM Studio + Llama 3.1

```json
// config/lm_studio_cfg.json
{
  "base_url": "http://localhost:1234/v1",
  "chat_model": "Llama-3.1-8B-Instruct",
  "embedding_model": "Llama-3.1-8B-Instruct",
  "temperature": 0.0,
  "top_p": 0.9,
  "max_tokens": 4000,
  "timeout": 60
}
```

### 示例2: 远程LM Studio + Qwen 2.5

```json
// config/lm_studio_cfg.json
{
  "base_url": "http://192.168.1.100:8080/v1",
  "chat_model": "Qwen2.5-7B-Instruct",
  "embedding_model": "Qwen2.5-7B-Instruct",
  "temperature": 0.0,
  "top_p": 0.9,
  "max_tokens": 4000,
  "timeout": 90
}
```

### 示例3: 使用OpenAI API

```json
// config/lm_studio_cfg.json
{
  "base_url": "https://api.openai.com/v1",
  "chat_model": "gpt-4o-mini",
  "embedding_model": "text-embedding-3-small",
  "temperature": 0.0,
  "top_p": 0.9,
  "max_tokens": 4000,
  "timeout": 60
}
```

⚠️ **注意**：使用OpenAI API需要额外配置API Key，需要修改代码添加认证头。

## 🎓 高级配置

### 环境变量配置

您也可以通过环境变量覆盖配置：

```bash
# 设置LM Studio地址
export LM_STUDIO_BASE_URL="http://localhost:8080/v1"

# 设置模型名称
export LM_STUDIO_CHAT_MODEL="Qwen2.5-7B-Instruct"
export LM_STUDIO_EMBEDDING_MODEL="Qwen2.5-7B-Instruct"

# 运行工作流
bash scripts/http_run.sh
```

### Docker部署配置

如果在Docker中运行，需要确保容器可以访问LM Studio：

```yaml
# docker-compose.yml
version: '3'
services:
  ai-exam:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LM_STUDIO_BASE_URL=http://host.docker.internal:1234/v1
```

## 📝 总结

**最关键的配置步骤**：

1. ✅ 启动LM Studio并加载模型
2. ✅ 修改 `config/lm_studio_cfg.json` 中的 `base_url`
3. ✅ 确保 `chat_model` 和 `embedding_model` 正确
4. ✅ 测试API连接
5. ✅ 运行工作流验证

完成这些步骤后，您的流水线就能正常调用本地大模型了！

## 🆘 获取帮助

如果遇到问题，请检查：

1. LM Studio日志：在LM Studio的 **Logs** tab中查看
2. 工作流日志：`tail -f /app/work/logs/bypass/app.log`
3. API测试：使用curl命令测试API是否可用

---

**配置完成后，享受高效的本地大模型服务吧！** 🚀
