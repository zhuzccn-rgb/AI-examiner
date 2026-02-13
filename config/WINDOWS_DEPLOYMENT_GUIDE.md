# PaddleOCR Windows Server 2022 部署指南（NVIDIA TCC GPU支持）

## 📋 问题描述

1. **目标**：在Windows Server 2022上部署AI试卷生成工作流
2. **需求**：让PaddleOCR使用NVIDIA的TCC计算卡（Tesla/数据中心GPU）
3. **问题**：安装依赖时 `patchelf` 无法在Windows上编译

## 🎯 核心说明

### 关于 patchelf

**`patchelf` 是Linux专用工具，Windows上不需要！**

- **Linux**: 使用ELF格式的二进制文件 → 需要patchelf
- **Windows**: 使用PE格式的二进制文件 → 不需要patchelf

**这是正常现象，不用担心！**

## 🔧 完整部署步骤

### 步骤1: 安装NVIDIA驱动和CUDA

#### 1.1 确认GPU型号

```powershell
# 查看GPU信息
nvidia-smi
```

**TCC模式支持**：
- Tesla系列（如Tesla T4, V100, A100等）✅ 原生支持TCC
- GeForce/Quadro系列（如RTX 3090, 4090等）⚠️ 可能需要手动启用TCC

#### 1.2 安装NVIDIA驱动

下载并安装企业级驱动（推荐）：
- 官方下载: https://www.nvidia.com/Download/index.aspx
- 选择 **"Data Center / Tesla"** 类别的驱动
- 或者使用 **"Production Branch / Studio"** 驱动

#### 1.3 安装CUDA Toolkit

**重要**：PaddleOCR对CUDA版本有要求！

查看PaddlePaddle支持的CUDA版本：
- Python 3.10: 推荐 CUDA 11.8 或 12.1
- Python 3.12: 推荐 CUDA 12.1 或 12.4

下载地址：https://developer.nvidia.com/cuda-downloads

#### 1.4 安装cuDNN

1. 下载：https://developer.nvidia.com/cudnn
2. 解压到CUDA安装目录，例如：
   ```
   C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1\
   ```

#### 1.5 配置环境变量

添加到系统环境变量：

```powershell
# CUDA
CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1
CUDA_PATH_V12_1=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1

# cuDNN
CUDNN_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1\bin

# 添加到PATH
%CUDA_PATH%\bin
%CUDA_PATH%\libnvvp
%CUDNN_PATH%
```

### 步骤2: 安装Python环境

#### 2.1 安装Python

推荐使用 **Python 3.10** 或 **Python 3.12**

下载地址：https://www.python.org/downloads/

**安装时勾选**：
- ✅ "Add Python to PATH"

#### 2.2 创建虚拟环境（推荐）

```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\activate
```

### 步骤3: 安装PaddlePaddle GPU版本 ⭐ 关键

**关键点**：不要直接安装 `paddleocr`，先安装 `paddlepaddle-gpu`！

#### 3.1 卸载CPU版本（如果之前安装过）

```powershell
pip uninstall paddlepaddle paddleocr -y
```

#### 3.2 安装PaddlePaddle GPU版本

**方案A：直接安装（推荐）**

```powershell
# Python 3.10 + CUDA 11.8
python -m pip install paddlepaddle-gpu==3.0.0b1 -i https://mirror.baidu.com/pypi/simple

# Python 3.10 + CUDA 12.1
python -m pip install paddlepaddle-gpu==3.0.0b1 -i https://mirror.baidu.com/pypi/simple

# Python 3.12 + CUDA 12.4
python -m pip install paddlepaddle-gpu==3.0.0b1 -i https://mirror.baidu.com/pypi/simple
```

**方案B：使用预编译包**

如果方案A失败，使用预编译的wheel包：

```powershell
# 访问 https://www.paddlepaddle.org.cn/install/quick
# 选择对应的版本下载wheel包，然后：
python -m pip install paddlepaddle_gpu-3.0.0b1-cp310-cp310-win_amd64.whl
```

#### 3.3 验证PaddlePaddle GPU支持

```python
import paddle
print(f"Paddle版本: {paddle.__version__}")
print(f"CUDA可用: {paddle.device.is_compiled_with_cuda()}")
print(f"CUDA版本: {paddle.version.cuda_version()}")

# 测试GPU
paddle.device.set_device('gpu:0')
print("GPU测试成功！")
```

**预期输出**：
```
Paddle版本: 3.0.0b1
CUDA可用: True
CUDA版本: 12.1
GPU测试成功！
```

### 步骤4: 安装PaddleOCR

```powershell
pip install paddleocr
```

### 步骤5: 安装其他依赖

```powershell
# 安装项目依赖
pip install -r requirements.txt

# 安装额外的依赖
pip install pymupdf requests jinja2
```

### 步骤6: 配置TCC模式（如需要）

#### 6.1 检查当前GPU模式

```powershell
nvidia-smi --query-gpu=compute_mode --format=csv
```

**输出说明**：
- `Default`: 自动选择
- `Exclusive_Process`: 独占进程模式
- `Prohibited`: 禁用GPU计算
- `Exclusive_Thread`: 独占线程模式

#### 6.2 启用TCC模式（针对GeForce/Quadro卡）

对于Tesla卡，TCC通常是默认模式。如果需要手动启用：

```powershell
# 使用NVIDIA-SMI设置（需要管理员权限）
nvidia-smi -i 0 -dm 1
nvidia-smi -i 0 -pm 1
nvidia-smi -i 0 -ac 1493,900
```

或者使用 `nvidia-smi` 的TCC开关：

```powershell
# 设置TCC模式（部分驱动支持）
nvidia-smi -fdm 1
```

**注意**：
- TCC模式可能不支持某些Windows图形API
- Tesla卡默认已经使用TCC
- 修改后可能需要重启

### 步骤7: 测试PaddleOCR GPU

```python
from paddleocr import PaddleOCR
import time

# 初始化OCR（使用GPU）
ocr = PaddleOCR(
    use_angle_cls=True,
    lang='ch',
    use_gpu=True,  # 关键：启用GPU
    gpu_mem=500,    # GPU内存限制（MB）
    show_log=True
)

# 测试图片
import cv2
img_path = "test.jpg"

start = time.time()
result = ocr.ocr(img_path, cls=True)
end = time.time()

print(f"OCR完成，耗时: {end-start:.2f}秒")
print(f"识别结果: {result[0]}")
```

**预期输出**（如果GPU工作正常）：
```
[INFO] ppocr init ...
[INFO] ppocr postprocess ...
[INFO] use_gpu: True
[INFO] gpu_id: 0
OCR完成，耗时: 0.35秒  # 应该比CPU快很多
```

### 步骤8: 验证整个工作流

```powershell
# 激活虚拟环境
.\venv\Scripts\activate

# 进入项目目录
cd C:\path\to\ai-exam-workflow-complete

# 运行测试
python -m src.main.py -m flow -i '{
  "pdf_url": "https://example.com/exam.pdf",
  "knowledge_pdf_path": "./assets/knowledge.pdf",
  "required_score": 100,
  "knowledge_range": "基础概念",
  "cover_title": "测试试卷"
}'
```

## 🐛 常见问题

### 问题1: ImportError: DLL load failed

**原因**：缺少CUDA或cuDNN库

**解决**：
1. 确认CUDA和cuDNN已正确安装
2. 将CUDA的`bin`目录添加到PATH
3. 重启终端或计算机

### 问题2: CUDA not available

**原因**：安装了CPU版本的PaddlePaddle

**解决**：
```powershell
# 卸载CPU版本
pip uninstall paddlepaddle -y

# 重新安装GPU版本
python -m pip install paddlepaddle-gpu==3.0.0b1 -i https://mirror.baidu.com/pypi/simple
```

### 问题3: GPU内存不足

**原因**：GPU内存被占用

**解决**：
```python
# 限制GPU内存使用
ocr = PaddleOCR(
    use_gpu=True,
    gpu_mem=200  # 降低到200MB
)
```

或者清理GPU内存：
```powershell
nvidia-smi --gpu-reset
```

### 问题4: 检测到GPU但性能没有提升

**原因**：TCC模式未正确配置

**解决**：
```python
import paddle

# 强制使用GPU
paddle.set_device('gpu:0')

# 查看设备信息
print(paddle.device.cuda.device_count())
print(paddle.device.cuda.get_device_name(0))
```

### 问题5: 编译错误

**原因**：尝试从源码编译

**解决**：
- **不要从源码编译**
- 使用预编译的wheel包
- 使用清华或百度镜像加速

## 📊 性能对比

| 配置 | 单页OCR耗时 | 说明 |
|------|-------------|------|
| CPU (Intel Xeon) | 2-3秒 | 依赖CPU性能 |
| GPU (Tesla T4, TCC) | 0.3-0.5秒 | 6-10倍加速 |
| GPU (RTX 3090, WDDM) | 0.2-0.4秒 | 7-15倍加速 |

## 🎯 优化建议

### 1. 批处理优化

```python
# 一次处理多页
batch_size = 4  # 根据GPU内存调整
results = ocr.ocr([img1, img2, img3, img4], cls=True)
```

### 2. 多GPU支持

```python
import paddle

# 使用多个GPU
paddle.set_device('gpu:1')  # 使用第二个GPU
```

### 3. 预加载模型

```python
# 启动时初始化OCR，避免每次调用重新加载
ocr = PaddleOCR(use_gpu=True)
```

## 📝 Windows特定配置

### 修改 `node.py` 中的OCR初始化

在 `src/graphs/node.py` 中找到 `ocr_recognition_node` 函数，修改：

```python
# 初始化OCR引擎（Windows GPU版）
ocr = PaddleOCR(
    use_angle_cls=True,
    lang='ch',
    use_gpu=True,          # 启用GPU
    gpu_id=0,             # 使用第一个GPU
    gpu_mem=800,          # GPU内存限制（MB）
    show_log=False,         # 关闭详细日志
    det_db_thresh=0.3,     # 检测阈值
    det_db_box_thresh=0.5  # 边框阈值
)
```

### 环境变量配置

在 `config/lm_studio_cfg.json` 中添加：

```json
{
  "base_url": "http://localhost:1234/v1",
  "chat_model": "local-model",
  "embedding_model": "local-embedding",
  "temperature": 0.0,
  "top_p": 0.9,
  "max_tokens": 4000,
  "timeout": 60,
  "ocr_gpu_enabled": true,
  "ocr_gpu_id": 0,
  "ocr_gpu_mem": 800
}
```

## ✅ 完整部署脚本

### `deploy_windows.bat`

```batch
@echo off
echo ========================================
echo PaddleOCR Windows GPU 部署脚本
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Python未安装或未添加到PATH
    pause
    exit /b 1
)

echo [1/6] 创建虚拟环境...
python -m venv venv
call venv\Scripts\activate

echo [2/6] 升级pip...
python -m pip install --upgrade pip

echo [3/6] 安装PaddlePaddle GPU版本...
python -m pip install paddlepaddle-gpu==3.0.0b1 -i https://mirror.baidu.com/pypi/simple

echo [4/6] 安装PaddleOCR...
pip install paddleocr

echo [5/6] 安装项目依赖...
pip install -r requirements.txt
pip install pymupdf requests jinja2

echo [6/6] 验证GPU支持...
python -c "import paddle; print(f'CUDA可用: {paddle.device.is_compiled_with_cuda()}')"

echo.
echo ========================================
echo 部署完成！
echo ========================================
echo.
echo 下一步：
echo 1. 配置CUDA环境变量（如果需要）
echo 2. 运行测试: python -m src.main.py -m flow
echo.
pause
```

## 🎉 总结

### 关键要点

1. ✅ **不要安装patchelf**：Windows不需要
2. ✅ **安装GPU版本的PaddlePaddle**：不是CPU版本
3. ✅ **正确安装CUDA和cuDNN**：匹配PaddlePaddle版本
4. ✅ **验证GPU可用性**：运行测试脚本
5. ✅ **配置TCC模式**：确保Tesla卡使用TCC

### 性能预期

- **CPU**: 2-3秒/页
- **GPU (TCC)**: 0.3-0.5秒/页
- **加速比**: 6-10倍

### 下一步

1. 按照上述步骤完成部署
2. 运行测试验证GPU工作
3. 根据实际性能调整参数
4. 开始使用AI试卷生成工作流

---

**祝部署顺利！** 🚀

如遇问题，请检查：
1. `nvidia-smi` 输出
2. `python -c "import paddle; print(paddle.device.cuda.get_device_name(0))"`
3. PaddleOCR日志输出
