# LM Studio 配置快速参考卡片

**只需修改一个文件：`config/lm_studio_cfg.json`**

##  快速配置（3步）

###  启动LM Studio

```
LM Studio → Local Server → Start Server (端口: 1234)
```

###  修改配置文件

编辑 `config/lm_studio_cfg.json`：

```json
{
  "base_url": "http://localhost:1234/v1",    ⭐ 只需修改这一行！
  "chat_model": "local-model",               ⭐ 可选：修改为您的模型名
  "embedding_model": "local-embedding",      ⭐ 可选：修改为您的模型名
  "temperature": 0.0,
  "top_p": 0.9,
  "max_tokens": 4000,
  "timeout": 60
}
```

###  测试

```bash
curl http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"local-model","messages":[{"role":"user","content":"Hi"}]}'
```

##  常见配置示例

### 默认端口 1234
```json
{
  "base_url": "http://localhost:1234/v1",
  ...
}
```

### 自定义端口 8080
```json
{
  "base_url": "http://localhost:8080/v1",
  ...
}
```

### 远程服务器
```json
{
  "base_url": "http://192.168.1.100:1234/v1",
  ...
}
```

### 使用OpenAI API
```json
{
  "base_url": "https://api.openai.com/v1",
  "chat_model": "gpt-4o-mini",
  "embedding_model": "text-embedding-3-small",
  ...
}
```

##  相关文件

| 文件 | 用途 | 是否需要修改 |
|------|------|-------------|
| `config/lm_studio_cfg.json` |  LM Studio主配置 |  **必须修改** |
| `config/questions_analysis_cfg.json` | 题目分析配置 |  确保base_url一致 |
| `config/LM_STUDIO_CONFIG_GUIDE.md` | 详细配置指南 |  参考 |

##  遇到问题？

1. **连接失败** → 检查LM Studio是否启动，端口是否正确
2. **模型未找到** → 确认模型名称，在LM Studio中查看
3. **响应慢** → 增加timeout值，使用更小的模型

##  详细文档

查看完整指南：`config/LM_STUDIO_CONFIG_GUIDE.md`

---

**就这么简单！修改一个文件即可！** 

---

# Windows Server 2022 部署快速参考（NVIDIA TCC GPU）

##  重要提醒

**`patchelf` 无法在Windows上编译是正常的！**
- patchelf是Linux专用工具
- Windows不需要patchelf
- 直接忽略即可

## 🚀 3步快速部署

### 步骤1: 安装NVIDIA驱动和CUDA

```powershell
# 查看GPU
nvidia-smi

# 安装CUDA Toolkit 12.9 (推荐）
# 下载: https://developer.nvidia.com/cuda-downloads
# 安装cuDNN并配置环境变量
```

### 步骤2: 安装PaddlePaddle GPU版本

```powershell
# 创建虚拟环境
python -m venv venv
.\venv\Scripts\activate

# 安装GPU版本（不是CPU版本！）
python -m pip install paddlepaddle-gpu==3.0.0b1 -i https://mirror.baidu.com/pypi/simple
```

### 步骤3: 安装PaddleOCR和其他依赖

```powershell
pip install paddleocr
pip install -r requirements.txt
pip install pymupdf requests jinja2
```

##  验证GPU支持

```python
import paddle
print(f"CUDA可用: {paddle.device.is_compiled_with_cuda()}")
```

**预期输出**: `CUDA可用: True`

##  OCR初始化（启用GPU）

```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(
    use_angle_cls=True,
    lang='ch/en',
    use_gpu=True,  # 关键：启用GPU
    gpu_id=0,     # GPU ID
    gpu_mem=800    # GPU内存（MB）
)
```

##  常见问题

**Q: patchelf编译失败**
- A: 正常！Windows不需要，直接忽略

**Q: CUDA not available**
- A: 安装了CPU版本，重新安装GPU版本

**Q: GPU内存不足**
- A: 降低 `gpu_mem` 参数或清理GPU内存

##  详细指南

查看完整文档：`README.md`
