from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, Field
from utils.file.file import File


# ==================== 全局状态 ====================
class GlobalState(BaseModel):
    """全局状态定义"""
    # 输入参数
    pdf_url: str = Field(default="", description="目标试卷PDF的URL")
    knowledge_pdf_path: str = Field(default="", description="知识点PDF的本地路径")
    required_score: int = Field(default=100, description="要求的总分值")
    knowledge_range: str = Field(default="", description="要求的知识点范围")
    cover_title: str = Field(default="试卷", description="封面标题")
    cover_subtitle: str = Field(default="", description="封面副标题")
    cover_author: str = Field(default="", description="封面作者")
    
    # 试卷信息
    subject_code: str = Field(default="", description="科目代码")
    paper_type: str = Field(default="", description="试卷类型")
    
    # 中间状态
    downloaded_pdf_path: str = Field(default="", description="下载的PDF文件路径")
    ocr_json_path: str = Field(default="", description="OCR识别后的JSON文件路径")
    markdown_content: str = Field(default="", description="（兼容）OCR识别后的Markdown内容，通常由OCR JSON 生成用于提示词")
    questions_info: List[Dict[str, Any]] = Field(default=[], description="题目信息列表")
    knowledge_embeddings: List[List[float]] = Field(default=[], description="知识点向量")
    knowledge_texts: List[str] = Field(default=[], description="知识点文本列表")
    relevant_pages: List[int] = Field(default=[], description="RAG检索到的相关页面")
    selected_questions: List[Dict[str, Any]] = Field(default=[], description="筛选后的题目")
    
    # 输出
    final_pdf_path: str = Field(default="", description="最终试卷PDF路径")
    analysis_report: str = Field(default="", description="分析报告")


# ==================== 工作流输入输出 ====================
class GraphInput(BaseModel):
    """工作流输入"""
    pdf_url: str = Field(..., description="目标试卷PDF的URL")
    exam_code: str = Field(default="", description="考试代码，例如: 9618。若提供，则按规则一次性下载该考试的多个试卷")
    year: str = Field(default="", description="考试年/期，例如: s23")
    knowledge_pdf_path: str = Field(..., description="知识点PDF的本地路径")
    required_score: int = Field(default=100, description="要求的总分值")
    knowledge_range: str = Field(..., description="要求的知识点范围")
    cover_title: str = Field(default="试卷", description="封面标题")
    cover_subtitle: str = Field(default="", description="封面副标题")
    cover_author: str = Field(default="", description="封面作者")


class GraphOutput(BaseModel):
    """工作流输出"""
    final_pdf_path: str = Field(..., description="最终试卷PDF路径")
    analysis_report: str = Field(..., description="分析报告")


# ==================== 节点1: 下载PDF ====================
class DownloadPdfInput(BaseModel):
    """下载PDF节点输入"""
    pdf_url: str = Field(default="", description="目标试卷PDF的URL")
    exam_code: str = Field(default="", description="考试代码，可选")
    year: str = Field(default="", description="考试年/期，可选")


class DownloadPdfOutput(BaseModel):
    """下载PDF节点输出"""
    downloaded_pdf_path: str = Field(..., description="下载的PDF文件路径")
    subject_code: str = Field(default="", description="科目代码")
    paper_type: str = Field(default="", description="试卷类型")


# ==================== 节点2: OCR识别 ====================
class OcrRecognitionInput(BaseModel):
    """OCR识别节点输入"""
    downloaded_pdf_path: str = Field(..., description="下载的PDF文件路径")


class OcrRecognitionOutput(BaseModel):
    """OCR识别节点输出"""
    ocr_json_path: str = Field(..., description="OCR识别后的JSON文件路径")
    markdown_content: str = Field(default="", description="（兼容）用于LM的Markdown文本，从OCR JSON生成")


# ==================== 节点3: 题目分析 ====================
class QuestionsAnalysisInput(BaseModel):
    """题目分析节点输入"""
    ocr_json_path: str = Field(..., description="OCR识别后的JSON文件路径")
    markdown_content: str = Field(default="", description="（兼容）OCR识别后的Markdown内容，可选")


class QuestionsAnalysisOutput(BaseModel):
    """题目分析节点输出"""
    questions_info: List[Dict[str, Any]] = Field(..., description="题目信息列表，每项包含type, page_num, score")


# ==================== 节点4: 数据库存储 ====================
class DatabaseStorageInput(BaseModel):
    """数据库存储节点输入"""
    downloaded_pdf_path: str = Field(..., description="原始PDF文件路径")
    questions_info: List[Dict[str, Any]] = Field(..., description="题目信息列表")
    ocr_json_path: str = Field(..., description="OCR识别后的JSON文件路径")
    markdown_content: str = Field(default="", description="（兼容）OCR识别后的Markdown内容")


class DatabaseStorageOutput(BaseModel):
    """数据库存储节点输出"""
    stored_question_ids: List[int] = Field(..., description="存储的题目ID列表")


# ==================== 节点5: RAG索引 ====================
class RagIndexingInput(BaseModel):
    """RAG索引节点输入"""
    knowledge_pdf_path: str = Field(..., description="知识点PDF的本地路径")


class RagIndexingOutput(BaseModel):
    """RAG索引节点输出"""
    knowledge_embeddings: List[List[float]] = Field(..., description="知识点向量")
    knowledge_texts: List[str] = Field(..., description="知识点文本列表")


# ==================== 节点6: RAG检索 ====================
class RagRetrievalInput(BaseModel):
    """RAG检索节点输入"""
    knowledge_range: str = Field(..., description="要求的知识点范围")
    knowledge_embeddings: List[List[float]] = Field(..., description="知识点向量")
    knowledge_texts: List[str] = Field(..., description="知识点文本列表")


class RagRetrievalOutput(BaseModel):
    """RAG检索节点输出"""
    relevant_pages: List[int] = Field(..., description="相关的页面列表")


# ==================== 节点7: 题目筛选 ====================
class QuestionsSelectionInput(BaseModel):
    """题目筛选节点输入"""
    questions_info: List[Dict[str, Any]] = Field(..., description="题目信息列表")
    relevant_pages: List[int] = Field(..., description="相关的页面列表")
    required_score: int = Field(..., description="要求的总分值")
    knowledge_range: str = Field(default="", description="知识点范围")
    knowledge_texts: List[str] = Field(default=[], description="知识点文本列表")
    ocr_json_path: str = Field(default="", description="OCR JSON文件路径")


class QuestionsSelectionOutput(BaseModel):
    """题目筛选节点输出"""
    selected_questions: List[Dict[str, Any]] = Field(..., description="筛选后的题目")


# ==================== 节点8: 试卷重组 ====================
class GenerateExamPaperInput(BaseModel):
    """生成试卷节点输入"""
    downloaded_pdf_path: str = Field(..., description="原始PDF文件路径")
    selected_questions: List[Dict[str, Any]] = Field(..., description="筛选后的题目")
    cover_title: str = Field(..., description="封面标题")
    cover_subtitle: str = Field(..., description="封面副标题")
    cover_author: str = Field(..., description="封面作者")
    subject_code: str = Field(default="", description="科目代码")
    paper_type: str = Field(default="", description="试卷类型")


class GenerateExamPaperOutput(BaseModel):
    """生成试卷节点输出"""
    final_pdf_path: str = Field(..., description="最终试卷PDF路径")
    analysis_report: str = Field(..., description="分析报告")
