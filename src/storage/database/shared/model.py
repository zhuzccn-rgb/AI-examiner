from sqlalchemy import BigInteger, DateTime, Identity, Index, Integer, JSON, PrimaryKeyConstraint, Text, text, String, Float
from typing import Optional
import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass


class Question(Base):
    __tablename__ = "questions"
    
    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1), primary_key=True)
    question_type: Mapped[str] = mapped_column(String(50), nullable=False, comment="题目类型")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="题目内容")
    score: Mapped[float] = mapped_column(Float, nullable=False, comment="分值")
    knowledge_points: Mapped[Optional[str]] = mapped_column(Text, comment="知识点，多个用逗号分隔")
    source_pdf_path: Mapped[str] = mapped_column(String(500), nullable=False, comment="来源PDF文件路径")
    page_num: Mapped[int] = mapped_column(Integer, nullable=False, comment="来源页码")
    difficulty: Mapped[Optional[str]] = mapped_column(String(20), comment="难度等级")
    tags: Mapped[Optional[JSON]] = mapped_column(JSON, comment="标签，JSON格式")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, comment="创建时间")
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, comment="更新时间")
    
    __table_args__ = (
        Index("idx_question_type", "question_type"),
        Index("idx_knowledge_points", "knowledge_points"),
        Index("idx_source_pdf", "source_pdf_path"),
        Index("idx_question_created_at", "created_at"),
    )


class ExamPaper(Base):
    __tablename__ = "exam_papers"
    
    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="试卷标题")
    subtitle: Mapped[Optional[str]] = mapped_column(String(200), comment="试卷副标题")
    author: Mapped[Optional[str]] = mapped_column(String(100), comment="出题人")
    total_score: Mapped[float] = mapped_column(Float, nullable=False, comment="总分")
    question_count: Mapped[int] = mapped_column(Integer, nullable=False, comment="题目数量")
    knowledge_range: Mapped[Optional[str]] = mapped_column(Text, comment="知识点范围")
    pdf_path: Mapped[str] = mapped_column(String(500), nullable=False, comment="生成的PDF文件路径")
    analysis_report: Mapped[Optional[Text]] = mapped_column(Text, comment="分析报告")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, comment="创建时间")
    
    __table_args__ = (
        Index("idx_title", "title"),
        Index("idx_created_at", "created_at"),
    )


class ExamPaperQuestion(Base):
    __tablename__ = "exam_paper_questions"
    
    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1), primary_key=True)
    exam_paper_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="试卷ID")
    question_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="题目ID")
    order_num: Mapped[int] = mapped_column(Integer, nullable=False, comment="题目顺序")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, comment="创建时间")
    
    __table_args__ = (
        Index("idx_exam_paper_id", "exam_paper_id"),
        Index("idx_question_id", "question_id"),
    )