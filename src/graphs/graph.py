from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context

# 导入状态定义
from graphs.state import (
    GlobalState,
    GraphInput,
    GraphOutput
)

# 导入节点函数
from graphs.node import (
    download_pdf_node,
    ocr_recognition_node,
    questions_analysis_node,
    database_storage_node,
    rag_indexing_node,
    rag_retrieval_node,
    questions_selection_node,
    generate_exam_paper_node
)


# 创建状态图，指定输入输出schema
builder = StateGraph(GlobalState, input_schema=GraphInput, output_schema=GraphOutput)

# 添加节点
builder.add_node("download_pdf", download_pdf_node)
builder.add_node("ocr_recognition", ocr_recognition_node)
builder.add_node("questions_analysis", questions_analysis_node, metadata={"type": "agent", "llm_cfg": "config/questions_analysis_cfg.json"})
builder.add_node("database_storage", database_storage_node)
builder.add_node("rag_indexing", rag_indexing_node)
builder.add_node("rag_retrieval", rag_retrieval_node)
builder.add_node("questions_selection", questions_selection_node, metadata={"type": "agent", "llm_cfg": "config/questions_selection_cfg.json"})
builder.add_node("generate_exam_paper", generate_exam_paper_node)

# 设置入口点
builder.set_entry_point("download_pdf")

# 添加边（串行流程）
builder.add_edge("download_pdf", "ocr_recognition")
builder.add_edge("ocr_recognition", "questions_analysis")
builder.add_edge("questions_analysis", "database_storage")
builder.add_edge("database_storage", "rag_indexing")
builder.add_edge("rag_indexing", "rag_retrieval")
builder.add_edge("rag_retrieval", "questions_selection")
builder.add_edge("questions_selection", "generate_exam_paper")
builder.add_edge("generate_exam_paper", END)

# 编译图
main_graph = builder.compile()
