import os
import sys
import logging
from pathlib import Path

# 添加项目根目录和src目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from storage.database.db import get_engine
from storage.database.shared.model import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    """
    初始化数据库，创建所有表
    """
    try:
        engine = get_engine()
        
        logger.info("开始初始化数据库...")
        
        # 先删除所有表
        logger.info("删除现有表...")
        Base.metadata.drop_all(bind=engine)
        
        # 创建所有表
        logger.info("创建数据库表...")
        Base.metadata.create_all(bind=engine)
        
        logger.info("数据库表创建成功！")
        logger.info("已创建以下表：")
        logger.info("  - questions (题目表)")
        logger.info("  - exam_papers (试卷表)")
        logger.info("  - exam_paper_questions (试卷题目关联表)")
        
        return True
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        return False


def drop_database():
    """
    删除所有表（谨慎使用）
    """
    try:
        engine = get_engine()
        
        logger.warning("警告：即将删除所有数据库表！")
        confirm = input("确认删除？(yes/no): ")
        
        if confirm.lower() == 'yes':
            Base.metadata.drop_all(bind=engine)
            logger.info("数据库表已删除")
        else:
            logger.info("操作已取消")
            
        return True
        
    except Exception as e:
        logger.error(f"删除数据库表失败: {str(e)}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="数据库管理工具")
    parser.add_argument("--init", action="store_true", help="初始化数据库")
    parser.add_argument("--drop", action="store_true", help="删除所有表")
    
    args = parser.parse_args()
    
    if args.init:
        init_database()
    elif args.drop:
        drop_database()
    else:
        parser.print_help()