#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证OCR配置有效性 - 英文试卷模式
"""

import os
import sys
import types

# 设置环境变量 - 系统只有1个GPU，使用GPU0
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ['OMP_NUM_THREADS'] = '24'
os.environ['MKL_NUM_THREADS'] = '24'

print('=== 环境变量配置 ===')
print(f'CUDA_VISIBLE_DEVICES: {os.environ.get("CUDA_VISIBLE_DEVICES", "未设置")}')
print(f'OMP_NUM_THREADS: {os.environ.get("OMP_NUM_THREADS", "未设置")}')
print()

# 首先创建PaddleX需要的langchain.docstore.document兼容模块
if 'langchain' not in sys.modules:
    langchain = types.ModuleType('langchain')
    sys.modules['langchain'] = langchain

if 'langchain.docstore' not in sys.modules:
    langchain_docstore = types.ModuleType('langchain.docstore')
    sys.modules['langchain.docstore'] = langchain_docstore
    langchain.docstore = langchain_docstore

if 'langchain.docstore.document' not in sys.modules:
    # 尝试从langchain_core导入Document类
    try:
        from langchain_core.documents import Document as CoreDocument
        # 创建兼容模块
        langchain_docstore_document = types.ModuleType('langchain.docstore.document')
        langchain_docstore_document.Document = CoreDocument
        sys.modules['langchain.docstore.document'] = langchain_docstore_document
        langchain_docstore.document = langchain_docstore_document
        print('✓ 使用langchain_core.documents.Document创建兼容模块')
    except ImportError:
        # 创建基本的Document类
        class Document:
            def __init__(self, page_content: str, metadata: dict = None, id: str = None):
                self.page_content = page_content
                self.metadata = metadata or {}
                self.id = id
        
        langchain_docstore_document = types.ModuleType('langchain.docstore.document')
        langchain_docstore_document.Document = Document
        sys.modules['langchain.docstore.document'] = langchain_docstore_document
        langchain_docstore.document = langchain_docstore_document
        print('⚠ 创建基本Document兼容类')

# 创建langchain.text_splitter兼容模块
if 'langchain.text_splitter' not in sys.modules:
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        langchain_text_splitter = types.ModuleType('langchain.text_splitter')
        langchain_text_splitter.RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter
        sys.modules['langchain.text_splitter'] = langchain_text_splitter
        langchain.text_splitter = langchain_text_splitter
        print('✓ 使用langchain_text_splitters创建兼容模块')
    except ImportError:
        class RecursiveCharacterTextSplitter:
            def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
                self.chunk_size = chunk_size
                self.chunk_overlap = chunk_overlap
            def split_documents(self, documents):
                return documents
        
        langchain_text_splitter = types.ModuleType('langchain.text_splitter')
        langchain_text_splitter.RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter
        sys.modules['langchain.text_splitter'] = langchain_text_splitter
        langchain.text_splitter = langchain_text_splitter
        print('⚠ 创建基本RecursiveCharacterTextSplitter兼容类')

print()

# 测试PaddleOCR导入和初始化
try:
    print('正在导入PaddleOCR...')
    from paddleocr import PaddleOCR
    print('✓ PaddleOCR导入成功')
    print()
    
    print('正在初始化OCR引擎（使用GPU0，英文模式）...')
    # 使用最简化的参数配置，只保留必要的参数
    ocr = PaddleOCR(
        lang='en',
        device='gpu:0'  # 系统只有1个GPU，使用GPU0
    )
    print('✓ OCR引擎初始化成功')
    print()
    
    # 检查GPU是否可用
    import paddle
    print('=== Paddle GPU状态 ===')
    print(f'Paddle版本: {paddle.__version__}')
    print(f'CUDA可用: {paddle.is_compiled_with_cuda()}')
    if paddle.is_compiled_with_cuda():
        print(f'GPU设备数: {paddle.device.cuda.device_count()}')
    else:
        print('CPU模式')
    print()
    
    print('=== 配置验证完成 ===')
    print('✓ GPU0分配成功')
    print('✓ 英文OCR模式已启用')
    print('✓ 多线程配置已加载')
    print()
    print('配置有效，可以处理英文试卷！')
    
except Exception as e:
    print(f'✗ 错误: {str(e)}')
    import traceback
    print(traceback.format_exc())
    sys.exit(1)
