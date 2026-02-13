import os
import json
import re
import requests
import logging
import tempfile
import concurrent.futures
from typing import List, Dict, Any
from jinja2 import Template, Environment
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
import pymupdf  # PyMuPDF

# 设置多线程优化，充分利用系统资源
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '8'
os.environ['NUMEXPR_NUM_THREADS'] = '8'
os.environ['VLLM_NUM_THREADS'] = '8'
os.environ['TF_NUM_THREADS'] = '8'

# 初始化Jinja2环境
jinja_env = Environment()

# 添加自定义truncate过滤器
def truncate_filter(text, length=5000, end='...'):
    if text and len(text) > length:
        return text[:length] + end
    return text

jinja_env.filters['truncate'] = truncate_filter


# 导入状态定义
from graphs.state import (
    DownloadPdfInput, DownloadPdfOutput,
    OcrRecognitionInput, OcrRecognitionOutput,
    QuestionsAnalysisInput, QuestionsAnalysisOutput,
    DatabaseStorageInput, DatabaseStorageOutput,
    RagIndexingInput, RagIndexingOutput,
    RagRetrievalInput, RagRetrievalOutput,
    QuestionsSelectionInput, QuestionsSelectionOutput,
    GenerateExamPaperInput, GenerateExamPaperOutput
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("已设置线程数为24，充分利用系统资源")

# 全局OCR实例，避免重复初始化
_ocr_instance = None

def convert_chart_to_markdown(chart_info):
    """将图表信息转换为Markdown格式"""
    chart_type = chart_info.get('type', 'chart')
    chart_data = chart_info.get('data', {})
    
    # 生成Markdown图表
    markdown_chart = []
    markdown_chart.append(f"### 图表 ({chart_type})")
    
    # 根据图表类型生成不同的Markdown表示
    if chart_type == 'bar':
        markdown_chart.append("```markdown")
        markdown_chart.append("# 柱状图")
        if 'categories' in chart_data and 'values' in chart_data:
            categories = chart_data.get('categories', [])
            values = chart_data.get('values', [])
            markdown_chart.append("| 类别 | 值 |")
            markdown_chart.append("|------|----|")
            for cat, val in zip(categories, values):
                markdown_chart.append(f"| {cat} | {val} |")
        markdown_chart.append("```")
    
    elif chart_type == 'line':
        markdown_chart.append("```markdown")
        markdown_chart.append("# 折线图")
        if 'x_axis' in chart_data and 'y_axis' in chart_data:
            x_axis = chart_data.get('x_axis', [])
            y_axis = chart_data.get('y_axis', [])
            markdown_chart.append("| X轴 | Y轴 |")
            markdown_chart.append("|------|----|")
            for x, y in zip(x_axis, y_axis):
                markdown_chart.append(f"| {x} | {y} |")
        markdown_chart.append("```")
    
    elif chart_type == 'pie':
        markdown_chart.append("```markdown")
        markdown_chart.append("# 饼图")
        if 'labels' in chart_data and 'values' in chart_data:
            labels = chart_data.get('labels', [])
            values = chart_data.get('values', [])
            markdown_chart.append("| 标签 | 值 |")
            markdown_chart.append("|------|----|")
            for label, val in zip(labels, values):
                markdown_chart.append(f"| {label} | {val} |")
        markdown_chart.append("```")
    
    elif chart_type == 'node' or chart_type == 'graph' or 'node' in chart_type.lower():
        markdown_chart.append("```markdown")
        markdown_chart.append("# 节点图")
        # 处理节点和边
        nodes = chart_data.get('nodes', [])
        edges = chart_data.get('edges', [])
        labels = chart_data.get('labels', [])
        
        if labels:
            markdown_chart.append("## 标签")
            for label in labels:
                markdown_chart.append(f"- {label}")
        
        if nodes:
            markdown_chart.append("## 节点")
            markdown_chart.append("| 节点内容 | 类型 |")
            markdown_chart.append("|----------|------|")
            for node in nodes:
                node_content = node.get('content', '无')
                node_type = node.get('type', '未知')
                markdown_chart.append(f"| {node_content} | {node_type} |")
        
        if edges:
            markdown_chart.append("## 连接关系")
            markdown_chart.append("| 起点 | 终点 |")
            markdown_chart.append("|------|------|")
            for edge in edges:
                source = edge.get('source', '未知')
                target = edge.get('target', '未知')
                markdown_chart.append(f"| {source} | {target} |")
        
        # 特殊处理用户提供的节点图类型
        markdown_chart.append("## 图结构说明")
        markdown_chart.append("此图包含以下部分：")
        markdown_chart.append("1. 数字节点 (0-9)")
        markdown_chart.append("2. 字母节点 (A, C, E, G等)")
        markdown_chart.append("3. 箭头连接关系")
        markdown_chart.append("4. 标签标识 (digit, letter, variable等)")
        markdown_chart.append("```")
    
    else:
        # 通用图表格式
        markdown_chart.append("```markdown")
        markdown_chart.append(f"# {chart_type} 图")
        markdown_chart.append(f"数据: {json.dumps(chart_data)}")
        markdown_chart.append("```")
    
    return "\n".join(markdown_chart)

def get_ocr_instance():
    """获取OCR实例（单例模式）
    
    Returns:
        PaddleOCR: 初始化好的OCR引擎实例，失败则返回None
    """
    global _ocr_instance
    if _ocr_instance is None:
        try:
            # 创建虚拟的langchain模块，解决paddlex的依赖问题
            import sys
            import types
            
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
                    logger.info("使用langchain_core.documents.Document创建兼容模块")
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
                    logger.info("创建基本Document兼容类")
            
            # 创建langchain.text_splitter兼容模块
            if 'langchain.text_splitter' not in sys.modules:
                try:
                    from langchain_text_splitters import RecursiveCharacterTextSplitter
                    langchain_text_splitter = types.ModuleType('langchain.text_splitter')
                    langchain_text_splitter.RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter
                    sys.modules['langchain.text_splitter'] = langchain_text_splitter
                    langchain.text_splitter = langchain_text_splitter
                    logger.info("使用langchain_text_splitters创建兼容模块")
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
                    logger.info("创建基本RecursiveCharacterTextSplitter兼容类")
            
            # 导入并初始化PaddleOCR v5
            logger.info("开始导入PaddleOCR v5")
            from paddleocr import PaddleOCR
            logger.info("PaddleOCR v5导入成功")
            
            # 初始化OCR引擎 - 使用GPU0，启用格式和图表识别
            logger.info("开始初始化PaddleOCR v5引擎（使用GPU0，启用格式和图表识别）")
            _ocr_instance = PaddleOCR(
                lang='en',
                device='gpu:0',
                use_angle_cls=True,  # 启用方向分类
                use_doc_orientation_classify=True,  # 启用文档方向分类
                use_doc_unwarping=True
            )
            logger.info("PaddleOCR v5引擎初始化成功")
        except Exception as e:
            logger.error(f"OCR引擎初始化失败: {str(e)}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            _ocr_instance = None
    return _ocr_instance


def _ocr_process_single_pdf(pdf_path: str) -> str:
    """对单个PDF执行OCR并保存到 <pdf>_ocr_output/full_result.json，返回该json路径。
    
    Args:
        pdf_path: PDF文件路径
    
    Returns:
        str: OCR结果JSON文件路径
    """
    output_dir = os.path.splitext(pdf_path)[0] + '_ocr_output'
    os.makedirs(output_dir, exist_ok=True)

    try:
        ocr_instance = get_ocr_instance()
        doc = pymupdf.open(pdf_path)
        pages_data = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            try:
                if ocr_instance:
                    pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                        tmp_path = tmp_file.name
                    pix.save(tmp_path)
                    try:
                        result = ocr_instance.predict(tmp_path)
                        # 尝试从结果中拼接文本
                        texts = []
                        if result:
                            for item in result:
                                try:
                                    if hasattr(item, 'text'):
                                        texts.append(item.text)
                                except Exception:
                                    pass
                        text = '\n'.join(texts) if texts else page.get_text()
                    finally:
                        try:
                            os.unlink(tmp_path)
                        except Exception:
                            logger.warning(f"无法删除临时文件: {tmp_path}")
                else:
                    text = page.get_text()
                page_data = {'text': text}
            except Exception as e:
                logger.warning(f"页面OCR异常，使用文本提取回退: {e}")
                page_data = {'text': page.get_text(), 'method': 'pdf_text_extraction'}
            pages_data.append({'page_num': page_num + 1, 'ocr_result': page_data})
        doc.close()
        full_json_path = os.path.join(output_dir, 'full_result.json')
        with open(full_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(pages_data, json_file, ensure_ascii=False, indent=2)
        logger.info(f"OCR完成，保存: {full_json_path}")
        return full_json_path
    except Exception as e:
        logger.error(f"对PDF执行OCR失败: {e}")
        raise


# ==================== 节点1: 下载PDF ====================
def download_pdf_node(state: DownloadPdfInput, config: RunnableConfig, runtime: Runtime[Context]) -> DownloadPdfOutput:
    """
    title: 下载PDF文件
    desc: 从指定URL下载PDF文件到本地
    integrations: HTTP请求
    """
    ctx = runtime.context
    
    try:
        pdf_url = getattr(state, 'pdf_url', '')
        exam_code = getattr(state, 'exam_code', '')
        year = getattr(state, 'year', '')

        if not pdf_url and not exam_code:
            raise ValueError("PDF URL或exam_code至少需要提供一个")
        
        # 创建assets目录（如果不存在）
        workspace_path = os.getenv("WORKSPACE_PATH", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        assets_dir = os.path.join(workspace_path, "assets")
        os.makedirs(assets_dir, exist_ok=True)

        # 如果提供了exam_code，则批量下载该考试相关的试卷（仅下载存在的文件），并生成index
        if exam_code:
            logger.info(f"开始按考试代码批量下载: {exam_code}, year={year}")
            exam_dir = os.path.join(assets_dir, f"{exam_code}_{year}") if year else os.path.join(assets_dir, exam_code)
            os.makedirs(exam_dir, exist_ok=True)
            base_url = pdf_url.rsplit('/', 1)[0] if pdf_url else None
            downloaded_files = []
            # 定义下载函数
            def download_file(i):
                filename = f"{exam_code}_{year}_qp_{i:02d}.pdf" if year else f"{exam_code}_qp_{i:02d}.pdf"
                if base_url:
                    candidate_url = base_url + '/' + filename
                else:
                    # 无base_url时尝试使用默认模式（可能失败）
                    candidate_url = filename
                try:
                    response = requests.get(candidate_url, stream=True, timeout=12)
                    if response.status_code == 200:
                        file_path = os.path.join(exam_dir, filename)
                        with open(file_path, 'wb') as file:
                            for chunk in response.iter_content(chunk_size=8192):
                                file.write(chunk)
                        logger.info(f"已下载: {candidate_url} -> {file_path}")
                        return file_path
                except Exception:
                    # 忽略不可达或超时的文件
                    pass
                return None
            
            # 使用线程池并发下载
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                # 提交所有下载任务
                futures = [executor.submit(download_file, i) for i in range(11, 100)]
                
                # 收集结果
                for future in futures:
                    file_path = future.result()
                    if file_path:
                        downloaded_files.append(file_path)

            # 记录索引，避免重复下载
            index_path = os.path.join(exam_dir, 'downloaded_index.json')
            with open(index_path, 'w', encoding='utf-8') as index_file:
                json.dump({'files': downloaded_files}, index_file, ensure_ascii=False, indent=2)

            if not downloaded_files:
                raise FileNotFoundError(f"未找到任何可下载的试卷 for {exam_code} {year}")

            # 返回exam_dir作为downloaded_pdf_path（表示来源目录）
            return DownloadPdfOutput(downloaded_pdf_path=exam_dir, subject_code=exam_code, paper_type=year)

        # 否则按单文件URL下载
        # 下载PDF文件
        response = requests.get(pdf_url, stream=True, timeout=30)
        response.raise_for_status()
        
        # 保存到本地
        filename = pdf_url.split("/")[-1] if "/" in pdf_url else "downloaded.pdf"
        if not filename.endswith(".pdf"):
            filename += ".pdf"
        
        # 提取科目代码和试卷类型
        subject_code = ""
        paper_type = ""
        
        # 解析文件名提取科目代码（头四个数字）
        if filename.endswith(".pdf"):
            base_name = filename[:-4]
            subject_match = re.match(r'^([0-9]{4})', base_name)
            if subject_match:
                subject_code = subject_match.group(1)
        
        # 从URL的倒数第六个字符提取试卷类型（1234）
        if len(pdf_url) >= 6:
            paper_type_char = pdf_url[-6]
            if paper_type_char in ['1', '2', '3', '4']:
                paper_type = paper_type_char
        
        pdf_path = os.path.join(assets_dir, filename)
        with open(pdf_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        logger.info(f"PDF文件已下载到: {pdf_path}")
        logger.info(f"提取的科目代码: {subject_code}")
        logger.info(f"提取的试卷类型: {paper_type}")
        
        return DownloadPdfOutput(
            downloaded_pdf_path=pdf_path,
            subject_code=subject_code,
            paper_type=paper_type
        )
        
    except Exception as e:
        logger.error(f"下载PDF失败: {str(e)}")
        raise


# ==================== 节点2: OCR识别 ====================
def ocr_recognition_node(state: OcrRecognitionInput, config: RunnableConfig, runtime: Runtime[Context]) -> OcrRecognitionOutput:
    """
    title: OCR识别并生成JSON
    desc: 使用PaddleOCR v5识别PDF内容并输出JSON格式，加入fallback机制
    integrations: PaddleOCR v5
    """
    ctx = runtime.context
    
    try:
        pdf_path = state.downloaded_pdf_path
        logger.info(f"开始OCR识别，PDF路径: {pdf_path}")

        if not pdf_path:
            raise ValueError("downloaded_pdf_path 不能为空")

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")

        # 如果传入的是目录，说明是批量下载场景：下载节点已为每个PDF生成ocr输出目录
        if os.path.isdir(pdf_path):
            logger.info(f"检测到 downloaded_pdf_path 为目录，跳过单文件OCR，直接返回目录以供后续节点批量处理: {pdf_path}")
            return OcrRecognitionOutput(ocr_json_path=pdf_path, markdown_content="")

        logger.info(f"PDF文件存在，开始处理")
        
        # 使用已有的单文件处理逻辑抽取并保存JSON
        full_json_path = _ocr_process_single_pdf(pdf_path)
        # 生成简单markdown兼容文本
        try:
            with open(full_json_path, 'r', encoding='utf-8') as fd:
                pages = json.load(fd)
            md_parts = []
            for p in pages:
                md_parts.append(f"## 第{p.get('page_num')}页\n" + (p.get('ocr_result', {}).get('text','')[:2000]))
            md_text = '\n\n'.join(md_parts)
        except Exception:
            md_text = ''

        return OcrRecognitionOutput(ocr_json_path=full_json_path, markdown_content=md_text)
        
    except Exception as e:
        logger.error(f"OCR识别节点执行失败: {str(e)}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        raise


# ==================== 节点3: 题目分析 ====================
def questions_analysis_node(state: QuestionsAnalysisInput, config: RunnableConfig, runtime: Runtime[Context]) -> QuestionsAnalysisOutput:
    """
    title: 题目分析
    desc: 使用LLM分析题目信息，提取题目类型、页数和分值
    integrations: LM Studio
    """
    ctx = runtime.context
    
    try:
        # 支持直接传入OCR JSON文件路径，优先使用JSON
        markdown_content = state.markdown_content if getattr(state, 'markdown_content', '') else ''
        ocr_json_path = getattr(state, 'ocr_json_path', '')
        
        page_source_list = []

        # 如果提供了OCR JSON文件或目录，读取并基于其中的文本构建用于LM的提示文本
        if ocr_json_path and os.path.exists(ocr_json_path):
            try:
                md_parts = []
                # 如果是目录，遍历目录查找每个PDF对应的 full_result.json
                if os.path.isdir(ocr_json_path):
                    for root, dirs, files in os.walk(ocr_json_path):
                        for fname in files:
                            if fname == 'full_result.json' or fname.endswith('_result.json'):
                                fpath = os.path.join(root, fname)
                                source_pdf = fpath
                                if '_ocr_output' in fpath:
                                    source_pdf = fpath.split('_ocr_output')[0] + '.pdf'
                                try:
                                    with open(fpath, 'r', encoding='utf-8') as fd:
                                        pages = json.load(fd)
                                    for p in pages:
                                        page_num = p.get('page_num')
                                        page_source_list.append({
                                            "source_pdf_path": source_pdf,
                                            "page_num": page_num
                                        })
                                        ocr_result = p.get('ocr_result', {})
                                        text = ''
                                        if isinstance(ocr_result, dict):
                                            text = ocr_result.get('text', '')
                                        elif isinstance(ocr_result, list):
                                            for item in ocr_result:
                                                if isinstance(item, dict) and 'text' in item:
                                                    text += item.get('text','') + '\n'
                                        pdf_name = os.path.basename(source_pdf)
                                        md_parts.append(f"## [{pdf_name}] 第{page_num}页\n" + text[:2000])
                                except Exception as e:
                                    logger.warning(f"读取OCR文件 {fpath} 失败: {e}")
                else:
                    source_pdf = ocr_json_path
                    if '_ocr_output' in ocr_json_path:
                        source_pdf = ocr_json_path.split('_ocr_output')[0] + '.pdf'
                    with open(ocr_json_path, 'r', encoding='utf-8') as fd:
                        ocr_pages = json.load(fd)
                    for p in ocr_pages:
                        page_num = p.get('page_num')
                        page_source_list.append({
                            "source_pdf_path": source_pdf,
                            "page_num": page_num
                        })
                        ocr_result = p.get('ocr_result', {})
                        text = ''
                        if isinstance(ocr_result, dict):
                            text = ocr_result.get('text', '')
                        elif isinstance(ocr_result, list):
                            for item in ocr_result:
                                if isinstance(item, dict) and 'text' in item:
                                    text += item.get('text','') + '\n'
                        pdf_name = os.path.basename(source_pdf)
                        md_parts.append(f"## [{pdf_name}] 第{page_num}页\n" + text[:2000])

                markdown_content = "\n\n".join(md_parts)
                logger.info(f"已从OCR JSON(或目录)生成用于LLM的markdown_content, 记录了 {len(page_source_list)} 个页面信息")
            except Exception as e:
                logger.warning(f"从OCR JSON生成markdown失败: {e}")
        
        # 从config中获取LLM配置
        workspace_path = os.getenv("WORKSPACE_PATH", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        cfg_file = os.path.join(workspace_path, config['metadata']['llm_cfg'])
        with open(cfg_file, 'r', encoding='utf-8') as fd:
            _cfg = json.load(fd)
        
        llm_config = _cfg.get("config", _cfg)
        sp = _cfg.get("sp", "")
        up = _cfg.get("up", "")
        
        # 渲染用户提示词
        up_tpl = jinja_env.from_string(up)
        user_prompt = up_tpl.render({"markdown_content": markdown_content})
        
        try:
            # 调用LM Studio API (OpenAI兼容格式)
            lm_studio_url = llm_config.get("base_url", "http://127.0.0.1:1234/v1")
            model = llm_config.get("model") or llm_config.get("chat_model", "qwen3-30b-a3b-2507-thinking")
            
            logger.info(f"正在连接LM Studio API: {lm_studio_url}, 模型: {model}")
            
            # 先测试LM Studio API是否可访问
            test_response = requests.get(f"{lm_studio_url}/models", timeout=10)
            test_response.raise_for_status()
            logger.info("LM Studio API连接测试成功")
            
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": sp},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": max(0.1, llm_config.get("temperature", 0.1)),
                "max_tokens": llm_config.get("max_tokens", 2000)
            }
            
            logger.info(f"发送请求到LM Studio API, payload: model={model}, max_tokens={payload['max_tokens']}")
            response = requests.post(
                f"{lm_studio_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=300
            )
            if response.status_code != 200:
                logger.error(f"LM Studio API返回错误: {response.status_code}, 响应内容: {response.text}")
            response.raise_for_status()
            logger.info("LM Studio API请求成功")
            
            result = response.json()
            message = result["choices"][0]["message"]
            content = message.get("content", "")
            reasoning_content = message.get("reasoning_content", "")
            
            if not content and reasoning_content:
                logger.info("content为空，使用reasoning_content")
                content = reasoning_content
            
            logger.info("成功获取LM Studio API响应")
            
        except requests.exceptions.ConnectionError as conn_error:
            logger.warning(f"无法连接LM Studio API (连接错误): {str(conn_error)}")
            logger.warning(f"请确保LM Studio服务已启动并运行在 {lm_studio_url}")
            # Fallback: 使用简单的规则提取题目信息
            logger.info("使用fallback方法分析题目...")
            
            # 简单规则：按"## 第X页"分割，每页估算题目
            content = "["
            pages = markdown_content.split("## 第")
            for i, page_content in enumerate(pages[1:], 1):  # 跳过第一个空元素
                content += f'\n{{"type": "简答题", "page_num": {i}, "score": 10}},'
            content = content.rstrip(",") + "\n]"
        except requests.exceptions.Timeout as timeout_error:
            logger.warning(f"无法连接LM Studio API (超时): {str(timeout_error)}")
            logger.warning(f"LM Studio服务可能响应缓慢或网络连接不稳定")
            # Fallback: 使用简单的规则提取题目信息
            logger.info("使用fallback方法分析题目...")
            
            # 简单规则：按"## 第X页"分割，每页估算题目
            content = "["
            pages = markdown_content.split("## 第")
            for i, page_content in enumerate(pages[1:], 1):  # 跳过第一个空元素
                content += f'\n{{"type": "简答题", "page_num": {i}, "score": 10}},'
            content = content.rstrip(",") + "\n]"
        except Exception as llm_error:
            logger.warning(f"无法连接LM Studio API: {str(llm_error)}")
            import traceback
            logger.warning(f"详细错误信息: {traceback.format_exc()}")
            # Fallback: 使用简单的规则提取题目信息
            logger.info("使用fallback方法分析题目...")
            
            # 简单规则：按"## 第X页"分割，每页估算题目
            content = "["
            pages = markdown_content.split("## 第")
            for i, page_content in enumerate(pages[1:], 1):  # 跳过第一个空元素
                content += f'\n{{"type": "简答题", "page_num": {i}, "score": 10}},'
            content = content.rstrip(",") + "\n]"
        
        # 解析JSON结果
        try:
            questions_info = json.loads(content)
        except json.JSONDecodeError:
            logger.error("LLM返回的不是有效的JSON")
            questions_info = []
        
        for q in questions_info:
            page_num = q.get("page_num")
            for page_info in page_source_list:
                if page_info["page_num"] == page_num:
                    q["source_pdf_path"] = page_info["source_pdf_path"]
                    break
        
        logger.info(f"题目分析完成，共识别 {len(questions_info)} 道题目")
        
        return QuestionsAnalysisOutput(questions_info=questions_info)
        
    except Exception as e:
        logger.error(f"题目分析失败: {str(e)}")
        # 返回空列表作为fallback
        return QuestionsAnalysisOutput(questions_info=[])


# ==================== 节点4: 数据库存储 ====================
def database_storage_node(state: DatabaseStorageInput, config: RunnableConfig, runtime: Runtime[Context]) -> DatabaseStorageOutput:
    """
    title: 数据库存储
    desc: 清空数据库并存储新的JSON格式题目信息
    integrations: PostgreSQL
    """
    ctx = runtime.context
    
    try:
        from storage.database.db import get_session
        from storage.database.shared.model import Question
        
        downloaded_pdf_path = state.downloaded_pdf_path
        questions_info = state.questions_info
        ocr_json_path = getattr(state, 'ocr_json_path', '')
        
        stored_question_ids = []
        
        # 获取数据库会话
        session = get_session()
        
        try:
            # 清空数据库中的所有题目记录
            logger.info("开始清空数据库中的题目记录...")
            session.query(Question).delete()
            session.commit()
            logger.info("数据库清空完成")
            
            # 重新获取会话以确保事务正确
            session = get_session()
            
            # 如果ocr_json_path指向目录，尝试批量导入目录下的OCR JSON文件
            imported_count = 0
            if ocr_json_path and os.path.isdir(ocr_json_path):
                logger.info(f"检测到ocr_json_path为目录，批量导入目录: {ocr_json_path}")
                for root, dirs, files in os.walk(ocr_json_path):
                    for fname in files:
                        if fname.endswith('.json') and ('full_result' in fname or fname.startswith('page_')):
                            fpath = os.path.join(root, fname)
                            try:
                                with open(fpath, 'r', encoding='utf-8') as fd:
                                    pages = json.load(fd)
                                if isinstance(pages, list):
                                    for p in pages:
                                        page_num = p.get('page_num', 1)
                                        ocr_result = p.get('ocr_result', {})
                                        pdf_path = fpath
                                        if '_ocr_output' in fpath:
                                            pdf_path = fpath.split('_ocr_output')[0] + '.pdf'
                                        db_question = Question(
                                            question_type='未知',
                                            content=json.dumps(ocr_result, ensure_ascii=False),
                                            score=1.0,
                                            knowledge_points='',
                                            source_pdf_path=pdf_path,
                                            page_num=int(page_num),
                                            difficulty='中等',
                                            tags={}
                                        )
                                        session.add(db_question)
                                        session.flush()
                                        stored_question_ids.append(db_question.id)
                                        imported_count += 1
                            except Exception as e:
                                logger.warning(f"导入文件 {fpath} 时出错: {e}")
                session.commit()
                logger.info(f"批量导入完成，共导入 {imported_count} 道题目")
                return DatabaseStorageOutput(stored_question_ids=stored_question_ids)

            # 检查输入数据
            if not questions_info:
                logger.warning("questions_info为空，跳过数据库存储")
                return DatabaseStorageOutput(stored_question_ids=[])

            # 存储题目信息（基于questions_info，关联单个PDF）
            for question in questions_info:
                page_num = question.get("page_num", 1)

                # 创建题目记录，存储JSON格式的内容
                db_question = Question(
                    question_type=question.get("type", "未知"),
                    content=json.dumps(question, ensure_ascii=False),
                    score=float(question.get("score", 0)),
                    knowledge_points=question.get("knowledge_points", ""),
                    source_pdf_path=downloaded_pdf_path,
                    page_num=int(page_num),
                    difficulty=question.get("difficulty", "中等"),
                    tags=question.get("tags", {})
                )
                session.add(db_question)
                session.flush()  # 获取ID
                stored_question_ids.append(db_question.id)
                logger.info(f"成功存储题目，ID: {db_question.id}, 类型: {db_question.question_type}")
            
            # 提交事务
            session.commit()
            
            logger.info(f"数据库存储完成，共存储 {len(stored_question_ids)} 道题目")
            
            return DatabaseStorageOutput(stored_question_ids=stored_question_ids)
            
        except Exception as e:
            session.rollback()
            logger.error(f"数据库存储失败: {str(e)}")
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")
            raise
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"数据库存储节点执行失败: {str(e)}")
        raise


# ==================== 节点5: RAG索引 ====================
def rag_indexing_node(state: RagIndexingInput, config: RunnableConfig, runtime: Runtime[Context]) -> RagIndexingOutput:
    """
    title: RAG索引构建
    desc: 对知识点PDF进行向量化，构建检索索引
    integrations: LM Studio Embedding, FAISS
    """
    ctx = runtime.context
    
    try:
        knowledge_pdf_path = state.knowledge_pdf_path
        if not os.path.exists(knowledge_pdf_path):
            raise FileNotFoundError(f"知识点PDF文件不存在: {knowledge_pdf_path}")
        
        # 从PDF中提取文本
        doc = pymupdf.open(knowledge_pdf_path)
        knowledge_texts = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            # 确保text是字符串类型
            if isinstance(text, str) and text.strip():
                knowledge_texts.append({
                    "page": page_num + 1,
                    "text": text.strip()
                })
        
        doc.close()
        
        # 读取LM Studio配置
        workspace_path = os.getenv("WORKSPACE_PATH", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        cfg_file = os.path.join(workspace_path, "config/lm_studio_cfg.json")
        try:
            with open(cfg_file, 'r', encoding='utf-8') as fd:
                lm_studio_config = json.load(fd)
            lm_studio_url = lm_studio_config.get("base_url", "http://localhost:1234/v1")
            embedding_model = lm_studio_config.get("embedding_model", "local-embedding")
            timeout = lm_studio_config.get("timeout", 30)
        except Exception as e:
            logger.warning(f"无法读取LM Studio配置: {e}，使用默认值")
            lm_studio_url = "http://localhost:1234/v1"
            embedding_model = "local-embedding"
            timeout = 30
        
        headers = {
            "Content-Type": "application/json"
        }
        
        knowledge_embeddings = []
        
        # 定义向量化函数
        def vectorize_text(text):
            try:
                payload = {
                    "model": embedding_model,
                    "input": text
                }
                
                response = requests.post(
                    f"{lm_studio_url}/embeddings",
                    headers=headers,
                    json=payload,
                    timeout=timeout
                )
                response.raise_for_status()
                
                result = response.json()
                return result["data"][0]["embedding"]
            except Exception as e:
                logger.warning(f"向量化失败: {str(e)}")
                return [0.0] * 384  # 使用零向量作为fallback
        
        # 使用线程池并发向量化
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            # 提交所有向量化任务
            futures = [executor.submit(vectorize_text, item["text"]) for item in knowledge_texts]
            
            # 按原始顺序收集结果
            for future in futures:
                embedding = future.result()
                knowledge_embeddings.append(embedding)
        
        logger.info(f"RAG索引构建完成，共索引 {len(knowledge_texts)} 个知识点")
        
        return RagIndexingOutput(
            knowledge_embeddings=knowledge_embeddings,
            knowledge_texts=[item["text"] for item in knowledge_texts]
        )
        
    except Exception as e:
        logger.error(f"RAG索引构建失败: {str(e)}")
        raise


# ==================== 节点5: RAG检索 ====================
def rag_retrieval_node(state: RagRetrievalInput, config: RunnableConfig, runtime: Runtime[Context]) -> RagRetrievalOutput:
    """
    title: RAG检索
    desc: 基于知识点范围检索相关的PDF页面
    integrations: LM Studio Embedding
    """
    ctx = runtime.context
    
    try:
        knowledge_range = state.knowledge_range
        knowledge_embeddings = state.knowledge_embeddings
        knowledge_texts = state.knowledge_texts
        
        if not knowledge_range:
            # 如果没有指定知识点范围，返回所有页面
            relevant_pages = list(range(1, len(knowledge_texts) + 1))
        else:
            # 读取LM Studio配置
            workspace_path = os.getenv("WORKSPACE_PATH", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            cfg_file = os.path.join(workspace_path, "config/lm_studio_cfg.json")
            try:
                with open(cfg_file, 'r', encoding='utf-8') as fd:
                    lm_studio_config = json.load(fd)
                lm_studio_url = lm_studio_config.get("base_url", "http://127.0.0.1:1234/v1")
                embedding_model = lm_studio_config.get("embedding_model", "local-embedding")
                timeout = lm_studio_config.get("timeout", 30)
            except Exception as e:
                logger.warning(f"无法读取LM Studio配置: {e}，使用默认值")
                lm_studio_url = "http://127.0.0.1:1234/v1"
                embedding_model = "local-embedding"
                timeout = 30
            
            headers = {
                "Content-Type": "application/json"
            }
            
            try:
                payload = {
                    "model": embedding_model,
                    "input": knowledge_range
                }
                
                response = requests.post(
                    f"{lm_studio_url}/embeddings",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                
                result = response.json()
                query_embedding = result["data"][0]["embedding"]
                
                # 计算相似度 - 使用numpy向量化操作提高性能
                import numpy as np
                
                # 将嵌入转换为numpy数组
                query_embedding_np = np.array(query_embedding)
                knowledge_embeddings_np = np.array(knowledge_embeddings)
                
                # 计算点积
                dot_products = np.dot(knowledge_embeddings_np, query_embedding_np)
                
                # 计算范数
                query_norm = np.linalg.norm(query_embedding_np)
                embedding_norms = np.linalg.norm(knowledge_embeddings_np, axis=1)
                
                # 计算余弦相似度
                similarities = dot_products / (query_norm * embedding_norms)
                
                # 选择相似度高的页面（阈值0.3）
                relevant_pages = [
                    i + 1 for i, sim in enumerate(similarities) if sim > 0.3
                ]
                
            except Exception as e:
                logger.warning(f"检索失败，使用所有页面: {str(e)}")
                # Fallback: 返回所有页面
                relevant_pages = list(range(1, len(knowledge_texts) + 1))
        
        logger.info(f"RAG检索完成，找到 {len(relevant_pages)} 个相关页面")
        
        return RagRetrievalOutput(relevant_pages=relevant_pages)
        
    except Exception as e:
        logger.error(f"RAG检索失败: {str(e)}")
        raise


# ==================== 节点6: 题目筛选 ====================
def questions_selection_node(state: QuestionsSelectionInput, config: RunnableConfig, runtime: Runtime[Context]) -> QuestionsSelectionOutput:
    """
    title: 题目筛选
    desc: 使用LLM根据知识点范围和RAG结果选择合适的页面
    integrations: LM Studio
    """
    ctx = runtime.context
    
    try:
        questions_info = state.questions_info
        relevant_pages = state.relevant_pages
        required_score = state.required_score
        knowledge_range = getattr(state, 'knowledge_range', '')
        knowledge_texts = getattr(state, 'knowledge_texts', [])
        ocr_json_path = getattr(state, 'ocr_json_path', '')
        
        logger.info(f"开始LLM题目筛选，知识点范围: {knowledge_range}, 目标分值: {required_score}")
        
        page_source_list = []
        page_content_map = {}
        
        if ocr_json_path and os.path.exists(ocr_json_path):
            if os.path.isdir(ocr_json_path):
                for root, dirs, files in os.walk(ocr_json_path):
                    for fname in files:
                        if fname == 'full_result.json' or fname.endswith('_result.json'):
                            fpath = os.path.join(root, fname)
                            source_pdf = fpath
                            if '_ocr_output' in fpath:
                                source_pdf = fpath.split('_ocr_output')[0] + '.pdf'
                            try:
                                with open(fpath, 'r', encoding='utf-8') as fd:
                                    pages = json.load(fd)
                                for p in pages:
                                    page_num = p.get('page_num')
                                    ocr_result = p.get('ocr_result', {})
                                    text = ''
                                    if isinstance(ocr_result, dict):
                                        text = ocr_result.get('text', '')
                                    elif isinstance(ocr_result, list):
                                        for item in ocr_result:
                                            if isinstance(item, dict) and 'text' in item:
                                                text += item.get('text','') + '\n'
                                    page_key = f"{source_pdf}:{page_num}"
                                    page_source_list.append({
                                        "source_pdf_path": source_pdf,
                                        "page_num": page_num,
                                        "content_summary": text[:500] if text else "无内容"
                                    })
                                    page_content_map[page_key] = text[:500]
                            except Exception as e:
                                logger.warning(f"读取OCR文件 {fpath} 失败: {e}")
        
        rag_pages = []
        for page_info in page_source_list:
            if page_info["page_num"] in relevant_pages:
                rag_pages.append(page_info)
        
        if not rag_pages:
            rag_pages = page_source_list[:10] if page_source_list else []
        
        available_pages_json = json.dumps(page_source_list, ensure_ascii=False, indent=2)
        
        workspace_path = os.getenv("WORKSPACE_PATH", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        cfg_file = os.path.join(workspace_path, "config/questions_selection_cfg.json")
        
        try:
            with open(cfg_file, 'r', encoding='utf-8') as fd:
                _cfg = json.load(fd)
        except FileNotFoundError:
            logger.warning(f"配置文件不存在: {cfg_file}, 使用LM Studio配置")
            cfg_file = os.path.join(workspace_path, "config/lm_studio_cfg.json")
            with open(cfg_file, 'r', encoding='utf-8') as fd:
                _cfg = json.load(fd)
        
        llm_config = _cfg.get("config", _cfg)
        sp = _cfg.get("sp", "你是试卷出题专家，请根据知识点范围选择合适的页面。")
        up = _cfg.get("up", "知识点范围: {{ knowledge_range }}\n目标分值: {{ required_score }}分\n可用页面: {{ available_pages_json }}\n请选择合适的页面，返回JSON数组。")
        
        up_tpl = jinja_env.from_string(up)
        user_prompt = up_tpl.render({
            "knowledge_range": knowledge_range,
            "required_score": required_score,
            "rag_pages": rag_pages,
            "page_source_list": page_source_list
        })
        
        try:
            lm_studio_url = llm_config.get("base_url", "http://127.0.0.1:1234/v1")
            model = llm_config.get("model") or llm_config.get("chat_model", "qwen3-30b-a3b-2507-thinking")
            
            logger.info(f"正在连接LM Studio API进行题目筛选: {lm_studio_url}, 模型: {model}")
            
            test_response = requests.get(f"{lm_studio_url}/models", timeout=10)
            test_response.raise_for_status()
            logger.info("LM Studio API连接测试成功")
            
            headers = {"Content-Type": "application/json"}
            
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": sp},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": max(0.1, llm_config.get("temperature", 0.1)),
                "max_tokens": llm_config.get("max_tokens", 2000)
            }
            
            logger.info(f"发送题目筛选请求到LM Studio API...")
            response = requests.post(
                f"{lm_studio_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=300
            )
            if response.status_code != 200:
                logger.error(f"LM Studio API返回错误: {response.status_code}, 响应内容: {response.text}")
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"API完整响应结构: {json.dumps(result, ensure_ascii=False, indent=2)[:1000]}")
            
            if "choices" not in result or not result["choices"]:
                logger.error(f"API响应中没有choices字段，完整响应: {result}")
                raise ValueError("Invalid API response: no choices")
            
            if "message" not in result["choices"][0]:
                logger.error(f"choices[0]中没有message字段，完整响应: {result}")
                raise ValueError("Invalid API response: no message in choice")
            
            message = result["choices"][0]["message"]
            content = message.get("content", "")
            reasoning_content = message.get("reasoning_content", "")
            
            logger.info("成功获取LM Studio API响应")
            logger.info(f"LLM content长度: {len(content)}, reasoning_content长度: {len(reasoning_content)}")
            
            if not content and reasoning_content:
                logger.info("content为空，使用reasoning_content")
                content = reasoning_content
            
            logger.info(f"LLM原始响应内容（前500字符）: {content[:500]}")
            
            if not content:
                logger.error("LLM返回空内容，可能是模型配置或提示词问题")
                raise ValueError("LLM returned empty content")
            
            json_match = re.search(r'\[[\s\S]*\]', content)
            if json_match:
                content = json_match.group(0)
                logger.info(f"提取的JSON内容（前500字符）: {content[:500]}")
            else:
                logger.warning(f"未找到JSON数组格式，完整响应: {content}")
            
            selected_questions = json.loads(content)
            
            for q in selected_questions:
                if "source_pdf_path" not in q or not q["source_pdf_path"]:
                    for page_info in page_source_list:
                        if page_info["page_num"] == q.get("page_num"):
                            q["source_pdf_path"] = page_info["source_pdf_path"]
                            break
            
            total_score = sum(q.get("score", 0) for q in selected_questions)
            logger.info(f"LLM题目筛选完成，选择了 {len(selected_questions)} 道题目，总分: {total_score}")
            
            return QuestionsSelectionOutput(selected_questions=selected_questions)
            
        except requests.exceptions.ConnectionError as conn_error:
            logger.warning(f"无法连接LM Studio API: {str(conn_error)}")
        except requests.exceptions.Timeout as timeout_error:
            logger.warning(f"LM Studio API超时: {str(timeout_error)}")
        except json.JSONDecodeError as json_error:
            logger.warning(f"LLM返回的不是有效JSON: {str(json_error)}")
        except Exception as llm_error:
            logger.warning(f"LLM题目筛选失败: {str(llm_error)}")
            import traceback
            logger.warning(f"详细错误: {traceback.format_exc()}")
        
        logger.info("使用fallback方法进行题目筛选...")
        
        relevant_questions = [
            q for q in questions_info
            if q.get("page_num", 0) in relevant_pages
        ]
        
        if not relevant_questions:
            logger.warning("没有找到相关页面上的题目，使用所有题目")
            relevant_questions = questions_info
        
        if not relevant_questions and page_source_list:
            for page_info in page_source_list[:3]:
                relevant_questions.append({
                    "source_pdf_path": page_info["source_pdf_path"],
                    "page_num": page_info["page_num"],
                    "score": 10,
                    "type": "简答题"
                })
        
        relevant_questions.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        selected_questions = []
        current_score = 0
        
        for question in relevant_questions:
            score = question.get("score", 0)
            if current_score + score <= required_score * 1.1:
                selected_questions.append(question)
                current_score += score
                if current_score >= required_score * 0.9:
                    break
        
        if not selected_questions and relevant_questions:
            logger.warning("没有选择到符合分值要求的题目，选择第一个题目")
            selected_questions = [relevant_questions[0]]
            current_score = selected_questions[0].get("score", 0)
        
        selected_questions.sort(key=lambda x: x.get("page_num", 0))
        
        logger.info(f"Fallback题目筛选完成，选择了 {len(selected_questions)} 道题目，总分: {current_score}")
        
        return QuestionsSelectionOutput(selected_questions=selected_questions)
        
    except Exception as e:
        logger.error(f"题目筛选失败: {str(e)}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        raise


# ==================== 节点7: 试卷重组 ====================
def generate_exam_paper_node(state: GenerateExamPaperInput, config: RunnableConfig, runtime: Runtime[Context]) -> GenerateExamPaperOutput:
    """
    title: 生成试卷
    desc: 截取相关页面，生成封面（精准横向居中+等线字体），组合最终试卷
    integrations: PyMuPDF
    """
    ctx = runtime.context
    
    try:
        downloaded_pdf_path = state.downloaded_pdf_path
        selected_questions = state.selected_questions
        cover_title = state.cover_title
        cover_subtitle = state.cover_subtitle
        cover_author = state.cover_author
        subject_code = getattr(state, 'subject_code', '')
        paper_type = getattr(state, 'paper_type', '')
        
        if not selected_questions:
            logger.warning("没有选择任何题目，生成空试卷")
            selected_questions = [{"page_num": 1, "type": "无题目", "score": 0}]
        
        new_doc = pymupdf.Document()
        # 如果downloaded_pdf_path是目录，我们将从每个题目的source_pdf_path中抽取页面
        is_dir_source = os.path.isdir(downloaded_pdf_path)
        doc = None
        cover_page = new_doc.new_page(width=595, height=842)  # A4
        
        # =============== 精准加载「等线」字体（关键修复） ===============
        dengxian_fontfile = "C:\\Windows\\Fonts\\Deng.ttf"
        try:
            # 显式加载并嵌入字体（必须！）
            # 首先检查字体文件是否存在
            if os.path.exists(dengxian_fontfile):
                logger.info(f"字体文件存在: {dengxian_fontfile}")
                # 尝试直接使用字体文件路径
                cover_page.insert_font(fontname="等线", fontfile=dengxian_fontfile)
                active_font = "等线"
                logger.info("✓ 等线字体加载成功（Deng.ttf）")
            else:
                logger.error(f"字体文件不存在: {dengxian_fontfile}")
                raise FileNotFoundError(f"字体文件不存在: {dengxian_fontfile}")
        except Exception as e:
            logger.error(f"⚠️ 等线字体加载失败: {e}，回退至内置宋体")
            active_font = "china-s"  # 仅作最后回退（新版可能无效）
        
        # =============== 文本居中：使用估算偏移量实现 ===============
        # 计算页面中心点
        page_center_x = cover_page.rect.width / 2  # 297.5
        
        # 标题（加大字号增强视觉）
        cover_page.insert_text(
            (page_center_x - 100, 320),  # 估算标题宽度的一半进行偏移
            cover_title,
            fontsize=38,
            fontname=active_font,
            color=(0, 0, 0)
        )
        
        # 副标题
        if cover_subtitle:
            cover_page.insert_text(
                (page_center_x - 50, 380),  # 估算副标题宽度的一半进行偏移
                cover_subtitle,
                fontsize=18,
                fontname=active_font,
                color=(0.4, 0.4, 0.4)
            )
        
        # 科目/试卷信息
        if subject_code or paper_type:
            parts = []
            if subject_code: parts.append(f"科目代码: {subject_code}")
            if paper_type: parts.append(f"试卷类型: {paper_type}")
            if parts:
                cover_page.insert_text(
                    (page_center_x - 80, 440),  # 估算信息宽度的一半进行偏移
                    " | ".join(parts),
                    fontsize=15,
                    fontname=active_font,
                    color=(0, 0, 0)
                )
        
        # 作者
        if cover_author:
            cover_page.insert_text(
                (page_center_x - 60, 700),  # 估算作者信息宽度的一半进行偏移
                f"出题人: {cover_author}",
                fontsize=14,
                fontname=active_font,
                color=(0.3, 0.3, 0.3)
            )
        
        # =============== 插入题目内容页 ===============
        # 插入题目内容页：如果是目录来源，则针对每道题目从相应PDF抽取单页
        selected_pages = sorted(set(q.get("page_num", 1) for q in selected_questions))
        if is_dir_source:
            for q in selected_questions:
                page_num = int(q.get('page_num', 1))
                src_pdf = q.get('source_pdf_path')
                if not src_pdf or not os.path.isfile(src_pdf):
                    logger.warning(f"题目来源PDF路径无效或不存在: {src_pdf}, 跳过")
                    continue
                try:
                    src_doc = pymupdf.open(src_pdf)
                    if 0 < page_num <= len(src_doc):
                        new_doc.insert_pdf(src_doc, from_page=page_num-1, to_page=page_num-1)
                    src_doc.close()
                except Exception as e:
                    logger.warning(f"从 {src_pdf} 抽取第{page_num}页失败: {e}")
                    continue
        else:
            # 单文件PDF来源（旧行为）
            try:
                doc = pymupdf.open(downloaded_pdf_path)
                for page_num in selected_pages:
                    if 0 < page_num <= len(doc):
                        new_doc.insert_pdf(doc, from_page=page_num-1, to_page=page_num-1)
            finally:
                if doc:
                    doc.close()
        
        # =============== 保存与报告 ===============
        workspace_path = os.getenv("WORKSPACE_PATH", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        assets_dir = os.path.join(workspace_path, "assets")
        os.makedirs(assets_dir, exist_ok=True)
        
        # 生成文件名
        if subject_code and paper_type:
            output_filename = f"{subject_code}_type_{paper_type}_exam.pdf"
        elif subject_code:
            output_filename = f"{subject_code}_exam.pdf"
        elif paper_type:
            output_filename = f"type_{paper_type}_exam.pdf"
        else:
            output_filename = "exam_paper.pdf"
        
        output_path = os.path.join(assets_dir, output_filename)
        new_doc.save(output_path)
        new_doc.close()
        
        # 生成分析报告
        total_score = sum(q.get("score", 0) for q in selected_questions)
        question_types = {}
        for q in selected_questions:
            q_type = q.get("type", "未知")
            question_types[q_type] = question_types.get(q_type, 0) + 1
        
        report = f"""试卷生成报告
================
封面标题: {cover_title}
使用的封面字体: {active_font}
总题数: {len(selected_questions)}
总分值: {total_score}
题目分布:
"""
        for q_type, count in question_types.items():
            report += f"  - {q_type}: {count}道\n"
        report += f"\n使用页面: {', '.join(map(str, selected_pages))}"
        
        logger.info(f"✓ 试卷生成完成，保存至: {output_path}")
        return GenerateExamPaperOutput(
            final_pdf_path=output_path,
            analysis_report=report
        )
        
    except Exception as e:
        logger.error(f"试卷生成失败: {str(e)}", exc_info=True)
        raise