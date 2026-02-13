import hashlib
import re
import sys
import os
from typing import List, Dict, Tuple
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage.database.db import get_session
from storage.database.shared.model import Question, ExamPaperQuestion

logger = logging.getLogger(__name__)

def normalize_content(content: str) -> str:
    """标准化题目内容，用于比较"""
    if not content:
        return ""
    
    # 去除空白字符
    content = re.sub(r'\s+', ' ', content.strip())
    # 去除标点符号
    content = re.sub(r'[\s\.,;:"\'\(\)\[\]\{\}\!\?]+', ' ', content)
    # 转为小写
    content = content.lower()
    # 去除多余空格
    content = re.sub(r'\s+', ' ', content).strip()
    
    return content

def get_content_hash(content: str) -> str:
    """计算内容的哈希值"""
    normalized = normalize_content(content)
    return hashlib.md5(normalized.encode('utf-8')).hexdigest()

def find_duplicate_questions() -> Dict[str, List[Question]]:
    """找出数据库中的重复题目"""
    session = get_session()
    duplicates = {}
    
    try:
        # 获取所有题目
        questions = session.query(Question).all()
        logger.info(f"共获取到 {len(questions)} 道题目")
        
        # 按内容哈希分组
        content_groups = {}
        for question in questions:
            content_hash = get_content_hash(question.content)
            if content_hash not in content_groups:
                content_groups[content_hash] = []
            content_groups[content_hash].append(question)
        
        # 找出有重复的组
        for content_hash, group in content_groups.items():
            if len(group) > 1:
                duplicates[content_hash] = group
        
        logger.info(f"找到 {len(duplicates)} 组重复题目")
        
        return duplicates
        
    except Exception as e:
        logger.error(f"查找重复题目失败: {str(e)}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return {}
    finally:
        session.close()

def merge_questions(duplicate_groups: Dict[str, List[Question]]) -> Dict[str, Tuple[Question, List[Question]]]:
    """合并重复题目"""
    merged_results = {}
    session = get_session()
    
    try:
        for content_hash, questions in duplicate_groups.items():
            # 选择保留的题目（最新的）
            questions.sort(key=lambda x: x.created_at, reverse=True)
            keep_question = questions[0]
            merge_questions = questions[1:]
            
            logger.info(f"开始合并题目组，保留题目ID: {keep_question.id}，合并 {len(merge_questions)} 道题目")
            
            # 更新引用这些题目的ExamPaperQuestion记录
            for q in merge_questions:
                # 查找引用该题目的试卷题目关联
                exam_question_links = session.query(ExamPaperQuestion).filter(
                    ExamPaperQuestion.question_id == q.id
                ).all()
                
                # 更新关联到保留的题目
                for link in exam_question_links:
                    link.question_id = keep_question.id
                    logger.debug(f"更新试卷题目关联: 试卷ID={link.exam_paper_id}, 题目ID={q.id} -> {keep_question.id}")
                
                # 删除被合并的题目
                session.delete(q)
                logger.debug(f"删除被合并的题目: ID={q.id}")
            
            # 提交事务
            session.commit()
            merged_results[content_hash] = (keep_question, merge_questions)
            logger.info(f"完成合并，保留题目ID: {keep_question.id}，合并了 {len(merge_questions)} 道题目")
        
        return merged_results
        
    except Exception as e:
        session.rollback()
        logger.error(f"合并题目失败: {str(e)}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return {}
    finally:
        session.close()

def run_question_merger() -> Dict[str, Tuple[Question, List[Question]]]:
    """运行题目合并流程"""
    logger.info("开始执行题目合并流程")
    
    # 查找重复题目
    duplicates = find_duplicate_questions()
    
    if not duplicates:
        logger.info("没有找到重复题目，合并流程结束")
        return {}
    
    # 合并重复题目
    merged = merge_questions(duplicates)
    
    # 统计结果
    total_merged = sum(len(questions) for _, questions in merged.values())
    logger.info(f"题目合并流程完成，共合并了 {total_merged} 道题目")
    
    return merged

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 运行合并
    result = run_question_merger()
    
    # 打印结果
    for content_hash, (keep_question, merge_questions) in result.items():
        print(f"\n合并组: {content_hash}")
        print(f"保留题目: ID={keep_question.id}, 类型={keep_question.question_type}, 创建时间={keep_question.created_at}")
        print(f"合并题目数量: {len(merge_questions)}")
        for q in merge_questions:
            print(f"  - ID={q.id}, 类型={q.question_type}, 创建时间={q.created_at}")
