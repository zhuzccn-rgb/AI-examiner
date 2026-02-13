# AI试卷生成工作流

## 项目概述

AI试卷生成工作流是一个基于LangGraph的智能教育工具，用于自动从PDF文档中提取题目、分析内容、构建知识索引，并生成符合特定知识点范围的试卷。

本项目采用模块化设计，通过工作流节点的形式实现了从PDF下载到试卷生成的完整流程，支持GPU加速的OCR识别、基于RAG的智能题目筛选，以及自定义试卷封面生成等功能。

### 核心价值

- **自动化试卷生成**：减少教师手动出卷的工作量
- **智能题目筛选**：基于知识点范围和目标分值自动选择合适的题目
- **GPU加速处理**：利用CUDA加速OCR识别，提高处理速度
- **可扩展性**：模块化设计，易于添加新功能或修改现有流程
- **本地部署**：支持使用LM Studio等本地LLM服务，保护数据隐私

## 功能特性

### 1. PDF处理与下载
- **批量PDF下载**：支持按考试代码批量下载相关试卷
- **PDF解析**：使用PyMuPDF高效解析PDF文档结构
- **本地文件支持**：同时支持从本地文件系统读取PDF文件

### 2. OCR识别
- **GPU加速**：支持CUDA GPU加速，提高OCR处理速度
- **多语言支持**：支持英文等多种语言的OCR识别
- **方向校正**：自动检测和校正文档方向
- **表格和图表识别**：支持识别文档中的表格和图表结构

### 3. 题目分析
- **LLM驱动**：使用本地LLM分析题目类型、分值和难度
- **智能提取**：自动从OCR结果中提取题目信息
- **JSON结构化输出**：将分析结果保存为结构化JSON格式

### 4. RAG知识检索
- **向量索引**：使用本地 embedding 模型构建知识向量索引
- **相似度搜索**：基于余弦相似度搜索相关知识点
- **并发处理**：使用多线程并发进行向量化，提高索引构建速度

### 5. 题目筛选
- **知识点匹配**：根据指定的知识点范围筛选相关题目
- **分值控制**：根据目标分值自动调整题目数量
- **多样化题目**：确保生成的试卷包含多种类型的题目

### 6. 试卷生成
- **自定义封面**：支持自定义试卷封面标题、副标题和作者信息
- **精确定位**：从原始PDF中精确提取题目页面
- **分析报告**：生成详细的试卷分析报告，包含题目分布和总分值

### 7. 部署与集成
- **多平台支持**：支持Windows、Linux和MacOS
- **HTTP API**：提供RESTful API接口，便于与其他系统集成
- **本地运行**：支持直接在本地运行工作流
- **配置灵活**：通过配置文件灵活调整系统参数

## 安装指南

### 系统要求

- **操作系统**：Windows 10/11, Windows Server 2019/2022, Linux, MacOS
- **Python版本**：Python 3.8+  
- **硬件要求**：
  - CPU：至少4核
  - 内存：至少8GB
  - GPU（推荐）：NVIDIA GPU，支持CUDA 11.8+
  - 存储空间：至少1GB

### 依赖项

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | 运行环境 |
| paddlepaddle-gpu | 3.0.12+ | 深度学习框架 |
| paddleocr | 最新版 | OCR识别引擎 |
| pymupdf | 最新版 | PDF处理 |
| requests | 最新版 | HTTP请求 |
| jinja2 | 最新版 | 模板渲染 |
| langgraph | 1.0+ | 工作流框架 |
| numpy | 最新版 | 数值计算 |

### Windows安装步骤

```powershell
# 1. 解压代码包（如果是压缩包形式）
# tar -xzf ai-exam-workflow-complete.tar.gz
# cd ai-exam-workflow-complete

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
.\venv\Scripts\activate

# 4. 安装paddlepaddle-gpu（使用百度镜像源加速）
https://www.paddleocr.ai/main/version3.x/pipeline_usage/OCR.html#1-ocr

# 5. 安装其他依赖
pip install -r requirements-windows.txt

```

### Linux/MacOS安装步骤

```bash
# 1. 解压代码包
# tar -xzf ai-exam-workflow-complete.tar.gz
# cd ai-exam-workflow-complete

# 2. 创建虚拟环境
python3 -m venv venv

# 3. 激活虚拟环境
source venv/bin/activate

# 4. 根据官方教程安装paddlepaddle-gpu
https://www.paddleocr.ai/main/version3.x/pipeline_usage/OCR.html#1-ocr

# 5. 安装其他依赖
pip3 install -r requirements.txt


### LM Studio配置

1. **下载并安装LM Studio**：从[官方网站](https://lmstudio.ai/)下载并安装
2. **下载模型**：在LM Studio中下载合适的LLM和embedding模型
3. **配置服务**：
   - 启动LM Studio的Local Server
   - 设置API端口为1234（默认）
   - 选择合适的模型作为chat_model和embedding_model

4. **编辑配置文件**：`config/lm_studio_cfg.json`

```json
{
  "base_url": "http://localhost:1234/v1",
  "chat_model": "your-chat-model-name",
  "embedding_model": "your-embedding-model-name"
}
```

### GPU配置（Windows）

1. **安装CUDA**：确保安装了兼容的CUDA版本（推荐12.6+）
2. **验证GPU可用性**：

```powershell
# 验证CUDA是否可用
python -c "import paddle; print(paddle.device.get_device())"

# 验证paddleocr是否使用GPU
python -c "from paddleocr import PaddleOCR; ocr = PaddleOCR(device='gpu:0'); print('GPU enabled')"
```

### 常见安装问题

| 问题 | 解决方案 |
|------|----------|
| patchelf错误 | Windows不需要patchelf，直接忽略 |
| CUDA不可用 | 检查CUDA安装，或使用CPU版本：`pip install paddlepaddle==3.0.0b1` |
| GPU内存不足 | 降低paddleocr的gpu_mem参数，或使用CPU模式 |
| 模型下载失败 | 检查网络连接，或手动下载模型到指定目录 |

## 文档索引

| 文档 | 说明 |
|------|------|
| `README.md` | 项目说明（本文件） |
| `config/WINDOWS_DEPLOYMENT_GUIDE.md` | Windows GPU详细部署指南 |
| `config/QUICK_REFERENCE.md` | 快速参考卡片 |
| `config/LM_STUDIO_CONFIG_GUIDE.md` | LM Studio配置指南 |

## 使用说明

### 1. HTTP API模式

```bash
# Linux/Mac
bash scripts/http_run.sh -p 8000

# Windows
python -m src.main.py -m http -p 8000
```

**API端点**：
- `POST /api/flow` - 运行完整工作流
- `GET /api/health` - 检查服务健康状态

### 2. 纯本地运行模式

```bash
# Linux/Mac
bash scripts/local_run.sh -m flow
or
python startup.py #recommended

# Windows
python -m src.main.py -m flow -i '{...}'
or
python startup.py #recommended
```

### 3. 工作流输入参数

```json
{
  "pdf_url": "https://example.com/exam.pdf",
  "knowledge_pdf_path": "./assets/knowledge.pdf",
  "required_score": 100,
  "knowledge_range": "基础概念",
  "cover_title": "测试试卷",
  "cover_subtitle": "AI自动生成",
  "cover_author": "AI Assistant",
  "exam_code": "9618",
  "year": "s23"
}
```

**参数说明**：
- `pdf_url`：PDF文件的下载URL（可选，与exam_code二选一）
- `exam_code`：考试代码，用于批量下载试卷（可选，与pdf_url二选一）
- `year`：考试年份，与exam_code配合使用
- `knowledge_pdf_path`：知识点PDF文件路径
- `required_score`：目标总分值
- `knowledge_range`：知识点范围
- `cover_title`：试卷封面标题
- `cover_subtitle`：试卷封面副标题
- `cover_author`：试卷封面作者

### 4. 工作流输出

```json
{
  "final_pdf_path": "/path/to/exam_paper.pdf",
  "analysis_report": "试卷生成报告..."
}
```

**输出说明**：
- `final_pdf_path`：生成的试卷PDF文件路径
- `analysis_report`：试卷分析报告，包含题目分布和总分值

## 常见问题

### Windows用户

**Q: patchelf编译失败**
- A: 正常！Windows不需要，直接忽略

**Q: CUDA不可用**
- A: 安装了CPU版本，重新安装GPU版本

**Q: GPU内存不足**
- A: 降低 `gpu_mem` 参数

### Linux/Mac用户

**Q: 权限错误**
- A: 使用 `chmod +x scripts/*.sh` 给脚本添加执行权限

**Q: 依赖安装失败**
- A: 尝试使用 `pip install --upgrade pip` 升级pip后重试

## API文档

### 1. HTTP API端点

#### POST /api/flow

**描述**：运行完整的试卷生成工作流

**请求体**：
```json
{
  "pdf_url": "https://example.com/exam.pdf",
  "knowledge_pdf_path": "./assets/knowledge.pdf",
  "required_score": 100,
  "knowledge_range": "基础概念",
  "cover_title": "测试试卷",
  "cover_subtitle": "AI自动生成",
  "cover_author": "AI Assistant",
  "exam_code": "9618",
  "year": "s23"
}
```

**响应**：
```json
{
  "status": "success",
  "data": {
    "final_pdf_path": "/path/to/exam_paper.pdf",
    "analysis_report": "试卷生成报告..."
  },
  "message": "工作流执行成功"
}
```

#### GET /api/health

**描述**：检查服务健康状态

**响应**：
```json
{
  "status": "healthy",
  "service": "ai-exam-workflow",
  "version": "1.0.0"
}
```

### 2. 工作流节点API

#### PDF下载节点
- **功能**：下载PDF文件或批量下载试卷
- **输入**：`pdf_url` 或 `exam_code` + `year`
- **输出**：下载的PDF文件路径列表

#### OCR识别节点
- **功能**：对PDF执行OCR识别
- **输入**：PDF文件路径
- **输出**：OCR结果JSON文件路径

#### 题目分析节点
- **功能**：分析题目类型、分值和难度
- **输入**：OCR结果JSON文件路径
- **输出**：题目分析结果JSON文件路径

#### RAG索引节点
- **功能**：构建知识向量索引
- **输入**：知识点PDF路径
- **输出**：向量索引文件路径

#### RAG检索节点
- **功能**：检索与知识点相关的内容
- **输入**：知识点范围、向量索引
- **输出**：相关知识点内容

#### 题目筛选节点
- **功能**：根据知识点筛选题目
- **输入**：题目分析结果、RAG检索结果、目标分值
- **输出**：筛选后的题目列表

#### 试卷生成节点
- **功能**：生成最终试卷PDF
- **输入**：筛选后的题目列表、封面信息
- **输出**：最终试卷PDF路径、分析报告

## 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | 运行环境 |
| LangGraph | 1.0+ | 工作流框架 |
| PaddleOCR | 最新版 | OCR识别引擎 |
| PyMuPDF | 最新版 | PDF处理 |
| LM Studio | 最新版 | 本地LLM服务 |
| FastAPI | 最新版 | HTTP服务 |
| NumPy | 最新版 | 数值计算 |
| Jinja2 | 最新版 | 模板渲染 |

## 工作流架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ 输入参数    │ ──> │ PDF下载    │ ──> │ OCR识别     │
└─────────────┘     └─────────────┘     └─────────────┘
                        │                     │
                        ▼                     ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ 试卷生成    │ <── │ 题目筛选    │ <── │ 题目分析    │
└─────────────┘     └─────────────┘     └─────────────┘
                        ▲                     │
                        │                     │
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ 输出结果    │ <── │ RAG检索    │ <── │ RAG索引     │
└─────────────┘     └─────────────┘     └─────────────┘
```

### 核心流程说明

1. **输入处理**：接收用户输入参数，验证必填字段
2. **PDF获取**：根据输入的URL或考试代码获取PDF文件
3. **内容提取**：使用OCR技术提取PDF中的文本内容
4. **智能分析**：使用LLM分析题目类型、分值和难度
5. **知识索引**：构建知识点的向量索引，用于相关度搜索
6. **智能筛选**：基于知识点范围和目标分值筛选合适的题目
7. **试卷生成**：将筛选的题目组合成完整的试卷
8. **结果输出**：返回生成的试卷路径和分析报告
## 贡献指南

### 开发环境设置

1. **克隆仓库**：
   ```bash
   git clone <repository-url>
   cd ai-exam-workflow-complete
   ```

2. **创建开发环境**：
   ```bash
   python -m venv venv_dev
   source venv_dev/bin/activate  # Linux/Mac
   # .\venv_dev\Scripts\activate  # Windows
   pip install -e "[dev]"
   ```

3. **安装开发依赖**：
   ```bash
   pip install pytest flake8 black isort
   ```

### 代码风格规范

- **代码格式**：使用 `black` 进行代码格式化
- **导入排序**：使用 `isort` 对导入进行排序
- **代码检查**：使用 `flake8` 进行代码质量检查
- **类型提示**：为所有函数和方法添加类型提示
- **文档字符串**：为所有公共函数添加详细的文档字符串

### 提交规范

- **提交消息格式**：
  ```
  <type>(<scope>): <description>
  
  <body>
  ```

- **类型说明**：
  - `feat`：新功能
  - `fix`：bug修复
  - `docs`：文档更新
  - `style`：代码风格调整
  - `refactor`：代码重构
  - `perf`：性能优化
  - `test`：测试相关
  - `chore`：构建或依赖更新

### 测试指南

1. **运行单元测试**：
   ```bash
   pytest tests/unit/
   ```

2. **运行集成测试**：
   ```bash
   pytest tests/integration/
   ```

3. **测试覆盖报告**：
   ```bash
   pytest --cov=src tests/
   ```
## 技术支持

### 联系方式
- **GitHub Issues**：提交问题和功能请求
- **邮件支持**：cnzhuzc@163.com
- **wechat**：19398613742（arthur）

### 贡献流程

1. **Fork仓库**：在GitHub上fork项目仓库
2. **创建分支**：从 `main` 分支创建功能分支
3. **开发功能**：实现新功能或修复bug
4. **运行测试**：确保所有测试通过
5. **提交代码**：使用规范的提交消息格式
6. **创建PR**：提交Pull Request，描述功能变更
7. **代码审查**：响应审查意见并进行必要的修改
8. **合并分支**：PR通过后合并到 `main` 分支

## 许可证

本项目基于 **MIT许可证** 开源。

```
MIT License

Copyright (c) 2024 AI Exam Workflow Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 故障排查

1. **查看日志**：
   ```bash
   # Linux/Mac
   tail -f logs/app.log
   
   # Windows
   Get-Content logs\app.log -Wait
   ```

2. **常见错误排查**：
   - OCR失败：检查GPU驱动和CUDA版本
   - LLM连接失败：检查LM Studio服务是否运行
   - PDF下载失败：检查网络连接和URL格式

3. **性能问题**：
   - 降低OCR的 `gpu_mem` 参数
   - 增加系统内存
   - 使用更高性能的GPU

---

**感谢您使用AI试卷生成工作流！** 

*如有任何问题或建议，欢迎通过GitHub Issues和wechat与我们交流。*

